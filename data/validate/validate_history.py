import pandas as pd
from personal_financial_report.data.transform.date_dim import Date
from pathlib import Path

class ValidateHistory:
    
    def __init__(self):
        pass
    
    def date_dim_validate(self,dates_dataframe):
        
        # tot dates for each month with all banks combined
        
       return dates_dataframe[["date"]]
        
        
validation = ValidateHistory() 
dates = Date()

excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

date_validation = validation.date_dim_validate(dates.history_dates(barclays_file_path,monzo_file_path,wise_file_path))
 
print(date_validation) 
