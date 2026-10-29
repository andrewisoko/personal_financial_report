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
                               calendar.month_name[12]:37, #2025
                               }
        
        count_rows_per_month = []
        count_months = 1
        exp_row_index = 0
        
        df_dict = self.df_converter(dates_dataframe)
        months_df =  df_dict["month"]
        months_df = [month for month in months_df if month != '12']
        
        
        while count_months < 13:
            month_format = lambda conto : F"0{conto}" if count_months <= 9 else str(conto)
            count_rows_per_month.append(months_df.count(month_format(count_months)))
            count_months += 1
        
        count_rows_per_month = [row_count for row_count in count_rows_per_month if row_count != 0]
      
        for key,val in EXPECTED_ROWS_COUNT.items():
            if val == count_rows_per_month[exp_row_index]:
                exp_row_index += 1
            
        if exp_row_index == len(list(EXPECTED_ROWS_COUNT)) - 1:   
            return "all dates rows validated"
        else:
            print(exp_row_index)  
            return False
        
        
validation = ValidateHistory() 
dates = Date()

excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

date_validation = validation.date_dim_validate(dates.history_dates(barclays_file_path,monzo_file_path,wise_file_path))
print(date_validation) 
