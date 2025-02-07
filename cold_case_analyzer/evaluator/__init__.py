import os
import pandas as pd
from bert_score import score
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

import colorama
from colorama import Fore, Style

from data_handler.local_file_retrieval import fetch_local_ground_truths

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
    Evaluates model-generated results by:
      1. Loading ground-truth data (same columns as results).
      2. Merging on 'ID' with the generated CSV.
      3. Computing BERTScore for each column in COLUMNS_TO_COMPARE.
      4. Doing a no-reference G-Eval (placeholder) for each column of generated text.
      5. Printing results to terminal with color formatting.
    
    :param inputs: DataFrame containing original court decision texts (includes 'ID' column).
    :param results_csv: Path to the CSV file containing the model's generated outputs.
                       This file must contain columns 'ID' + those in COLUMNS_TO_COMPARE.
    """

    colorama.init(autoreset=True)

    # 1) Load ground truths
    gt_df = fetch_local_ground_truths()  
    # Ensure gt_df has columns: ["ID"] + COLUMNS_TO_COMPARE
    # e.g. "ID Col Section Abstract Relevant Facts Rules of Law Choice of Law Issue Classification Choice of Law Issue Court's Position"

    # 2) Load generated results
    results_df = pd.read_csv(results_csv)
    # Should also have "ID" + the same columns as ground truths:
    # e.g. "ID Col Section Abstract Relevant Facts Rules of Law Choice of Law Issue Classification Choice of Law Issue Court's Position"

    # Merge on "ID". By default, same column names will be suffixed with _x (ground truth) and _y (generated).
    merged_df = pd.merge(
        gt_df, 
        results_df, 
        on="ID", 
        suffixes=("_gt", "_gen"),  # so "Col Section" => "Col Section_gt" and "Col Section_gen"
        how="inner"
    )

    if "Original text" not in inputs.columns:
        raise ValueError("Ensure 'inputs' DataFrane has the column 'Original text'")
    
    merged_df = pd.merge(
        merged_df,
        inputs[["ID", "Original text"]],
        on="ID",
        how="inner"
    )

    # 3) For each column in COLUMNS_TO_COMPARE, compute BERTScore
    print(f"\n{Fore.CYAN}========== EVALUATION REPORT =========={Style.RESET_ALL}\n")

    # Keep track of average scores across all columns if you like
    all_precision = []
    all_recall = []
    all_f1 = []

    for col in COLUMNS_TO_COMPARE:
        # references = ground truth
        references = merged_df[f"{col}_gt"].fillna("").tolist()
        # candidates = generated answers
        candidates = merged_df[f"{col}_gen"].fillna("").tolist()

        # BERTScore
        # If your text is in a non-English language, set 'lang' accordingly
        P, R, F1 = score(candidates, references, lang="en", verbose=False)
        
        p_avg = P.mean().item()
        r_avg = R.mean().item()
        f_avg = F1.mean().item()

        all_precision.append(p_avg)
        all_recall.append(r_avg)
        all_f1.append(f_avg)

        print(f"{Fore.GREEN}Column: {col}{Style.RESET_ALL}")
        print(f"  BERTScore Precision: {p_avg:.4f}")
        print(f"  BERTScore Recall:    {r_avg:.4f}")
        print(f"  BERTScore F1:        {f_avg:.4f}\n")

    # Optionally, print an overall average across all columns
    if all_precision:
        print(f"{Fore.YELLOW}--- AVERAGE BERTScore (across all compared columns) ---{Style.RESET_ALL}")
        print(f"  Precision: {sum(all_precision)/len(all_precision):.4f}")
        print(f"  Recall:    {sum(all_recall)/len(all_recall):.4f}")
        print(f"  F1:        {sum(all_f1)/len(all_f1):.4f}\n")

    # 4) G-Eval (no-reference) placeholder for each column
    correctness_metric = GEval(
        name="Correctness",
        # Instead of 'criteria', you can supply 'evaluation_steps', but not both at once:
        evaluation_steps=[
            "Check whether the facts in the 'actual output' contradict any facts in the 'input'.",
            "Penalize omissions of crucial details that appear in the 'input'.",
            "Penalize vague or contradictory claims.",
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
    )

    # 5) Now compute G-Eval column-by-column by measuring each row
    for col in COLUMNS_TO_COMPARE:
        original_texts = merged_df["Original text"].fillna("").tolist()
        generated_texts = merged_df[f"{col}_gen"].fillna("").tolist()

        g_scores = []
        for orig, gen in zip(original_texts, generated_texts):
            test_case = LLMTestCase(
                input=orig,
                actual_output=gen
                # no expected_output because we are doing a no-reference approach
            )
            correctness_metric.measure(test_case)
            # correctness_metric.score is updated each time we call measure
            # we can store that for averaging
            g_scores.append(correctness_metric.score)

        avg_score = sum(g_scores) / len(g_scores) if g_scores else 0.0
        print(f"{Fore.MAGENTA}Column: {col} - G-Eval Average: {avg_score:.4f}{Style.RESET_ALL}")