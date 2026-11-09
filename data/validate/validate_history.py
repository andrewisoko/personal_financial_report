import pandas as pd
from personal_financial_report.data.transform.date_dim import Date
from personal_financial_report.data.transform.transaction_facts import Transaction
from personal_financial_report.blc_balances import BCL_BALANCES
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
        
        df_dict = self.df_converter(tr_dataframe)
        
        
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
        
        for key,val in EXPECTED_ROWS_COUNT.items():
                if val == count_rows_per_month[exp_row_index]:
                    exp_row_index += 1     
            
        assert list(EXPECTED_ROWS_COUNT.values()) == count_rows_per_month
        
        
    # 2.  expected end balance for each month 
        
        
        month_end_balances = []       
        transactions_updates = [BCL_BALANCES["start_balance"]]
        month_periods:list = df_dict["month_payment_period"] 
        amounts:list = df_dict["amount"]
        money_in:list = df_dict["money_in"]
        category:list = df_dict["category_id"]
        
        data_transactions = {month:[] for month in list(dict.fromkeys(month_periods))}
        
        for index, month in enumerate(month_periods):
            if "bcl" in category[index]:
                data_transactions[month].append({money_in[index]:amounts[index]})
        
        data_transactions.pop("December 2025")  
        print(data_transactions["January"])
        
        for month_name, data in data_transactions.items():
            for obj in data:
                    try:
                        transactions_updates.append(transactions_updates[-1] + obj[True])
                        
                    except KeyError:
                        transactions_updates.append(transactions_updates[-1] - obj[False])
                
                
            month_end_balances.append((month_name,transactions_updates[-1]))
        # print(*month_end_balances,sep="\n")
            
        
validation = ValidateHistory() 
dates = Date()
transactions = Transaction()

excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

date_validation = validation.transaction_facts_validate(transactions.history_transactions(barclays_file_path,monzo_file_path,wise_file_path))
print(date_validation) 
