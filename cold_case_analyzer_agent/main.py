import json

from subgraphs.col_extractor import run_col_section_extraction
from subgraphs.themes_classifier import run_theme_classification
from subgraphs.case_analyzer import run_analysis
from schemas.appstate import AppState
from config import thread_id
from utils.sample_cd import SAMPLE_COURT_DECISION

# run the subgraphs in the following order:
# 1. run_col_section_extraction
# 2. run_theme_classification
# 3. run_analysis
def run_cold_case_analysis(state: AppState):
    """
    Run the cold case analysis workflow.
    """
    # Run the subgraphs in order
    state_col_section = run_col_section_extraction(state)
    #print("\n--- STATE AFTER COL SECTION EXTRACTION ---")
    #print(json.dumps(state_col_section.values, indent=4, default=str))
    
    #print("\n--- FINAL COL SECTION ---")
    #print(state_col_section.values["col_section"][-1].content)
    
    state_theme_classification = run_theme_classification(state_col_section.values)
    #print("\n--- STATE AFTER THEME CLASSIFICATION ---")
    #if hasattr(state_theme_classification, 'values'):
        #print(json.dumps(state_theme_classification.values, indent=4, default=str))
    #else: # If it's already a dict (e.g., if run_theme_classification returns a dict directly)
        #print(json.dumps(state_theme_classification, indent=4, default=str))
    
    #print("\n--- FINAL CLASSIFICATION ---")
    #print(state_theme_classification.values["classification"][-1].content)

    state_final = run_analysis(state_theme_classification.values)

    return state_final

initial_state = {
    "full_text": SAMPLE_COURT_DECISION,
    "col_section": "",
    "col_section_feedback": [],
    "col_section_evaluation": 101,
    "user_approved_col": False,
    "classification": [],
    "theme_feedback": [],
    "theme_evaluation": 101,
    "user_approved_theme": False,
    "abstract": "",
    "abstract_evaluation": 101,
    "relevant_facts": "",
    "relevant_facts_evaluation": 101,
    "pil_provisions": "",
    "pil_provisions_evaluation": 101,
    "col_issue": "",
    "col_issue_evaluation": 101,
    "courts_position": "",
    "courts_position_evaluation": 101
}

if __name__ == "__main__":
    # Run the cold case analysis workflow
    final_state_result = run_cold_case_analysis(initial_state)
    print("\n--- FINAL STATE (PRETTY) ---")
    if final_state_result:
        print(json.dumps(final_state_result, indent=4, default=str))
    else:
        print("Workflow did not return a final state.")