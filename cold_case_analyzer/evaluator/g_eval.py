import os
from datetime import datetime
import pandas as pd
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from colorama import Fore, Style

def evaluate_g_eval(merged_df, columns_to_compare):
    """
    For each column in `columns_to_compare`, run a no‐reference G‐Eval for every case (row)
    individually, print each score, and save the detailed results to a CSV file.
    """
    print(f"\n{Fore.CYAN}========== G-EVAL EVALUATION (Detailed Per Case) =========={Style.RESET_ALL}\n")
    
    detailed_results = []
    original_texts = merged_df["Original text"].fillna("").tolist()
    
    # For each column you want to evaluate...
    for col in columns_to_compare:
        generated_texts = merged_df[f"{col}_gen"].fillna("").tolist()
        
        # Process each case individually.
        for idx, (orig, gen) in enumerate(zip(original_texts, generated_texts)):
            # Create a new GEval instance per test case so that the score is not cumulative.
            correctness_metric = GEval(
                name="Correctness",
                evaluation_steps=[
                    "Check whether the facts in the 'actual output' contradict any facts in the 'input'.",
                    "Penalize omissions of crucial details that appear in the 'input'.",
                    "Penalize vague or contradictory claims.",
                ],
                evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
            )
            test_case = LLMTestCase(
                input=orig,
                actual_output=gen
            )
            correctness_metric.measure(test_case)
            score_value = correctness_metric.score
            case_id = merged_df.iloc[idx]["ID"]
            print(f"Case {case_id} - Column '{col}': G-Eval Score: {score_value:.4f}")
            
            detailed_results.append({
                "ID": case_id,
                "Column": col,
                "G_Eval_Score": score_value
            })
    
    # Create output folder (e.g., within your data/evaluations folder).
    output_folder = os.path.join(os.path.dirname(__file__), "..", "data", "evaluations")
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f"geval_evaluation_detailed_{timestamp}.csv")
    
    # Save the detailed results to CSV.
    df_results = pd.DataFrame(detailed_results)
    df_results.to_csv(output_file, index=False)
    print(f"\nDetailed G-Eval evaluation results saved to: {output_file}\n")
