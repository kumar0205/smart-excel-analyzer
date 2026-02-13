import pandas as pd

def detect_columns(df):
    cols = {c.lower(): c for c in df.columns}

    mapping = {}

    keywords = {
        "date": ["date","day","time","order_date"],
        "price": ["price","amount","cost","rate"],
        "quantity": ["qty","quantity","units","count"],
        "product": ["product","item","name"],
        "customer": ["customer","client","buyer","user"],
        "city": ["city","location","place"],
        "category": ["category","group","type","dept"]
    }

    for key, words in keywords.items():
        for w in words:
            for col in cols:
                if w in col:
                    mapping[key] = cols[col]

    return mapping
