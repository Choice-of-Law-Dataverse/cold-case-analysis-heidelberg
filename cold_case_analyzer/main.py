import os
import pandas as pd
from datetime import datetime
from data_handler.airtable_retrieval import fetch_data
from data_handler.airtable_concepts import fetch_and_prepare_concepts
from data_handler.local_file_retrieval import fetch_local_data, fetch_local_concepts
from case_analyzer import CaseAnalyzer
from config import AIRTABLE_CD_TABLE
import questionary

def main_own_data(model_name):
    # Fetch data from file
    df = fetch_local_data()
    # Assuming fetch_concepts() is defined elsewhere; if not, replace with the proper function call
    concepts = fetch_local_concepts()  

    print("Now starting the analysis...")
    results = []

    # Analyze each case
    for i, (idx, text) in enumerate(df['Original text'].iteritems(), start=1):
        quote = df['Quote'].iloc[i-1]
        print(f"Now analyzing case {i}\n")
        analyzer = CaseAnalyzer(text, quote, model_name, concepts)
        analysis_results = analyzer.analyze()

        # Append results to the list
        results.append({
            "ID": df['ID'].iloc[idx],
            **analysis_results
        })

    results_df = pd.DataFrame(results)

    # Define output path with date, time, and model in filename
    output_folder = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f'case_analysis_results_{timestamp}_{model_name}.csv')

    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


def main_airtable(model_name):
    # Fetch data from Airtable
    df = fetch_data(AIRTABLE_CD_TABLE)
    concepts = fetch_and_prepare_data()

    # Filter out cases missing key information
    columns_to_check = ["Original text"]
    df = df.dropna(subset=columns_to_check)
    print("Length of df: ", len(df))
    
    print("Writing df as ground truths to storage")
    gt_output_folder = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(gt_output_folder, exist_ok=True)
    gt_output_file = os.path.join(gt_output_folder, 'ground_truths.csv')
    df.to_csv(gt_output_file, index=False)

    print("Now starting the analysis...")
    results = []

    # Analyze each case
    for i, (idx, text) in enumerate(df['Original text'].iteritems(), start=1):
        quote = df['Quote'].iloc[i-1]
        print(f"Now analyzing case {i}\n")
        analyzer = CaseAnalyzer(text, quote, model_name, concepts)
        analysis_results = analyzer.analyze()

        results.append({
            "ID": df['ID'].iloc[idx],
            **analysis_results
        })

    results_df = pd.DataFrame(results)

    output_folder = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f'case_analysis_results_{timestamp}_{model_name}.csv')

    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


def main():
    data_source = questionary.select(
        "Select your data source:",
        choices=["Own data", "Airtable"]
    ).ask()

    model_choice = questionary.select(
        "Select the model:",
        choices=["gpt-4o", "llama3.1"]
    ).ask()

    if data_source == "Own data":
        main_own_data(model_choice)
    elif data_source == "Airtable":
        main_airtable(model_choice)
    else:
        print("No valid option selected. Exiting.")


if __name__ == "__main__":
    main()
