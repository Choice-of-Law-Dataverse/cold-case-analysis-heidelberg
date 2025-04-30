import os
from datetime import datetime
import pandas as pd
from bert_score import score
from colorama import Fore, Style

def evaluate_bertopic(merged_df, columns_to_compare):
    """
    For each column in `columns_to_compare`, compute BERTScore for every case (row) individually,
    print the detailed scores (precision, recall, F1), and store the results in a CSV file.
    """
    print(f"\n{Fore.CYAN}========== BERTScore EVALUATION (Detailed Per Case) =========={Style.RESET_ALL}\n")
    
    detailed_results = []
    
    for col in columns_to_compare:
        # Prepare lists for references (ground-truth) and candidates (generated) for this column.
        references = merged_df[f"{col}_gt"].fillna("").tolist()
        candidates = merged_df[f"{col}_gen"].fillna("").tolist()
        
        # Compute BERTScore in batch.
        P, R, F1 = score(candidates, references, lang="en", verbose=False)
        
        # Loop over each case, printing and storing individual scores.
        for idx, (p, r, f) in enumerate(zip(P, R, F1)):
            p_val = p.item()
            r_val = r.item()
            f_val = f.item()
            case_id = merged_df.iloc[idx]["ID"]
            print(f"Case {case_id} - Column '{col}': Precision: {p_val:.4f}, Recall: {r_val:.4f}, F1: {f_val:.4f}")
            
            detailed_results.append({
                "ID": case_id,
                "Column": col,
                "BERT_Precision": p_val,
                "BERT_Recall": r_val,
                "BERT_F1": f_val
            })
    
    # Create output folder (e.g., within your data/evaluations folder).
    output_folder = os.path.join(os.path.dirname(__file__), "..", "data", "evaluations")
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f"bertopic_evaluation_detailed_{timestamp}.csv")
    
    # Save the detailed results to CSV.
    df_results = pd.DataFrame(detailed_results)
    df_results.to_csv(output_file, index=False)
    print(f"\nDetailed BERTScore evaluation results saved to: {output_file}\n")
