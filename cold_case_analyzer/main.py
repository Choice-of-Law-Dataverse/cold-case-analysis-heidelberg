import os
from datetime import datetime
import pandas as pd
import questionary
from data_handler.airtable_retrieval import fetch_data
from data_handler.airtable_concepts import fetch_and_prepare_concepts
from data_handler.local_file_retrieval import fetch_local_data, fetch_local_concepts
from case_analyzer import CaseAnalyzer
from evaluator import evaluate_results
from config import AIRTABLE_CD_TABLE


def main_own_data(model_name):
    
    df = fetch_local_data()
    concepts = fetch_local_concepts()

    print("Now starting the analysis...")
    results = []

    # Analyze each case
    for i, (idx, text) in enumerate(df["Original text"].items(), start=1):
        quote = df["Quote"].iloc[i - 1]
        print(f"Now analyzing case {i}\n")
        analyzer = CaseAnalyzer(text, quote, model_name, concepts)
        analysis_results = analyzer.analyze()

        # Append results to the list
        results.append({"ID": df["ID"].iloc[idx], **analysis_results})

    results_df = pd.DataFrame(results)

    # Define output path with date, time, and model in filename
    output_folder = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(
        output_folder, f"case_analysis_results_{timestamp}_{model_name}.csv"
    )

    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

    #print("Skipped all generation and using data from a previous iteration.")
    #output_file = "cold_case_analyzer/data/case_analysis_results_20250206_121810_gpt-4o.csv"
    #output_file = "cold_case_analyzer/data/case_analysis_results_20250204_172632_gpt-4o.csv"
    should_evaluate = questionary.select("Would you like to evaluate the results now?", choices=["Yes", "No"]).ask()
    if should_evaluate == "Yes":
        evaluate_results(df, output_file)


def main_airtable(model_name):
    # Fetch data from Airtable
    df = fetch_data(AIRTABLE_CD_TABLE)
    df.to_csv('cold_case_analyzer/data/raw/input.csv', index=False)
    concepts = fetch_and_prepare_concepts()
    concepts.to_csv('cold_case_analyzer/data/raw/concepts.csv', index=False)

    # Filter out cases missing key information
    columns_to_check = ["Original text"]
    df = df.dropna(subset=columns_to_check)
    # keep only the first three rows of df
    df = df.iloc[0:3]
    print("Length of df: ", len(df))

    print("Writing df as ground truths to storage")
    gt_output_folder = os.path.join(os.path.dirname(__file__), "data", "raw")
    os.makedirs(gt_output_folder, exist_ok=True)
    gt_output_file = os.path.join(gt_output_folder, "ground_truths.csv")
    df.to_csv(gt_output_file, index=False)

    print("Now starting the analysis...")
    results = []

    # Analyze each case
    for idx, row in df.iterrows():
        text = row['Original text']
        quote = row['Quote']
        print(f"Now analyzing case {idx}\n")
        analyzer = CaseAnalyzer(text, quote, model_name, concepts)
        analysis_results = analyzer.analyze()

        results.append({"ID": row['ID'], **analysis_results})

    results_df = pd.DataFrame(results)

    output_folder = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(
        output_folder, f"case_analysis_results_{timestamp}_{model_name}.csv"
    )

    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
    
    should_evaluate = questionary.select("Would you like to evaluate the results now?", choices=["Yes", "No"]).ask()
    if should_evaluate == "Yes":
        evaluate_results(df, output_file)


def main():
    data_source = questionary.select(
        "Select your data source (for most use cases, you likely want to select 'Own data'):",
        choices=["Own data", "Airtable"],
    ).ask()

    model_choice = questionary.select(
        "Select the model:", choices=["gpt-4o", "gpt-4o-mini", "llama3.1"]
    ).ask()

    if data_source == "Own data":
        main_own_data(model_choice)
    elif data_source == "Airtable":
        main_airtable(model_choice)
    else:
        print("No valid option selected. Exiting.")


if __name__ == "__main__":
    main()
