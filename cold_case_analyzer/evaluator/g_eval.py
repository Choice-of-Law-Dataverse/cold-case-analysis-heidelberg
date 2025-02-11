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
                "name": "Col Section - Accuracy",
                "evaluation_steps": [
                    "Check whether the text contains only paragraphs relevant for private international law.",
                    "The paragraphs must justify the court's decision on the choice of law issue.",
                    "Penalize if the focus lies not on the methodological part of the court decision but instead the facts or contractual details of the case."   
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Col Section - Conciseness",
                "evaluation_steps": [
                    "The answer cannot consist of more than 3 paragraphs."
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Abstract": [
            {
                "name": "Abstract - Accuracy",
                "evaluation_steps": [
                    "Check whether the abstract contains all the information relevant for an abstract of a court decision.",
                    "The correct lanugage to describe all important aspects is essential."
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Abstract - Conciseness",
                "evaluation_steps": [
                    "Evaluate the ressourcefulness in the sense that the important information is condensed in a short paragraph.",
                    "The text must not unnecessarily elaborate on minor aspects."
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Relevant Facts": [
            {
                "name": "Relevant Facts - Accuracy",
                "evaluation_steps": [
                    "Check whether the relevant facts contains all the information relevant for the relevant facts of a court decision.",
                    "The correct lanugage to describe all important aspects is essential."
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Relevant Facts - Focus on PIL",
                "evaluation_steps": [
                    "Evaluate whether the case is described through a private international law lens"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Relevant Facts - Conciseness",
                "evaluation_steps": [
                    "Evaluate the ressourcefulness in the sense that the important information is condensed in a short paragraph.",
                    "The text must not unnecessarily elaborate on minor aspects.",
                    "The relevant facts must include the procedural history in a short manner."
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Rules of Law": [
            {
                "name": "Rules of Law - Adherence to Format",
                "evaluation_steps": [
                    "Check whether the text resembles a list in the format '[rule1, rule2, ...]'"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Rules of Law - Accuracy",
                "evaluation_steps": [
                    "Evaluate whether the list contains the relevant private international law provisions.",
                    "Are the provisions sorted in descending order by their relevance for the choice of law issue at hand?"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Choice of Law Issue Classification": [
            {
                "name": "Choice of Law Issue Classification - Accuracy",
                "evaluation_steps": [
                    "Does the answer contain only the name of themes separated by comma, if multiple themes were assigned?",
                    "Were the corresponding choice of law themes accurately identified?"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Choice of Law Issue": [
            {
                "name": "Choice of Law Issue - Correct Identification of CoLI",
                "evaluation_steps": [
                    "Was the choice of law issue correctly identifier?",
                    "Does the phrasing of the question use the correct language to precisely describe the issue?"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Choice of Law Issue - Precision of Phrasing",
                "evaluation_steps": [
                    "Was the choice of law issue phrased as a question?",
                    "Is the choice of law issue formally correct?"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
        ],
        "Court's Position": [
            {
                "name": "Court's Position - Answering CoLI",
                "evaluation_steps": [
                    "Does the court's position contain all the relevant information?",
                    "Does the court's position use the correct language to describe all important aspects?"
                ],
                "evaluation_params": [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            },
            {
                "name": "Court's Position - Conciseness",
                "evaluation_steps": [
                    "Evaluate the ressourcefulness in the sense that the important information is condensed in a short paragraph.",
                    "The text must not unnecessarily elaborate on minor aspects."
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
