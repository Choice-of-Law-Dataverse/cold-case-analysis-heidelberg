import streamlit as st
import json

from utils.input_handler import set_input_func, streamlit_input
# Override builtins.input to use Streamlit UI
set_input_func(streamlit_input)

from subgraphs.col_extractor import run_col_section_extraction
from subgraphs.themes_classifier import run_theme_classification
from subgraphs.case_analyzer import run_analysis
from schemas.appstate import AppState
from utils.sample_cd import SAMPLE_COURT_DECISION

# Initial application state
initial_state: AppState = {
    "full_text": SAMPLE_COURT_DECISION,
    "col_section": [],
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
    "courts_position_evaluation": 101,
    # timing fields if required by schema
    "col_section_time": 0.0,
    "theme_classification_time": 0.0,
    "abstract_time": 0.0,
    "relevant_facts_time": 0.0,
    "pil_provisions_time": 0.0,
    "col_issue_time": 0.0,
    "courts_position_time": 0.0,
}

# Define the workflow
def run_cold_case_analysis(state: AppState) -> AppState:
    # 1. Choice-of-law section extraction
    state_col = run_col_section_extraction(state)
    # 2. Theme classification
    state_theme = run_theme_classification(state_col.values)
    # 3. Final case analysis
    result = run_analysis(state_theme.values)
    return result

st.title("Cold Case Analysis")
# Text area for the full decision text
full_text = st.text_area("Court decision text:", value=initial_state["full_text"], height=300)

# Update the state with user-provided text
initial_state["full_text"] = full_text

if st.button("Run analysis"):
    with st.spinner("Analyzing..."):
        output_state = run_cold_case_analysis(initial_state)
        st.success("Analysis complete")
        st.subheader("Final State")
        st.json(output_state)
