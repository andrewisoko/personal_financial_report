import pandas as pd



class Category:
    
    def all_categories_table(self):
         
        
        data = {
            "id": [
                   "bcl_cat_income01","bcl_cat_rent02","bcl_cat_water03","bcl_cat_electricity04","bcl_cat_gym05","bcl_cat_tax06",
                   "bcl_cat_food07","bcl_cat_extrafood08","bcl_cat_nightsout09","bcl_cat_homenecessities10","bcl_cat_spotifythree11","bcl_cat_transport11",
                   "bcl_cat_community12","bcl_cat_s&p50013","bcl_cat_aitools14","bcl_cat_holidays15","bcl_cat_acerlaptop16","bcl_cat_health17","bcl_cat_extra18",
                   
                   "monzo_cat_gym19","monzo_cat_food20","monzo_cat_extrafood21","monzo_cat_nightsout22","monzo_cat_homenecessities23","monzo_cat_transport24",
                   "monzo_cat_health25","monzo_cat_extras26",
                   
                   "wise_cat_holidays27","wise_cat_food28","wise_cat_nightsout29","wise_cat_extras30"
                   
                   ],
            "name": [ "income","rent","water","electricity","gym","tax","food","extra food","nights out","home necessities",
                     "spotify and three","transport","community","s&p500","ai tools","holidays","acer laptop","health","extra",
                     
                     "gym","food","extra food","nights out","home necessities","transport","health","extras",
                     
                     "holidays","food","nights out","extras"
                    ]
        }
        return pd.DataFrame(data)
    
    
category = Category()
    
print(category.all_categories_table())