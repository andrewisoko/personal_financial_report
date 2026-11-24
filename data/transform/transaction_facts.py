import pandas as pd
import uuid
from pathlib import Path
import math
import calendar
from collections import defaultdict
from non_confidential_keywords import KEYWORD_TO_CATEGORY
import requests



class Transaction:
    
    def __init__(self):
        self.payment_dates = [] # store main income date for each month, only one value expected.
        self.conversions = {} # updating dict with non-gbp currencies as key and rate as key when succesfully fatching data from api to avoid multiple calls for the same rate 
        
    
    def convert_currency(self,amount, from_currency, to_currency):

            
            if from_currency in self.conversions:

                conv_rate = amount * self.conversions[from_currency]        
                return round(conv_rate,2) 
            else:
                try:
                    response = requests.get(
                        "https://api.frankfurter.dev/v1/latest",
                        params={"from": from_currency, "to": to_currency},
                        timeout=10,
                    )
                    response.raise_for_status()
                    data = response.json()

                    rate = round(data["rates"][to_currency],2)
                    self.conversions.update({from_currency:rate})
                    conv_rate = amount * rate
                    return   round(conv_rate,2) 

                except requests.exceptions.HTTPError:
                    print("Error: Invalid currency code or API issue.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                return None
        
    def transaction_facts(self,file_path,sheet_name):
        
       
        bank_ref = "barclays" if "barclays" in str(file_path) else "monzo" if "monzo" in str(file_path) else "wise"
        unidentified_transactions = {month: [] for month in list(calendar.month_name)[1:]}
        
        banks:list[str] = []   
        transaction_id:list[str] = []
        amount:list[float]  = []
        converted_to_gbp:list[bool] = []
        currency:list[str]  = []
        money_out:list[bool]  = []
        money_in:list[bool] = []
        month_payment_period:list[str] = [] # month from the payment received in descending order.
        

        date_id:list[str] = []
        category_id:list[str] = []
    
    #-----------------------------------------------------------------------------------------#  
    #---------------------------------BARCLAYS------------------------------------------------# 
    #-----------------------------------------------------------------------------------------#

        if bank_ref == "barclays":
            
            count = 0 
            dates:dict = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            money_out_bcl:dict = pd.read_excel(file_path,sheet_name,usecols=["Money Out"]).to_dict()['Money Out']
            money_in_bcl:dict = pd.read_excel(file_path,sheet_name,usecols=["Money In"]).to_dict()["Money In"]
            description:dict = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            end_balance:int = len(category_id) - 1 
            
            ### category id ###
                                    
            for description_text in description.values():
                lowered_description = str(description_text).lower()
                month = str(dates[count])[5:7]
                month_name:str = calendar.month_name[int(month)]
                
    
                matched_category= None
                for keyword, category in KEYWORD_TO_CATEGORY["barclays"].items():
                    
                    ### appending date of main income received
                    bcl_amount:float = money_out_bcl[count] if math.isnan(money_in_bcl[count]) else money_in_bcl[count]
                    if category == "bcl_cat_income01" and bcl_amount > 999:
                        self.payment_dates.append(dates[count])
                        break
                   
                    
                    if keyword.lower() in lowered_description:
                        matched_category = category
                        category_id.append(matched_category)
                        break
                if money_in_bcl[count] > 0 and matched_category == None:
                    keyword = "income source"
                    category_id.append("bcl_cat_income01")
                    
                elif keyword.lower() not in lowered_description:
                    keyword = "bcl unidentified transfer " + str(count)
                    amount_unidentified:float = money_out_bcl[count] if math.isnan(money_in_bcl[count]) else money_in_bcl[count]
                    unidentified_transactions[month_name].append({keyword:amount_unidentified})
                    category_id.append("bcl_cat_extras18")
                
                count += 1
                
            ### assiging month at each row on the sheet based on time comparison between row and main income date.
            
            for index,datetime in dates.items():
                if index == 0 or index == len(dates)-1:
                    pass
                else:
                    if self.payment_dates[-1] == pd.Timestamp("2025-12-31 00:00:00"): 
                        month_payment_period.append("December 2025" if datetime < self.payment_dates[-1] else "January")
                    elif "-12-" in str(self.payment_dates[-1]):
                        month_payment_period.append("December" if datetime < self.payment_dates[-1] else "January")
                    else:
                        month = str(dates[0])[5:7] # resetting the month count
                        month_payment_period.append(calendar.month_name[int(month)] if self.payment_dates[-1] > datetime else calendar.month_name[int(month) + 1])
                       
    
       
              
            category_id.pop(0) ## first and last row are containing the start balance and end balance with no transaction details hence not needed.
            category_id.pop(end_balance)
              
            ### dates id ###
             
                
            for index,datetime in dates.items():
                date_fk = str(datetime)[0:4] + str(datetime)[5:7] + str(datetime)[8:10]
                if index == 0 or index == len(dates)-1: ## reason of the condition explained in the categories logic
                    pass
                else:
                    date_id.append(date_fk)
                
            ### rest of data ###
            
            
            for index,amount_out in money_out_bcl.items():
                
                if math.isnan(amount_out) and math.isnan(money_in_bcl[index]) == False:
                    banks.append("barclays")
                    transaction_id.append("bcl_" + str(uuid.uuid4()))
                    amount.append(money_in_bcl[index])
                    converted_to_gbp.append(False)
                    currency.append("GBP")
                    money_in.append(True)
                    money_out.append(False)
                    
                elif math.isnan(amount_out) == False and math.isnan(money_in_bcl[index]):
                    banks.append("barclays")
                    transaction_id.append("bcl_" + str(uuid.uuid4()))
                    amount.append(amount_out)
                    converted_to_gbp.append(False)
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
           
            month_in_dates = list(set([calendar.month_name[int(str(month)[5:7])] for index,month in dates.items()]))
            monzo_date_bc_payment = [payment_dt_month for payment_dt_month in self.payment_dates if calendar.month_name[int(str(payment_dt_month)[5:7])] == month_in_dates[0]] 
            
            
            ### category id ###
                        
            for description_text in description.values():
                lowered_description = str(description_text).lower()
                month = str(dates[count])[5:7]
                month_name:str = calendar.month_name[int(month)]

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
            
    
            ### different from barlays, extracting relevant payment date from already populated list
            
            if len(monzo_date_bc_payment) > 0:
                for index,datetime in dates.items():
                    if monzo_date_bc_payment[0] == pd.Timestamp("2025-12-31 00:00:00"):
                        month_payment_period.append("December 2025" if datetime < monzo_date_bc_payment[0] else "January")
                    elif "-12-" in str(monzo_date_bc_payment[0]):
                        month_payment_period.append("December" if datetime < monzo_date_bc_payment[0] else "January")
                    else:
                        month_payment_period.append(calendar.month_name[int(month)] if monzo_date_bc_payment[0] > datetime  else calendar.month_name[int(month) + 1])
                
                
            ### dates id ### 
            
            for index,datetime in dates.items():
                date_fk = str(datetime)[0:4] + str(datetime)[5:7] + str(datetime)[8:10]
                date_id.append(date_fk)
                
            ### rest of data ###
            
            for index,amount_val in gbp_amount.items():
                if amount_val < 0:
                    banks.append("monzo")
                    transaction_id.append("mon_" + str(uuid.uuid4()))
                    positive_val = str(amount_val).strip("-")
                    amount.append(float(positive_val))
                    converted_to_gbp.append(False)
                    currency.append("GBP")
                    money_in.append(False)
                    money_out.append(True)
                else:
                    transaction_id.append("mon_" + str(uuid.uuid4()))
                    banks.append("monzo")
                    amount.append(amount_val)
                    converted_to_gbp.append(False)
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
            
            month_in_dates = list(set([calendar.month_name[int(str(month)[5:7])] for key,month in dates.items()]))
            wise_date_bc_payment = [payment_dt_month for payment_dt_month in self.payment_dates if calendar.month_name[int(str(payment_dt_month)[5:7])] == month_in_dates[0]] 
                     
            ### category id ###
           
            for description_text in description.values():
                lowered_description = str(description_text).lower()
                month = str(dates[count])[5:7]
                month_name = calendar.month_name[int(month)]
               
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
                
           
            for index,datetime in dates.items():
                if "Converted" not in description[index] and len(wise_date_bc_payment) > 0:
                    if wise_date_bc_payment[0] == pd.Timestamp("2025-12-31 00:00:00"):
                        month_payment_period.append("December 2025" if datetime < wise_date_bc_payment[0] else "January")
                    elif "-12-" in str(wise_date_bc_payment[0]):
                        month_payment_period.append("December" if datetime < wise_date_bc_payment[0] else "January")
                    else:
                        month_payment_period.append(calendar.month_name[int(month)] if wise_date_bc_payment[0] > datetime  else calendar.month_name[int(month) + 1])
                elif "Converted" not in description[index]:
                    month_payment_period.append(calendar.month_name[int(month)])
                    
                
            ### dates id ###  
                    
            for index,datetime in dates.items():
                date_fk = str(datetime)[0:4] + str(datetime)[5:7] + str(datetime)[8:10]
                if "Converted" not in description[index]:
                    date_id.append(date_fk)
            
            ### rest of data ###
            
            for index,amount_out in outgoing.items():
                if math.isnan(amount_out) and math.isnan(incoming[index]) == False and "Converted" not in description[index]:
                    banks.append("wise")
                    transaction_id.append("wis_" + str(uuid.uuid4()))
                    amount.append(incoming[index] if currency_wise[index] == 'GBP' else self.convert_currency(incoming[index],currency_wise[index],'GBP'))
                    converted_to_gbp.append(False if currency_wise[index] == 'GBP' else True)
                    currency.append(currency_wise[index])
                    money_in.append(True)
                    money_out.append(False)
                elif math.isnan(amount_out) == False and math.isnan(incoming[index]) and "Converted" not in description[index]:
                    banks.append("wise")
                    transaction_id.append("wis_" + str(uuid.uuid4()))
                    positive_val = str(amount_out).strip("-")
                    amount.append(float(positive_val) if currency_wise[index] == 'GBP' else self.convert_currency(float(positive_val),currency_wise[index],'GBP'))
                    converted_to_gbp.append(False if currency_wise[index] == 'GBP' else True)
                    currency.append(currency_wise[index])
                    money_in.append(False)
                    money_out.append(True)
        
                  
        data = {
            "id": transaction_id,
            "bank": banks,
            "amount": amount,
            "converted_to_gbp":converted_to_gbp,
            "currency": currency,
            "money_in":money_in,
            "money_out":money_out,
            "month_payment_period":month_payment_period,
            "category_id":category_id,
            "date_id": date_id
            
        }
     
        return data
      
      
    def history_transactions(self,bcl_file_path,monzo_file_path,wise_file_path):
    
       
        #---------------------------------BARCLAYS------------------------------------------------# 
       
        
        bcl_sheet_names = [bcl_sheet_month for bcl_sheet_month in pd.ExcelFile(bcl_file_path).sheet_names if bcl_sheet_month != "All Transactions"]
        bcl_xlsx_container = [self.transaction_facts(bcl_file_path,bcl_sheet_month) for bcl_sheet_month in bcl_sheet_names]
        
              
        bcl_grouped = defaultdict(list)
        
        for bcl_sheet_month in bcl_xlsx_container:
            for col, row_list in bcl_sheet_month.items():
                bcl_grouped[col].extend(row_list)

        bcl_xlsx_df = pd.DataFrame(dict(bcl_grouped))
        
        bcl_payment_months = [calendar.month_name[int(str(date)[5:7])][0:3] for date in self.payment_dates]
    
                 
        #-----------------------------------MONZO------------------------------------------------#  
    
          
        monzo_sheet_names = [monzo_sheet_month for monzo_sheet_month in pd.ExcelFile(monzo_file_path).sheet_names if monzo_sheet_month[0:3] in bcl_payment_months]
        monzo_xlsx_container = [self.transaction_facts(monzo_file_path,monzo_sheet_month) for monzo_sheet_month in monzo_sheet_names] 

        monzo_grouped = defaultdict(list)
        
        for monzo_sheet_month in monzo_xlsx_container:
            for  col,row_list in monzo_sheet_month.items():
                monzo_grouped[col].extend(row_list)

        monzo_xlsx_df = pd.DataFrame(dict(monzo_grouped))
        
        #---------------------------------WISE------------------------------------------------#
    
        wise_sheet_names = [wise_sheet_month for wise_sheet_month in pd.ExcelFile(wise_file_path).sheet_names]
        wise_xlsx_container = [self.transaction_facts(wise_file_path,wise_sheet_month) for wise_sheet_month in wise_sheet_names if wise_sheet_month[8:11] in bcl_payment_months] 
        
        wise_grouped = defaultdict(list)
        
        for wise_sheet_month in wise_xlsx_container:
            for col,row_list in wise_sheet_month.items():
                wise_grouped[col].extend(row_list)
        
        wise_xlsx_df = pd.DataFrame(dict(wise_grouped))
         
                
        all_frames = [bcl_xlsx_df,monzo_xlsx_df,wise_xlsx_df]
        
        return pd.concat(all_frames).drop_duplicates()
      
      
     


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
        
        return pd.concat(all_frames).drop_duplicates()
    
    
transaction = Transaction()
excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"


print(transaction.history_transactions(barclays_file_path,monzo_file_path,wise_file_path))