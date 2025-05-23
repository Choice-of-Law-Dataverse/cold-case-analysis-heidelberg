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

def filter_themes_by_list(themes_list: list[str]) -> pd.DataFrame:
    """
    Filters the themes DataFrame by a given list of theme names.

    Args:
        themes_list: A list of theme names to filter by.

    Returns:
        A pandas DataFrame containing only the rows where the 'Theme'
        matches the themes in the input list.
    """
    #print("\n\n--- FILTERING THEMES ---")
    #print(f"Input themes list: {themes_list}\n")
    df = fetch_themes_dataframe()
    if df.empty or not themes_list:
        return pd.DataFrame(columns=df.columns) # Return empty DataFrame with same columns
    
    # Filter the DataFrame
    # The 'Theme' column in the DataFrame can contain comma-separated strings if a keyword was a list initially.
    # We need to handle cases where a theme in themes_list might be part of a comma-separated string in df['Theme'].
    # However, the current 'Theme' column after rename from 'Keywords' should be single string themes if 'Keywords' was processed correctly.
    # Assuming 'Theme' column contains single theme strings after processing.
    # If 'Theme' could contain multiple comma-separated themes per row, the logic would need to be:
    # filtered_df = df[df['Theme'].apply(lambda x: any(theme_item in x.split(',') for theme_item in themes_list))]
    # For now, assuming direct match is sufficient based on current df structure.
    filtered_df = df[df['Theme'].isin(themes_list)]
    themes_table_filtered_str = format_themes_table(filtered_df)
    #print(f"Filtered themes table:\n{themes_table_filtered_str}\n")
    return themes_table_filtered_str

def fetch_themes_list():
    df = fetch_themes_dataframe()
    return df["Theme"].tolist()

def format_themes_table(df):
    if df.empty:
        return "No themes available."
    table_str = "| Theme | Definition |\n"
    table_str += "|-------|------------|\n"
    for _, row in df.iterrows():
        theme = str(row['Theme']).replace("|", "\\|")
        definition = str(row['Definition']).replace("|", "\\|")
        table_str += f"| {theme} | {definition} |\n"
    return table_str

THEMES_TABLE_DF = fetch_themes_dataframe()
THEMES_TABLE_STR = format_themes_table(THEMES_TABLE_DF)