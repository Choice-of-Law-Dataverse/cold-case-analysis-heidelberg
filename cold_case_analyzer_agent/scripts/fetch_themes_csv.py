#!/usr/bin/env python3
import pandas as pd
from pyairtable import Api
import os
from dotenv import load_dotenv
load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_CONCEPTS_TABLE = os.getenv("AIRTABLE_CONCEPTS_TABLE") or "Concepts"  # Default to "Concepts" if not set

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

def fetch_themes_dataframe() -> pd.DataFrame:
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE)
    records = table.all()
    if not records:
        return pd.DataFrame(columns=["Theme","Definition"])
    df = pd.json_normalize([r["fields"] for r in records])
    df = remove_fields_prefix(df)
    df = process_list_like_values(df)
    df = df[df["Relevant for Case Analysis"] == True]
    df = df[["Keywords","Definition"]].rename(columns={"Keywords":"Theme"}).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = fetch_themes_dataframe()
    out = "data/themes.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} themes to {out}")