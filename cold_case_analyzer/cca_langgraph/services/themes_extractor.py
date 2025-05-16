import pandas as pd
from pyairtable import Api
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE

def remove_fields_prefix(df):
    df.columns = df.columns.str.replace("fields.", "")
    return df

def process_list_like_values(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(
                lambda x: ",".join(map(str, x)) if isinstance(x, list) else x
            )
    return df

def fetch_themes_dataframe():
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE)
    records = table.all()

    if not records:
        return pd.DataFrame(columns=["Theme", "Definition"])

    df = pd.json_normalize([record["fields"] for record in records])
    df = remove_fields_prefix(df)
    df = process_list_like_values(df)
    df = df[df["Relevant for Case Analysis"] == True]
    df = df[["Keywords", "Definition"]]
    df = df.rename(columns={"Keywords": "Theme"})
    df = df.reset_index(drop=True)
    return df

def fetch_themes_list():
    df = fetch_themes_dataframe()
    return df["Theme"].tolist()

if __name__ == "__main__":
    print("Themes DataFrame:")
    print(fetch_themes_dataframe())
    print("\nThemes List:")
    print(fetch_themes_list())