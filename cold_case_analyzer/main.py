import os
import pandas as pd
from datetime import datetime
from data_handler.airtable_retrieval import fetch_data
from data_handler.airtable_concepts import fetch_and_prepare_data
from case_analyzer import CaseAnalyzer
from config import AIRTABLE_CD_TABLE

def main():
    # Fetch data from Airtable
    df = fetch_data(AIRTABLE_CD_TABLE)
    concepts = fetch_and_prepare_data()

    # Filter out cases missing key information
    columns_to_check = [
        "Relevant facts / Summary of the case", 
        "PIL provisions", 
        "Choice of law issue", 
        "Court's position"
    ]
    df = df.dropna(subset=columns_to_check)
    #df = df[0:2]
    print("Length of df: ", len(df))
    print("Now starting the analysis...")

    # Prepare to store analysis results
    results = []

    # Analyze each case
    i = 0
    model = "gpt-4o"  # other valid option: "llama3.1"
    for idx, text in enumerate(df['Content']):
        i += 1
        print(f"Now analyzing case {i}", "\n")
        analyzer = CaseAnalyzer(text, model, concepts)
        analysis_results = analyzer.analyze()
        
        # Append results to the list
        results.append({
            "ID": df['ID'].iloc[idx],
            **analysis_results
        })

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    # Define the output path with date, time, and model in filename
    output_folder = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f'case_analysis_results_{timestamp}_{model}.csv')

    # Save the DataFrame to CSV
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
