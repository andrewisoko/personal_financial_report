import pandas as pd
from personal_financial_report.data.transform.date_dim import Date
from pathlib import Path
import calendar

class ValidateHistory:
    
    def __init__(self):
        pass
    
    def df_converter(self,dataframe):
        return dataframe.to_dict(orient='list')
    
    
    def date_dim_validate(self,dates_dataframe):
        
        # tot dates rows for each month with all banks combined, rows including start and end date from barclays
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
            
        return (
            "all dates rows validated"
            if list(EXPECTED_ROWS_COUNT.values()) == count_rows_per_month
            else False
        )
        
        
validation = ValidateHistory() 
dates = Date()

excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

date_validation = validation.date_dim_validate(dates.history_dates(barclays_file_path,monzo_file_path,wise_file_path))
print(date_validation) 
