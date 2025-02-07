from bert_score import score
from colorama import Fore, Style

def evaluate_bertopic(merged_df, columns_to_compare):
    """
    Computes BERTScore for each column in `columns_to_compare`.
    Expects that for each column `col`, merged_df has:
      - `col + '_gt'` for ground-truth text
      - `col + '_gen'` for model-generated text
    """

    print(f"\n{Fore.CYAN}========== BERTScore EVALUATION =========={Style.RESET_ALL}\n")

    all_precision = []
    all_recall = []
    all_f1 = []

    for col in columns_to_compare:
        # references = ground truth
        references = merged_df[f"{col}_gt"].fillna("").tolist()
        # candidates = generated answers
        candidates = merged_df[f"{col}_gen"].fillna("").tolist()

        # If your text is non-English, set lang='...' accordingly
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

    # Optionally, print an overall average
    if all_precision:
        print(f"{Fore.YELLOW}--- AVERAGE BERTScore (across all compared columns) ---{Style.RESET_ALL}")
        print(f"  Precision: {sum(all_precision)/len(all_precision):.4f}")
        print(f"  Recall:    {sum(all_recall)/len(all_recall):.4f}")
        print(f"  F1:        {sum(all_f1)/len(all_f1):.4f}\n")
