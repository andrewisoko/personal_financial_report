import pandas as pd
import uuid
from pathlib import Path
import math



class Transaction:
    
    def transaction_facts(self,file_path,sheet_name):
        
       
        banks = ["barclays" if "barclays" in str(file_path) else "monzo" if "monzo" in str(file_path) else "wise"]
        transaction_id = []
        amount = []
        currency = []
        money_out = []
        money_in = []
        date_id = []
        category_id = []
        
        for bank_name in banks:
            if bank_name == "barclays":
                
                date_foreign_key = pd.read_excel(file_path,sheet_name,usecols=["Date"]).to_dict()['Date']
                money_out_bcl = pd.read_excel(file_path,sheet_name,usecols=["Money Out"]).to_dict()['Money Out']
                money_in_bcl = pd.read_excel(file_path,sheet_name,usecols=["Money In"]).to_dict()["Money In"]
                
                for key,val in money_out_bcl.items():
                    
                    if math.isnan(val) and math.isnan(money_in_bcl[key]) == False:
                        transaction_id.append("bcl_" + str(uuid.uuid4()))
                        amount.append(money_in_bcl[key])
                        currency.append("GBP")
                        money_in.append(True)
                        money_out.append(False)
                        
                    elif math.isnan(val) == False and math.isnan(money_in_bcl[key]):
                        transaction_id.append("bcl_" + str(uuid.uuid4()))
                        amount.append(val)
                        currency.append("GBP")
                        money_in.append(False)
                        money_out.append(True)
                
            elif bank_name == "monzo":
                gbp_amount = pd.read_excel(file_path,sheet_name,usecols=["(GBP) Amount"])["(GBP) Amount"]
                
                for key,val in gbp_amount.items():
                    if val < 0:
                        transaction_id.append("mon_" + str(uuid.uuid4()))
                        positive_val = str(val).strip("-")
                        amount.append(float(positive_val))
                        currency.append("GBP")
                        money_in.append(False)
                        money_out.append(True)
                    else:
                        transaction_id.append("mon_" + str(uuid.uuid4()))
                        amount.append(val)
                        currency.append("GBP")
                        money_in.append(True)
                        money_out.append(False)
                        
            elif bank_name == "wise":
                
                description = pd.read_excel(file_path,sheet_name,usecols=["Description"]).to_dict()['Description']
                currency_wise = pd.read_excel(file_path,sheet_name,usecols=["Currency"]).to_dict()['Currency']
                incoming = pd.read_excel(file_path,sheet_name,usecols=["Incoming"]).to_dict()['Incoming']
                outgoing = pd.read_excel(file_path,sheet_name,usecols=["Outgoing"]).to_dict()['Outgoing']
                
               
                for key,val in outgoing.items():
                    if math.isnan(val) and math.isnan(incoming[key]) == False and "Converted" not in description[key]:
                        transaction_id.append("wis_" + str(uuid.uuid4()))
                        amount.append(incoming[key])
                        currency.append(currency_wise[key])
                        money_in.append(True)
                        money_out.append(False)
                    elif math.isnan(val) == False and math.isnan(incoming[key]) and "Converted" not in description[key]:
                        transaction_id.append("wis_" + str(uuid.uuid4()))
                        positive_val = str(val).strip("-")
                        amount.append(float(positive_val))
                        currency.append(currency_wise[key])
                        money_in.append(False)
                        money_out.append(True)
        
        return amount       
        # data = {
        #     "id": transaction_id,
        #     "bank": banks,
        #     "amount": amount,
        #     "currency": currency,
        #     "money_in":money_in,
        #     "money_out":money_out,
        #     "category_id":
        #     "date_id":
            
        # }
        
        # return data
      
      
    
    
transaction = Transaction()
excel_dir = Path(__file__).parent.parent / "extract"/ "excel"

barclays_file_path = excel_dir / "barclays_excel" / "barclays_statements.xlsx"
monzo_file_path = excel_dir / "monzo_excel" / "monzo_statements.xlsx"
wise_file_path = excel_dir / "wise_excel" / "wise_statements.xlsx"

# print(transaction.transaction_facts(wise_file_path,"2026-05 May"))
# print(transaction.transaction_facts(barclays_file_path,"2025-12 to 2026-01"))
print(transaction.transaction_facts(wise_file_path,"2026-05 May"))