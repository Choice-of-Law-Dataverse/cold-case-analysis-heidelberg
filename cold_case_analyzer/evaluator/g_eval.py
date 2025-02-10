import os
from datetime import datetime
import pandas as pd
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from colorama import Fore, Style

def evaluate_g_eval(merged_df, columns_to_compare):
    """
    For each column in `columns_to_compare`, run three unique G-Eval evaluations per case,
    using specific metric configurations for that column. For instance, if there are 7 columns,
    then a total of 21 unique metrics will be evaluated. Detailed per-case results are printed
    and saved to a CSV file.
    """
    print(f"\n{Fore.CYAN}========== G-EVAL EVALUATION (Detailed Per Case for Multiple Unique Metrics) =========={Style.RESET_ALL}\n")
    
    detailed_results = []
    original_texts = merged_df["Original text"].fillna("").tolist()

    # Define unique metric configurations for each column.
    # Replace the placeholder evaluation steps and parameters with your specific details.
    column_metric_config = {
        "Col Section": [
            {
                "name": "Col Section - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Col Section - Metric 1",
                    "Placeholder: Step 2 for Col Section - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Col Section - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Col Section - Metric 2",
                    "Placeholder: Step 2 for Col Section - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Col Section - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Col Section - Metric 3",
                    "Placeholder: Step 2 for Col Section - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Abstract": [
            {
                "name": "Abstract - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Abstract - Metric 1",
                    "Placeholder: Step 2 for Abstract - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Abstract - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Abstract - Metric 2",
                    "Placeholder: Step 2 for Abstract - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Abstract - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Abstract - Metric 3",
                    "Placeholder: Step 2 for Abstract - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Relevant Facts": [
            {
                "name": "Relevant Facts - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Relevant Facts - Metric 1",
                    "Placeholder: Step 2 for Relevant Facts - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Relevant Facts - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Relevant Facts - Metric 2",
                    "Placeholder: Step 2 for Relevant Facts - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Relevant Facts - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Relevant Facts - Metric 3",
                    "Placeholder: Step 2 for Relevant Facts - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Rules of Law": [
            {
                "name": "Rules of Law - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Rules of Law - Metric 1",
                    "Placeholder: Step 2 for Rules of Law - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Rules of Law - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Rules of Law - Metric 2",
                    "Placeholder: Step 2 for Rules of Law - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Rules of Law - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Rules of Law - Metric 3",
                    "Placeholder: Step 2 for Rules of Law - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Choice of Law Issue Classification": [
            {
                "name": "Choice of Law Issue Classification - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Choice of Law Issue Classification - Metric 1",
                    "Placeholder: Step 2 for Choice of Law Issue Classification - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Choice of Law Issue Classification - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Choice of Law Issue Classification - Metric 2",
                    "Placeholder: Step 2 for Choice of Law Issue Classification - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Choice of Law Issue Classification - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Choice of Law Issue Classification - Metric 3",
                    "Placeholder: Step 2 for Choice of Law Issue Classification - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Choice of Law Issue": [
            {
                "name": "Choice of Law Issue - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Choice of Law Issue - Metric 1",
                    "Placeholder: Step 2 for Choice of Law Issue - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Choice of Law Issue - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Choice of Law Issue - Metric 2",
                    "Placeholder: Step 2 for Choice of Law Issue - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Choice of Law Issue - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Choice of Law Issue - Metric 3",
                    "Placeholder: Step 2 for Choice of Law Issue - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Court's Position": [
            {
                "name": "Court's Position - Metric 1",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Court's Position - Metric 1",
                    "Placeholder: Step 2 for Court's Position - Metric 1"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Court's Position - Metric 2",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Court's Position - Metric 2",
                    "Placeholder: Step 2 for Court's Position - Metric 2"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Court's Position - Metric 3",
                "evaluation_steps": [
                    "Placeholder: Step 1 for Court's Position - Metric 3",
                    "Placeholder: Step 2 for Court's Position - Metric 3"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
    }
    
    # Loop through each column defined in columns_to_compare.
    for col in columns_to_compare:
        if col not in column_metric_config:
            print(f"Warning: No metric configuration found for column '{col}'. Skipping.")
            continue

        generated_texts = merged_df[f"{col}_gen"].fillna("").tolist()
        
        # Process each case (row) in the dataset.
        for idx, (orig, gen) in enumerate(zip(original_texts, generated_texts)):
            case_id = merged_df.iloc[idx]["ID"]
            test_case = LLMTestCase(
                input=orig,
                actual_output=gen
            )
            # For each metric unique to the current column...
            for metric_config in column_metric_config[col]:
                # Create a new GEval instance for this metric.
                metric = GEval(
                    name=metric_config["name"],
                    evaluation_steps=metric_config["evaluation_steps"],
                    evaluation_params=metric_config["evaluation_params"]
                )
                metric.measure(test_case)
                score_value = metric.score
                print(f"Case {case_id} - Column '{col}' - {metric_config['name']} Score: {score_value:.4f}")
                
                detailed_results.append({
                    "ID": case_id,
                    "Column": col,
                    "Metric": metric_config["name"],
                    "G_Eval_Score": score_value
                })
    
    # Create an output folder for the evaluation results.
    output_folder = os.path.join(os.path.dirname(__file__), "..", "data", "evaluations")
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f"geval_evaluation_detailed_{timestamp}.csv")
    
    # Save all detailed evaluation results to a CSV file.
    df_results = pd.DataFrame(detailed_results)
    df_results.to_csv(output_file, index=False)
    print(f"\nDetailed G-Eval evaluation results saved to: {output_file}\n")
