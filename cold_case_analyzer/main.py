import os
import pandas as pd
from data_handler.airtable_retrieval import fetch_data
from case_analyzer import CaseAnalyzer
from config import AIRTABLE_CD_TABLE

def main():
    # Fetch data from Airtable
    df = fetch_data(AIRTABLE_CD_TABLE)

    # Filter out cases missing key information
    columns_to_check = [
        "Relevant facts / Summary of the case", 
        "Relevant rules of law", 
        "Choice of law issue", 
        "Court's position"
    ]
    df = df.dropna(subset=columns_to_check)
    df = df[0:2]
    print("Length of df: ", len(df))

    # Prepare to store analysis results
    results = []

    # Analyze each case
    i = 0
    for idx, text in enumerate(df['Content']):
        i += 1
        print(f"Now analyzing case {i}", "\n")
        model = "gpt-4o" # other valid option: "llama3.1"
        analyzer = CaseAnalyzer(text, model)
        analysis_results = analyzer.analyze()
        
        # Append results to the list
        results.append({
            "ID": df['ID'].iloc[idx],
            **analysis_results
        })

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    # Define the output path
    output_folder = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, 'case_analysis_results.csv')

    # Save the DataFrame to CSV
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
