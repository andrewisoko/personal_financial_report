import pandas as pd
from pathlib import Path
import os
from data.transform.date_dim import Date
from data.transform.category_dim import Category
from data.transform.transaction_facts import Transaction
from data.validate.validate_current_month import Validate_Current_Month
from sqlalchemy import create_engine,inspect
from dotenv import load_dotenv


def cm_df_to_sql():
    
    load_dotenv()
    
    
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    
    # Format: postgresql+psycopg2://username:password@host:port/database_name
    engine = create_engine(
      f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    )
    inspector = inspect(engine)
    
    excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

    barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
    monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
    wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"
    
    validate_data = Validate_Current_Month()
    date = Date()
    transaction = Transaction()
    
    current_month_dates = date.current_month_dates(barclays_file_path,monzo_file_path,wise_file_path)
    current_month_transactions = transaction.current_month_transactions(barclays_file_path,monzo_file_path,wise_file_path)
    
   
    
    if validate_data.date_dim_validate(current_month_dates) == True and inspector.has_table("date_dim","public"):
        
        first_id = pd.read_sql("SELECT id FROM public.date_dim LIMIT 1", con=engine).iloc[0, 0]
        if not current_month_dates.iloc[0, 0] == first_id:

            current_month_dates.to_sql(
            name='date_dim',
            con=engine,
            if_exists='append',
            index=False
        )
   
        
    if validate_data.transaction_facts_validate(current_month_transactions) == True and inspector.has_table("transaction_facts","public"):
        
        first_date_id = pd.read_sql("SELECT * FROM public.transaction_facts ORDER BY date_id LIMIT 1;", con=engine).iloc[0,9] 
        if not current_month_transactions.iloc[0, 9] == first_date_id:
            current_month_transactions.to_sql(
            name='transaction_facts',
            con=engine,
            if_exists='append',
            index=False
        )
   
    
    print("all dataframes [CURRENT MONTH] moved into Postgres 🚀")
   

if __name__ == "__main__":
    cm_df_to_sql()