import os
import pandas as pd


def fetch_local_data():
    """
    Loads analysis cases from the Excel file located at:
    cold-case-analysis/cold_case_analyzer/data/cases.xlsx
    """
    # Compute the absolute path to the "data" folder.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    file_path = os.path.join(base_dir, "cases.xlsx")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file at {file_path}: {e}")
        raise

    return df


def fetch_local_concepts():
    """
    Loads analysis concepts from the Excel file located at:
    cold-case-analysis/cold_case_analyzer/data/concepts.xlsx
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    file_path = os.path.join(base_dir, "concepts.xlsx")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file at {file_path}: {e}")
        raise

    return df
