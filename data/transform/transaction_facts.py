import pandas as pd
import uuid
from pathlib import Path
import math
from personal_financial_report.non_confidential_keywords import KEYWORD_TO_CATEGORY



class Transaction:
    
    def transaction_facts(self,file_path,sheet_name):
        
       
        bank_ref = "barclays" if "barclays" in str(file_path) else "monzo" if "monzo" in str(file_path) else "wise"
        unidentified_transactions = []
        banks = []   
        transaction_id = []
        amount = []
        currency = []
        money_out = []
        money_in = []
        date_id = []
        category_id = []
        
       
        if bank_ref == "barclays":
            
            
            dates = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            money_out_bcl = pd.read_excel(file_path,sheet_name,usecols=["Money Out"]).to_dict()['Money Out']
            money_in_bcl = pd.read_excel(file_path,sheet_name,usecols=["Money In"]).to_dict()["Money In"]
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            
            for description_text in description.values():
                lowered_description = str(description_text).lower()

                matched_category= None

                for keyword, category in KEYWORD_TO_CATEGORY["barclays"].items():
                    if keyword.lower() in lowered_description:
                        matched_category = category
                        category_id.append(matched_category)
                    else:
                        matched_category = "bcl_cat_extras18"
                        category_id.append(matched_category)
            
            
            for key,val in dates.items():
                date_fk = str(val)[0:3] + str(val)[5:7] + str(val)[8:10] 
                date_id.append(date_fk)
                
            
            for key,val in money_out_bcl.items():
                
                if math.isnan(val) and math.isnan(money_in_bcl[key]) == False:
                    banks.append("barclays")
                    transaction_id.append("bcl_" + str(uuid.uuid4()))
                    amount.append(money_in_bcl[key])
                    currency.append("GBP")
                    money_in.append(True)
                    money_out.append(False)
                    
                elif math.isnan(val) == False and math.isnan(money_in_bcl[key]):
                    banks.append("wise")
                    transaction_id.append("bcl_" + str(uuid.uuid4()))
                    amount.append(val)
                    currency.append("GBP")
                    money_in.append(False)
                    money_out.append(True)
            
        elif bank_ref == "monzo":
            
            count = 0
            gbp_amount = pd.read_excel(file_path,sheet_name,usecols=["(GBP) Amount"])["(GBP) Amount"]
            dates = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            
            for description_text in description.values():
                lowered_description = str(description_text).lower()

                matched_category = None

                for keyword, category in KEYWORD_TO_CATEGORY["monzo"].items():
                    if keyword.lower() in lowered_description:
                        # print(f"keyword name {keyword} {gbp_amount[count]}")
                        matched_category = category
                        category_id.append(matched_category)
                        break
                         
                if gbp_amount[count] > 0 and category not in category_id:
                    keyword = "income source"
                    # print(f"keyword name {keyword} {gbp_amount[count]}")
                    category_id.append("monzo_cat_transferin29")
                    
                elif keyword.lower() not in lowered_description:
                    keyword = "unidentified transfer of" + str(gbp_amount[count])
                    # print(f"keyword name {keyword} {gbp_amount[count]}")
                    unidentified_transactions.append({keyword:category})
                    category_id.append("monzo_cat_extras28")
                     
                count += 1
            
            for key,val in dates.items():
                date_fk = str(val)[0:3] + str(val)[5:7] + str(val)[8:10] 
                date_id.append(date_fk)
            
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
                    
        elif bank_ref == "wise":
            
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            currency_wise = pd.read_excel(file_path,sheet_name,usecols=["Currency"]).to_dict()['Currency']
            incoming = pd.read_excel(file_path,sheet_name,usecols=["Incoming"]).to_dict()['Incoming']
            outgoing = pd.read_excel(file_path,sheet_name,usecols=["Outgoing"]).to_dict()['Outgoing']
            dates = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
            description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
            
            for description_text in description.values():
                lowered_description = str(description_text).lower()

                matched_category = None
                count = 0
                
                for keyword, category in KEYWORD_TO_CATEGORY["wise"].items():
                    if currency_wise[count] != "GBP":
                        matched_category = "wise_cat_holidays30"
                        category_id.append(matched_category)
                        
                    elif keyword.lower() in lowered_description and currency_wise[count] == "GBP":
                        matched_category = category
                        category_id.append(matched_category)
                    else:
                        matched_category = "wise_cat_extras33"
                        category_id.append(matched_category) 
                    count += 1
                        
            for key,val in dates.items():
                date_fk = str(val)[0:3] + str(val)[5:7] + str(val)[8:10] 
                date_id.append(date_fk)
            
            
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
        # print(f"category id {category_id}")
     
        print(unidentified_transactions)
          
        # data = {
        #     "id": transaction_id,
        #     "bank": banks,
        #     "amount": amount,
        #     "currency": currency,
        #     "money_in":money_in,
        #     "money_out":money_out,
        #     "category_id":category_id,
        #     "date_id": date_id
            
        # }
        
        # return pd.DataFrame(data)
      
      
    
    
transaction = Transaction()
excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

# print(transaction.transaction_facts(wise_file_path,"2026-05 May"))
# print(transaction.transaction_facts(barclays_file_path,"2025-12 to 2026-01"))
print(transaction.transaction_facts(monzo_file_path,"Feb 2026 (01-28)"))