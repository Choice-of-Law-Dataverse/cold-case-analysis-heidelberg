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
    #print(state_col_section)
    print("\n--- FINAL COL SECTION ---")
    print(state_col_section.values["col_section"][-1].content)
    state_theme_classification = run_theme_classification(state_col_section.values)
    print("\n--- STATE AFTER THEME CLASSIFICATION ---")
    print(state_theme_classification)
    #state_final = run_analysis(state_theme_classification)
    # Return the final state
    #return state_final

initial_state = {
    "full_text": SAMPLE_COURT_DECISION,
    "col_section": "",
    "col_section_feedback": [],
    "user_approved_col": False,
    "classification": [],
    "theme_feedback": [],
    "user_approved_theme": False,
    "analysis": "",
    "analysis_feedback": [],
    "user_approved_analysis": False,
}

if __name__ == "__main__":
    # Run the cold case analysis workflow
    final_state = run_cold_case_analysis(initial_state)
    print("\n--- FINAL STATE ---")
    print(final_state)