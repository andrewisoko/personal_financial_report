import pandas as pd
from pathlib import Path
from collections import defaultdict



class Date:
    
    def __init__(self):
        pass
    
    def date_dim(self,file_path,sheet_name):
        
        
        date_dict = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()
        
        id = [ str(val)[0:4] + str(val)[5:7] + str(val)[8:10] for key,val in date_dict["Date"].items()]
        dates = [ val for key,val in date_dict["Date"].items()]
        year = [ str(val)[0:4] for key,val in date_dict["Date"].items()]
        month = [ str(val)[5:7] for key,val in date_dict["Date"].items()]
        day = [ str(val)[8:10] for key,val in date_dict["Date"].items()]
        
        date_series = pd.Series(dates)
        datetimes = pd.to_datetime(date_series)
    
        quarter = [str(qrt) for qrt in datetimes.dt.quarter.to_list()]
        weekday = [str(wkd) for wkd in datetimes.dt.day_of_week.to_list()]
           
        
        data = {
            "id": id,
            "date":dates,
            "year":year,
            "month":month,
            "day":day,
            "quarter":quarter,
            "day_of_week":weekday
        }
        return data
    
    def history_dates(self,bcl_file_path,monzo_file_path,wise_file_path):
        
        #-----------------------------------------------------------------------------------------#  
        #---------------------------------BARCLAYS------------------------------------------------# 
        #-----------------------------------------------------------------------------------------#
         
        bcl_sheet_names = [bcl_sheet_month for bcl_sheet_month in pd.ExcelFile(bcl_file_path).sheet_names if bcl_sheet_month != "All Transactions"]
        bcl2_xlsx_container = [self.date_dim(bcl_file_path,bcl_sheet_month) for bcl_sheet_month in bcl_sheet_names]

      
        bcl_grouped = defaultdict(list)
        
        for bcl_sheet_month in bcl2_xlsx_container:
            for key, value in bcl_sheet_month.items():
                bcl_grouped[key].extend(value)

        bcl_xlsx_df = pd.DataFrame(dict(bcl_grouped))
       
        
        #----------------------------------------------------------------------------------------#               
        #-----------------------------------MONZO------------------------------------------------#  
        #----------------------------------------------------------------------------------------# 
        
        monzo_sheet_names = [monzo_sheet_month for monzo_sheet_month in pd.ExcelFile(monzo_file_path).sheet_names]
        monzo_xlsx_container = [self.date_dim(monzo_file_path,monzo_sheet_month) for monzo_sheet_month in monzo_sheet_names] 
        
            
        monzo_grouped = defaultdict(list)
        
        for monzo_sheet_month in monzo_xlsx_container:
            for key,value in monzo_sheet_month.items():
                monzo_grouped[key].extend(value)

  
        monzo_xlsx_df = pd.DataFrame(dict(monzo_grouped))
    
          
        #-------------------------------------------------------------------------------------#
        #---------------------------------WISE------------------------------------------------#
        #-------------------------------------------------------------------------------------#    
       
        wise_sheet_names = [wise_sheet_month for wise_sheet_month in pd.ExcelFile(wise_file_path).sheet_names]
        wise_xlsx_container = [self.date_dim(wise_file_path,wise_sheet_month) for wise_sheet_month in wise_sheet_names] 
        
        wise_grouped = defaultdict(list)
        
        for wise_sheet_month in wise_xlsx_container:
            for key,value in wise_sheet_month.items():
                wise_grouped[key].extend(value)
        
        wise_xlsx_df = pd.DataFrame(dict(wise_grouped))
       
        all_frames = [bcl_xlsx_df,monzo_xlsx_df,wise_xlsx_df]
        
        return pd.concat(all_frames).drop_duplicates()
    
    
        
    def current_month_dates(self,blc_file_path,monzo_file_path,wise_file_path):
        
        #--------------------barclays-----------------------------#
          
        blc_doc = pd.ExcelFile(blc_file_path)
        bcl_sheet_name = blc_doc.sheet_names[-2]

        bcl_xlsx_df = pd.DataFrame(self.date_dim(blc_file_path,bcl_sheet_name))
        
        #--------------------monzo-----------------------------#
        
        monzo_doc = pd.ExcelFile(monzo_file_path)
        monzo_sheet_name = monzo_doc.sheet_names[-1]
        
        monzo_xlsx_df = pd.DataFrame(self.date_dim(monzo_file_path,monzo_sheet_name))
        
        #-----------------------wise-----------------------------#
        
        wise_doc = pd.ExcelFile(wise_file_path)
        wise_sheet_name = wise_doc.sheet_names[-1]
        
        wise_xlsx_df = pd.DataFrame(self.date_dim(wise_file_path,wise_sheet_name))
        
        all_frames = [bcl_xlsx_df,monzo_xlsx_df,wise_xlsx_df]
        
        
        return pd.concat(all_frames).drop_duplicates()
    
  