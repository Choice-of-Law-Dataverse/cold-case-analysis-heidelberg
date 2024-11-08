import pandas as pd
from pyairtable import Api
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

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
def fetch_data(table_id):
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, table_id)
    records = table.all()

    if records:
        df = pd.json_normalize([record['fields'] for record in records])  # Directly normalize 'fields'
        df = remove_fields_prefix(df)
        df = process_list_like_values(df)
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no records
