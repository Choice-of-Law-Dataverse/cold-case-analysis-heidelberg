from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from colorama import Fore, Style

def evaluate_g_eval(merged_df, columns_to_compare):
    """
    For each column in `columns_to_compare`, runs no-reference G-Eval by comparing 
    the generated text (`col + '_gen'`) to the original text (`merged_df['Original text']`).
    """

    print(f"\n{Fore.CYAN}========== G-EVAL EVALUATION =========={Style.RESET_ALL}\n")

    # Setup the metric once, reusing for all rows
    correctness_metric = GEval(
        name="Correctness",
        evaluation_steps=[
            "Check whether the facts in the 'actual output' contradict any facts in the 'input'.",
            "Penalize omissions of crucial details that appear in the 'input'.",
            "Penalize vague or contradictory claims.",
        ],
        # Using no-reference: only input + actual_output
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
    )

    for col in columns_to_compare:
        # We'll compare the model output to the original text (row by row)
        original_texts = merged_df["Original text"].fillna("").tolist()
        generated_texts = merged_df[f"{col}_gen"].fillna("").tolist()

        g_scores = []
        for orig, gen in zip(original_texts, generated_texts):
            test_case = LLMTestCase(
                input=orig,
                actual_output=gen
                # No expected_output since this is no-reference style
            )
            # Evaluate
            correctness_metric.measure(test_case)
            # correctness_metric.score is updated with each measure
            g_scores.append(correctness_metric.score)

        # Compute the average
        avg_score = sum(g_scores) / len(g_scores) if g_scores else 0.0
        print(f"{Fore.MAGENTA}Column: {col} - G-Eval Average: {avg_score:.4f}{Style.RESET_ALL}")
