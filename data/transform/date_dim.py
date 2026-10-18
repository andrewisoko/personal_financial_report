import pandas as pd
from pathlib import Path
from collections import defaultdict



class Date:
    
    def date_dim(self,file_path,sheet_name):
        
    
        date_dict = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()
        
        id = [ str(val)[0:3] + str(val)[5:7] + str(val)[8:10] for key,val in date_dict["Date"].items()]
        dates = [ str(val) for key,val in date_dict["Date"].items()]
        year = [ str(val)[5:7] for key,val in date_dict["Date"].items()]
        day = [ str(val)[8:10] for key,val in date_dict["Date"].items()]
        
        date_series = pd.Series(dates)
        datetimes = pd.to_datetime(date_series)
    
        quarter = datetimes.dt.quarter.to_list()
        weekday = datetimes.dt.weekday.to_list()
           
        
        data = {
            "id": id,
            "date":dates,
            "year":year,
            "day":day,
            "quarter":quarter,
            "day_of_week_name":weekday
        }
        
        return data
    
    def history_dates(self,blc_file_path,monzo_file_path,wise_file_path):
        
        #--------------------barclays-----------------------------#
         
        blc2_xlsx_container = []
        
        from_num = 1
        to_num = 2
        blc1_xlsx_df = pd.DataFrame(self.date_dim(blc_file_path,"2025-12 to 2026-01")) # bcl 2025 sheet

        while to_num <= 9:
            
            monzo_sheet_month = self.date_dim(blc_file_path,f"2026-0{from_num} to 2026-0{to_num}")
            blc2_xlsx_container.append(monzo_sheet_month)
            
            from_num += 1
            to_num += 1
            
        blc_grouped = defaultdict(list)
        
        for blc_sheet_month in blc2_xlsx_container:
            for key, value in blc_sheet_month.items():
                blc_grouped[key].extend(value)

        blc2_xlsx_df = pd.DataFrame(dict(blc_grouped))
       
        # print(pd.concat([blc1_xlsx_df,blc2_xlsx_df]))
        
        
        #--------------------monzo-----------------------------#
        
        monzo_xlsx_container = []
        months_dict = {0:"Jan",1:"Feb",2:"Mar",3:"Apr",4:"May",5:"Jun",6:"Jul",7:"Aug",8:"Sep"}
        
        monzo1_xlsx_df = pd.DataFrame(self.date_dim(monzo_file_path, "Dec 2025 (28-31)")) #2025 sheet
        
        
        for month_index in range(0,8):
            if month_index == 1:
                monzo_xlsx_container.append(self.date_dim(monzo_file_path,"Feb 2026 (01-28)"))
            elif month_index == 3:
                monzo_xlsx_container.append(self.date_dim(monzo_file_path,"Apr 2026 (01-30)"))
            elif month_index == 5:
                monzo_xlsx_container.append(self.date_dim(monzo_file_path,"Jun 2026 (01-30)"))
            elif month_index == 8:
                monzo_xlsx_container.append(self.date_dim(monzo_file_path,"Sep 2026 (01-30)"))
            else:
                monzo_xlsx_container.append(self.date_dim(monzo_file_path,f"{months_dict[month_index]} 2026 (01-31)"))
                
            month_index += 1
            
        monzo_grouped = defaultdict(list)
        
        for monzo_sheet_month in monzo_xlsx_container:
            for key,value in monzo_sheet_month.items():
                monzo_grouped[key].extend(value)

        monzo2_xlsx_df = pd.DataFrame(dict(monzo_grouped))
    
          
        #--------------------wise-----------------------------#   
       
        wise_may_2026 = self.date_dim(wise_file_path, "2026-05 May")
        wise_jul_2026 = self.date_dim(wise_file_path, "2026-07 Jul")
        wise_aug_2026 = self.date_dim(wise_file_path, "2026-08 Aug")
        wise_sep_2026 = self.date_dim(wise_file_path, "2026-09 Sep")
        
        wise_xlsx_container = [wise_may_2026,wise_jul_2026,wise_aug_2026,wise_sep_2026]
        wise_grouped = defaultdict(list)
        
        for wise_sheet_month in wise_xlsx_container:
            for key,value in wise_sheet_month.items():
                wise_grouped[key].extend(value)
        
        wise_xlsx_df = pd.DataFrame(dict(wise_grouped))
       
        all_frames = [blc1_xlsx_df,blc2_xlsx_df,monzo1_xlsx_df,monzo2_xlsx_df,wise_xlsx_df]
        
        return pd.concat(all_frames)
        
    def latest_dates(self,blc_file_path,monzo_file_path,wise_file_path):
        
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
        
        return pd.concat(all_frames)
       
                
date = Date()
excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

print(date.history_dates(barclays_file_path,monzo_file_path,wise_file_path))