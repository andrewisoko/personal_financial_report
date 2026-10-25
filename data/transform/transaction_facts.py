import pandas as pd
import uuid
from pathlib import Path
import math
import calendar
from collections import defaultdict
from personal_financial_report.non_confidential_keywords import KEYWORD_TO_CATEGORY



class Transaction:
    
    def transaction_facts(self,file_path,sheet_name):
        
        EXCEL_DIR = Path(__file__).parent.parent / "extract"/ "excel"
        BCL_FILE_PATH = EXCEL_DIR / "barclays_excel" / "barclays_statements.xlsx"
        STARTING_BALANCE_2026 = pd.read_excel(BCL_FILE_PATH,"2025-12 to 2026-01",usecols=["Balance"]).to_dict()['Balance'][21]
        
        bank_ref = "barclays" if "barclays" in str(file_path) else "monzo" if "monzo" in str(file_path) else "wise"
        unidentified_transactions = {
            "january": [],
            "february":[],
            "march":[],
            "april":[],
            "may":[],
            "june":[],
            "july":[],
            "august":[],
            "september":[],
            "october":[],
            "november":[],
            "december":[]
        }
        
        banks = []   
        transaction_id = []
        amount = []
        currency = []
        money_out = []
        money_in = []
        date_id = []
        category_id = []
    
    #-----------------------------------------------------------------------------------------#  
    #---------------------------------BARCLAYS------------------------------------------------# 
    #-----------------------------------------------------------------------------------------#
    
        if bank_ref == "barclays":
            
            count = 0 
            dates = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            money_out_bcl = pd.read_excel(file_path,sheet_name,usecols=["Money Out"]).to_dict()['Money Out']
            money_in_bcl = pd.read_excel(file_path,sheet_name,usecols=["Money In"]).to_dict()["Money In"]
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            end_balance = len(category_id) - 1 
            
            ### category id ###
            
            for description_text in description.values():
                lowered_description = str(description_text).lower()
                month = str(dates[count])[6:7]
                month_name = calendar.month_name[int(month)].lower()
                
                matched_category= None

                for keyword, category in KEYWORD_TO_CATEGORY["barclays"].items(): 
                    if keyword.lower() in lowered_description:
                        matched_category = category
                        category_id.append(matched_category)
                        break
                if money_in_bcl[count] > 0 and matched_category == None:
                    keyword = "income source"
                    category_id.append("bcl_cat_income01")
                    
                elif keyword.lower() not in lowered_description:
                    keyword = "bcl unidentified transfer " + str(count)
                    amount_unidentified = money_out_bcl[count] if math.isnan(money_in_bcl[count]) else money_in_bcl[count]
                    unidentified_transactions[month_name].append({keyword:amount_unidentified})
                    category_id.append("bcl_cat_extras18")
                
                count += 1
              
            category_id.pop(0) ## first and last row are containing the start balance and end balance with no transaction details hence not needed.
            category_id.pop(end_balance)
            
            
            ### dates id ###
             
                
            for key,val in dates.items():
                date_fk = str(val)[0:4] + str(val)[5:7] + str(val)[8:10]
                if key == 0 or key == len(dates)-1: ## reason of the condition explained in the categories logic
                    pass
                else:
                    date_id.append(date_fk)
                
            ### rest of data ###
            
            
            for key,val in money_out_bcl.items():
                
                if math.isnan(val) and math.isnan(money_in_bcl[key]) == False:
                    banks.append("barclays")
                    transaction_id.append("bcl_" + str(uuid.uuid4()))
                    amount.append(money_in_bcl[key])
                    currency.append("GBP")
                    money_in.append(True)
                    money_out.append(False)
                    
                elif math.isnan(val) == False and math.isnan(money_in_bcl[key]):
                    banks.append("barclays")
                    transaction_id.append("bcl_" + str(uuid.uuid4()))
                    amount.append(val)
                    currency.append("GBP")
                    money_in.append(False)
                    money_out.append(True)
                    
    #----------------------------------------------------------------------------------------#               
    #-----------------------------------MONZO------------------------------------------------#  
    #----------------------------------------------------------------------------------------#   
         
        elif bank_ref == "monzo":
            
            count = 0
            gbp_amount = pd.read_excel(file_path,sheet_name,usecols=["(GBP) Amount"])["(GBP) Amount"]
            dates = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            
            ### category id ###
                        
            for description_text in description.values():
                lowered_description = str(description_text).lower()
                month = str(dates[count])[6:7]
                month_name = calendar.month_name[int(month)].lower()

                matched_category = None

                for keyword, category in KEYWORD_TO_CATEGORY["monzo"].items():
                    if keyword.lower() in lowered_description:
                        matched_category = category
                        category_id.append(matched_category)
                        break
                         
                if gbp_amount[count] > 0 and matched_category == None:
                    keyword = "income source"
                    category_id.append("monzo_cat_transferin29")
                    
                elif keyword.lower() not in lowered_description:
                    keyword = "monzo unidentified transfer " + str(count)
                    amount_unidentified = gbp_amount[count]
                    unidentified_transactions[month_name].append({keyword:amount_unidentified})
                    category_id.append("monzo_cat_extras28")
                     
                count += 1
                
                
            ### dates id ### 
            
            for key,val in dates.items():
                date_fk = str(val)[0:3] + str(val)[5:7] + str(val)[8:10] 
                date_id.append(date_fk)
                
            ### rest of data ###
            
            for key,val in gbp_amount.items():
                if val < 0:
                    banks.append("monzo")
                    transaction_id.append("mon_" + str(uuid.uuid4()))
                    positive_val = str(val).strip("-")
                    amount.append(float(positive_val))
                    currency.append("GBP")
                    money_in.append(False)
                    money_out.append(True)
                else:
                    transaction_id.append("mon_" + str(uuid.uuid4()))
                    banks.append("monzo")
                    amount.append(val)
                    currency.append("GBP")
                    money_in.append(True)
                    money_out.append(False)
    
    #-------------------------------------------------------------------------------------#
    #---------------------------------WISE------------------------------------------------#
    #-------------------------------------------------------------------------------------#                
        elif bank_ref == "wise":
            
            count = 0
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            currency_wise = pd.read_excel(file_path,sheet_name,usecols=["Currency"]).to_dict()['Currency']
            incoming = pd.read_excel(file_path,sheet_name,usecols=["Incoming"]).to_dict()['Incoming']
            outgoing = pd.read_excel(file_path,sheet_name,usecols=["Outgoing"]).to_dict()['Outgoing']
            dates = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            
            ### category id ###
           
            for description_text in description.values():
                lowered_description = str(description_text).lower()
                month = str(dates[count])[6:7]
                month_name = calendar.month_name[int(month)].lower()
               
                if currency_wise[count] != "GBP" and "Converted" not in description[count]:
                    category_id.append("wise_cat_holidays30")

                matched_category = None
                
                for keyword, category in KEYWORD_TO_CATEGORY["wise"].items():
                    
                    
                    if keyword.lower() in lowered_description and currency_wise[count] == "GBP" and "Converted" not in description[count]:
                        matched_category = category
                        category_id.append(matched_category)
                    
                if currency_wise[count] == "GBP" and "Converted" not in description[count] and matched_category == None:
                    keyword = "wise unidentified transfer " + str(count)
                    amount_unidentified = outgoing[count] if math.isnan(incoming[count]) else incoming[count]
                    unidentified_transactions[month_name].append({keyword:amount_unidentified})
                    category_id.append("wise_cat_extras33")
                                
                count += 1
                
            ### dates id ###  
                    
            for key,val in dates.items():
                date_fk = str(val)[0:3] + str(val)[5:7] + str(val)[8:10]
                if "Converted" not in description[key]:
                    date_id.append(date_fk)
            
            ### rest of data ###
            
            for key,val in outgoing.items():
                if math.isnan(val) and math.isnan(incoming[key]) == False and "Converted" not in description[key]:
                    banks.append("wise")
                    transaction_id.append("wis_" + str(uuid.uuid4()))
                    amount.append(incoming[key])
                    currency.append(currency_wise[key])
                    money_in.append(True)
                    money_out.append(False)
                elif math.isnan(val) == False and math.isnan(incoming[key]) and "Converted" not in description[key]:
                    banks.append("wise")
                    transaction_id.append("wis_" + str(uuid.uuid4()))
                    positive_val = str(val).strip("-")
                    amount.append(float(positive_val))
                    currency.append(currency_wise[key])
                    money_in.append(False)
                    money_out.append(True)
                        
        # print(f"banks {len(banks)}")
        # print(f"transaction_id {len(transaction_id)}")
        # print(f"currency {len(currency)}")
        # print(f"amount {len(amount)}")
        # print(f"money out {len(money_out)}")
        # print(f"money in {len(money_in)}")
        # print(f"category id {len(category_id)}")
        # print(f"date id {len(date_id)}")
        # print(*category_id,sep='\n')
       

        # print(unidentified_transactions)
          
        data = {
            "id": transaction_id,
            "bank": banks,
            "amount": amount,
            "currency": currency,
            "money_in":money_in,
            "money_out":money_out,
            "category_id":category_id,
            "date_id": date_id
            
        }
        
        return data
      
      
    def history_transactions(self,bcl_file_path,monzo_file_path,wise_file_path):
        
        #-----------------------------------------------------------------------------------------#  
        #---------------------------------BARCLAYS------------------------------------------------# 
        #-----------------------------------------------------------------------------------------#
        
        bcl2_xlsx_container = []
        
        from_num = 1
        to_num = 2
        last_page_count = len(pd.ExcelFile(bcl_file_path).sheet_names) - 1
        description = pd.read_excel(bcl_file_path,f"2026-0{from_num} to 2026-0{to_num}",usecols=["Description"]).to_dict()['Description']
        bcl1_xlsx_df = pd.DataFrame(self.transaction_facts(bcl_file_path,"2025-12 to 2026-01")) # bcl 2025 sheet
        
        
        while to_num <= last_page_count:
            
            bcl_sheet_month = self.transaction_facts(bcl_file_path,f"2026-0{from_num} to 2026-0{to_num}")
            bcl2_xlsx_container.append(bcl_sheet_month)
            from_num += 1
            to_num += 1
        bcl_grouped = defaultdict(list)
        
        for bcl_sheet_month in bcl2_xlsx_container:
            for key, value in bcl_sheet_month.items():
                bcl_grouped[key].extend(value)

        bcl2_xlsx_df = pd.DataFrame(dict(bcl_grouped))
        
        #----------------------------------------------------------------------------------------#               
        #-----------------------------------MONZO------------------------------------------------#  
        #----------------------------------------------------------------------------------------#  
                
        monzo_xlsx_container = []
        months_dict = {0:"Jan",1:"Feb",2:"Mar",3:"Apr",4:"May",5:"Jun",6:"Jul",7:"Aug",8:"Sep"}
        
        monzo1_xlsx_df = pd.DataFrame(self.transaction_facts(monzo_file_path, "Dec 2025 (28-31)")) #2025 sheet
        
        
        for month_index in range(0,8):
            if month_index == 1:
                monzo_xlsx_container.append(self.transaction_facts(monzo_file_path,"Feb 2026 (01-28)"))
            elif month_index == 3:
                monzo_xlsx_container.append(self.transaction_facts(monzo_file_path,"Apr 2026 (01-30)"))
            elif month_index == 5:
                monzo_xlsx_container.append(self.transaction_facts(monzo_file_path,"Jun 2026 (01-30)"))
            elif month_index == 8:
                monzo_xlsx_container.append(self.transaction_facts(monzo_file_path,"Sep 2026 (01-30)"))
            else:
                monzo_xlsx_container.append(self.transaction_facts(monzo_file_path,f"{months_dict[month_index]} 2026 (01-31)"))
                
            month_index += 1
            
        monzo_grouped = defaultdict(list)
        
        for monzo_sheet_month in monzo_xlsx_container:
            for key,value in monzo_sheet_month.items():
                monzo_grouped[key].extend(value)

        monzo2_xlsx_df = pd.DataFrame(dict(monzo_grouped))
        
        #-------------------------------------------------------------------------------------#
        #---------------------------------WISE------------------------------------------------#
        #-------------------------------------------------------------------------------------#  
    
     
        wise_may_2026 = self.transaction_facts(wise_file_path, "2026-05 May")
        wise_jul_2026 = self.transaction_facts(wise_file_path, "2026-07 Jul")
        wise_aug_2026 = self.transaction_facts(wise_file_path, "2026-08 Aug")
        wise_sep_2026 = self.transaction_facts(wise_file_path, "2026-09 Sep")
        
        wise_xlsx_container = [wise_may_2026,wise_jul_2026,wise_aug_2026,wise_sep_2026]
        wise_grouped = defaultdict(list)
        
        for wise_sheet_month in wise_xlsx_container:
            for key,value in wise_sheet_month.items():
                wise_grouped[key].extend(value)
        
        wise_xlsx_df = pd.DataFrame(dict(wise_grouped))
        
        all_frames = [bcl1_xlsx_df,bcl2_xlsx_df,monzo1_xlsx_df,monzo2_xlsx_df,wise_xlsx_df]
        
        # return pd.concat(all_frames)


    def current_month_transactions(self,bcl_file_path,monzo_file_path,wise_file_path):
        
        #--------------------barclays--------------------------#
          
        blc_doc = pd.ExcelFile(bcl_file_path)
        bcl_sheet_name = blc_doc.sheet_names[-2]

        bcl_xlsx_df = pd.DataFrame(self.transaction_facts(bcl_file_path,bcl_sheet_name))
        
        #--------------------monzo-----------------------------#
        
        monzo_doc = pd.ExcelFile(monzo_file_path)
        monzo_sheet_name = monzo_doc.sheet_names[-1]
        
        monzo_xlsx_df = pd.DataFrame(self.transaction_facts(monzo_file_path,monzo_sheet_name))
        
        #-----------------------wise-----------------------------#
        
        wise_doc = pd.ExcelFile(wise_file_path)
        wise_sheet_name = wise_doc.sheet_names[-1]
        
        wise_xlsx_df = pd.DataFrame(self.transaction_facts(wise_file_path,wise_sheet_name))
        
        all_frames = [bcl_xlsx_df,monzo_xlsx_df,wise_xlsx_df]
        
        return pd.concat(all_frames)
    
    
transaction = Transaction()
excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

# print(transaction.transaction_facts(wise_file_path,"2026-05 May"))
# print(transaction.transaction_facts(barclays_file_path,"2026-05 to 2026-06"))
# print(transaction.transaction_facts(monzo_file_path,"Feb 2026 (01-28)"))

print(transaction.history_transactions(barclays_file_path,monzo_file_path,wise_file_path))