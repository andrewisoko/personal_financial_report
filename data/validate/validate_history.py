from personal_financial_report.data.transform.date_dim import Date
from personal_financial_report.data.transform.category_dim import Category
from personal_financial_report.data.transform.transaction_facts import Transaction
from personal_financial_report.blc_balances import BCL_BALANCES_2026
from pathlib import Path
import calendar

class ValidateHistory:
    
    def __init__(self):
        pass
    
    def df_converter(self,dataframe):
        return dataframe.to_dict(orient='list')
    
    
    def date_dim_validate(self,dates_dataframe):
        
        df_dict = self.df_converter(dates_dataframe)
        all_values = [val for array in df_dict.values() for val in array]
        
        # 1. tot dates rows for each month with all banks combined, rows including start and end date from barclays
        
        
        EXPECTED_ROWS_COUNT= { 
                               calendar.month_name[1]:79,
                               calendar.month_name[2]:50,
                               calendar.month_name[3]:85,
                               calendar.month_name[4]:68,
                               calendar.month_name[5]:232,
                               calendar.month_name[6]:85,
                               calendar.month_name[7]:167,
                               calendar.month_name[8]:121,
                               calendar.month_name[9]:118
                               }
        
       
        exp_row_index = 0
        
        df_dict = self.df_converter(dates_dataframe)
        months_df = [month for month in self.df_converter(dates_dataframe)["month"] if month != "12"]
        
        count_rows_per_month = [months_df.count(f"{month:02}") for month in range(1,13) if months_df.count(f"{month:02}") != 0]
    
        for key,val in EXPECTED_ROWS_COUNT.items():
            if val == count_rows_per_month[exp_row_index]:
                exp_row_index += 1
            
        
        assert list(EXPECTED_ROWS_COUNT.values()) == count_rows_per_month
        
        # 2.  None values checks
        
            
        assert all(val != None for val in all_values)
            
        # 3. Id check
        
        matches = 0
        ids_formatted = [id_date[0:4] + "-" + id_date[4:6] + "-" + id_date[6:8]  for id_date in df_dict["id"]]
        dates_notime = [date[0:10] for date in df_dict["date"]]
        
        for id_in_date in ids_formatted:
            if id_in_date == dates_notime[matches]:
                matches += 1
    
        
        assert matches == len(df_dict["id"])  and matches == len(df_dict["date"]) 
        
        
        # 4. types check
     
        assert all( isinstance( item, str) for item in all_values)
        
        return True
     
    def transaction_facts_validate(self,tr_dataframe):
        
        excel_dir = Path(__file__).parent.parent / "extract"/ "excel"
        barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
        monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
        wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"
        
        all_categories = self.df_converter(Category().all_categories_table())
        all_dates = self.df_converter(Date().history_dates(barclays_file_path,monzo_file_path,wise_file_path))
        
        df_dict = self.df_converter(tr_dataframe)
        
        transaction_id :list[str] = df_dict["id"] 
        bank :list[str] = df_dict["bank"] 
        amounts:list[float] = df_dict["amount"]
        currency :list[str] = df_dict["currency"] 
        money_in:list[bool] = df_dict["money_in"]
        money_out:list[bool] = df_dict["money_out"]
        month_periods:list[str] = df_dict["month_payment_period"] 
        category:list[str] = df_dict["category_id"]
        date_id:list[str] = df_dict["date_id"]
        
    
        
        
    # 1. tot month periods with all banks included
     
        EXPECTED_ROWS_COUNT= { 
            calendar.month_name[1]:64,
            calendar.month_name[2]:59,
            calendar.month_name[3]:72,
            calendar.month_name[4]:80,
            calendar.month_name[5]:170,
            calendar.month_name[6]:86,
            calendar.month_name[7]:143,
            calendar.month_name[8]:112,
            calendar.month_name[9]:60
        }
        
        exp_row_index = 0
        months_period = [month for month in df_dict["month_payment_period"]]
        count_rows_per_month = [months_period.count(calendar.month_name[month]) for month in range(1,13) if calendar.month_name[month] in months_period]
        
        for key,id in EXPECTED_ROWS_COUNT.items():
                if id == count_rows_per_month[exp_row_index]:
                    exp_row_index += 1     
            
        assert list(EXPECTED_ROWS_COUNT.values()) == count_rows_per_month
        
        
    # 2.  expected end balance for each month 
        
        expected_balances_per_month = [BCL_BALANCES_2026["end_balances"][calendar.month_name[month_num]] 
                                      for month_num in range(1,13) 
                                      if calendar.month_name[month_num] in BCL_BALANCES_2026["end_balances"]] 
        
        month_end_balances = []       
        transactions_updates = [BCL_BALANCES_2026["start_balance"]]
       
        
        data_transactions = {month:[] for month in list(dict.fromkeys(month_periods))}
        
        for index, month in enumerate(month_periods):
            if "bcl" in category[index]:
                data_transactions[month].append({money_in[index]:amounts[index]})
        
        data_transactions.pop("December 2025")  
        
        for month_name, data in data_transactions.items():
            for obj in data:
                    try:
                        transactions_updates.append(transactions_updates[-1] + obj[True])
                        
                    except KeyError:
                        transactions_updates.append(transactions_updates[-1] - obj[False])
            month_end_balances.append(float(f"{transactions_updates[-1]:.2f}"))
               
         
        assert month_end_balances == expected_balances_per_month
        
    # 3. money In money out validation
       
        for index,id in enumerate(transaction_id):
            assert money_in[index] == True if money_out[index] == False else money_out[index] == True and money_in[index] == False
            
    # 4. data types of list items
    
            assert isinstance(id,str)
            assert isinstance(bank[index],str)
            assert isinstance(amounts[index],float)
            assert isinstance(currency[index],str)
            assert isinstance(money_in[index],bool)
            assert isinstance(money_out[index],bool)
            assert isinstance(month_periods[index],str)
            assert isinstance(category[index],str)
            assert isinstance(date_id[index],str)
        
    # 5. foreign keys
    
        assert category[index] in all_categories["id"]
        assert date_id[index] in all_dates["id"]
    
    # 6. bank prefix
    
        assert id[0:3] in bank[index] if bank[index] != "barclays" else transaction_id[index][0:3] == "bcl"
    
    # 7. amounts
    
        assert amounts[index] > 0 
        
    # 8. money transfered to different bank accounts
    
        assert transaction_id.count("bcl_cat_monzotransferout19") == transaction_id.count("monzo_cat_transferin29")
        assert transaction_id.count("bcl_cat_wisetransferout20") == transaction_id.count("wise_transferin34")


        return True
        
validation = ValidateHistory() 
dates = Date()
transactions = Transaction()

excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

date_validation = validation.transaction_facts_validate(transactions.history_transactions(barclays_file_path,monzo_file_path,wise_file_path))
print(date_validation) 
