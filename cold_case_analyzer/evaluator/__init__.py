import os
import pandas as pd
import colorama
from colorama import Fore, Style

from data_handler.local_file_retrieval import fetch_local_ground_truths

# Import the specialized evaluation modules
from evaluator.bertopic import evaluate_bertopic
from evaluator.g_eval import evaluate_g_eval

# List all columns (besides "ID") that we want to compare
COLUMNS_TO_COMPARE = [
    "Col Section",
    "Abstract",
    "Relevant Facts",
    "Rules of Law",
    "Choice of Law Issue Classification",
    "Choice of Law Issue",
    "Court's Position",
]

def evaluate_results(inputs: pd.DataFrame, results_csv: str):
    """
    High-level function:
      1) Loads ground truth and generated results,
      2) Merges them with the DataFrame 'inputs' that includes 'Original text',
      3) Calls the specialized BERTScore and G-Eval functions.
    """

    colorama.init(autoreset=True)

    # 1) Load ground truths (must have columns: ID + COLUMNS_TO_COMPARE)
    gt_df = fetch_local_ground_truths()  

    # 2) Load generated results (must have columns: ID + COLUMNS_TO_COMPARE)
    results_df = pd.read_csv(results_csv)

    # Merge ground truths and results on ID
    merged_df = pd.merge(
        gt_df, 
        results_df, 
        on="ID", 
        suffixes=("_gt", "_gen"),
        how="inner"
    )

    # Merge in the original court-decision text (required for G-Eval)
    if "Original text" not in inputs.columns:
        raise ValueError("Ensure your 'inputs' DataFrame has the column 'Original text'.")

    merged_df = pd.merge(
        merged_df,
        inputs[["ID", "Original text"]],
        on="ID",
        how="inner"
    )

    # --- Evaluate with BERTScore ---
    evaluate_bertopic(merged_df, COLUMNS_TO_COMPARE)

    # --- Evaluate with G-Eval ---
    evaluate_g_eval(merged_df, COLUMNS_TO_COMPARE)
