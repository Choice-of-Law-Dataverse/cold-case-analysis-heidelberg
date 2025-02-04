import pandas as pd
from pyairtable import Api
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE

# data processing
def remove_fields_prefix(df):
    df.columns = df.columns.str.replace('fields.', '')
    return df

def process_list_like_values(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: ','.join(map(str, x)) if isinstance(x, list) else x)
    return df

# data fetching
def fetch_and_prepare_concepts():
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE)
    records = table.all()

    if records:
        df = pd.json_normalize([record['fields'] for record in records])  # Directly normalize 'fields'
        df = remove_fields_prefix(df)
        df = process_list_like_values(df)
        df = df[df["Relevant for case analysis"] == True]
        df = df[["Keywords", "Definition"]]
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no records
