from data.transform.date_dim import Date
from data.transform.category_dim import Category
from pathlib import Path
import calendar
from datetime import datetime
from blc_balances import BCL_CM_BALANCE

class Validate_Current_Month:
    
    def __init__(self):
        pass
    
    def date_dim_validate(self,dates_dataframe):
        
        df_dict = self.df_converter(dates_dataframe)
        all_values = [val for array in df_dict.values() for val in array]
        
        # 1.  None values checks
            
                
        assert all(val != None for val in all_values)
            
        # 2. Id check
        
        matches = 0
        ids_formatted = [id_date[0:4] + "-" + id_date[4:6] + "-" + id_date[6:8]  for id_date in df_dict["id"]]
        dates_notime = [str(date)[0:10] for date in df_dict["date"]]
        
        for id_in_date in ids_formatted:
            if id_in_date == dates_notime[matches]:
                matches += 1
    
        
        assert matches == len(df_dict["id"])  and matches == len(df_dict["date"]) 
        
        
        # 3. types check
        
        
        assert all( isinstance( item, str) for item in df_dict["id"])
        assert all( isinstance( item, datetime) for item in df_dict["date"])
        assert all( isinstance( item, str) for item in df_dict["year"])
        assert all( isinstance( item, str) for item in df_dict["month"])
        assert all( isinstance( item, str) for item in df_dict["day"])
        assert all( isinstance( item, str) for item in df_dict["quarter"])
        assert all( isinstance( item, str) for item in df_dict["day_of_week"])
        
    
        
        return True
    
    def transaction_facts_validate(self,tr_dataframe):
        
        excel_dir = Path(__file__).parent.parent / "extract"/ "excel"
        barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
        monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
        wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"
        
        all_categories = self.df_converter(Category().category_df())
        all_dates = self.df_converter(Date().current_month_dates(barclays_file_path,monzo_file_path,wise_file_path))
        
        df_dict = self.df_converter(tr_dataframe)
        
        transaction_id :list[str] = df_dict["id"] 
        bank :list[str] = df_dict["bank"] 
        amounts:list[float] = df_dict["amount"]
        converted_to_gbp:list[bool] = df_dict["converted_to_gbp"]
        currency :list[str] = df_dict["currency"] 
        money_in:list[bool] = df_dict["money_in"]
        money_out:list[bool] = df_dict["money_out"]
        month_periods:list[str] = df_dict["month_payment_period"] 
        category:list[str] = df_dict["category_id"]
        date_id:list[str] = df_dict["date_id"]
        
    
    # 1. tot row count per month periods with all banks included    
        
    # 2.  expected end balance for each month 
           
    # 3. money In money out validation
        
        for index,id in enumerate(transaction_id):
            assert money_in[index] == True if money_out[index] == False else money_out[index] == True and money_in[index] == False
            
    # 4. data types of list items
    
            assert isinstance(id,str)
            assert isinstance(bank[index],str)
            assert isinstance(amounts[index],float)
            assert isinstance(converted_to_gbp[index],bool)
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
        
    # 8. conversions
        
        assert converted_to_gbp[index] == True if currency[index] != "GBP" else converted_to_gbp[index] == False
        
    # 9. money transfered to different bank accounts
    
        assert transaction_id.count("bcl_cat_monzotransferout19") == transaction_id.count("monzo_cat_transferin29")
        assert transaction_id.count("bcl_cat_wisetransferout20") == transaction_id.count("wise_transferin34")


        return True
        
    