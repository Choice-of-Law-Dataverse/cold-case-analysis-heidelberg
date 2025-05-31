import streamlit as st
import json
from utils.input_handler import set_input_func, streamlit_input
from utils.output_handler import set_output_func, streamlit_output
from utils.debug_print_state import print_state

# wire up Streamlit I/O
set_input_func(streamlit_input)
set_output_func(streamlit_output)

from subgraphs.col_extractor import run_col_section_extraction
from utils.sample_cd import SAMPLE_COURT_DECISION

# init session_state once
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

if "app_state" not in st.session_state:
    st.session_state.app_state = initial_state

print("UI session_state initialized with:", json.dumps(st.session_state.app_state, indent=4))

# UI: title & input
st.title("Choice‐of‐Law Section Extractor")
full_text = st.text_area(
    "Court decision text:",
    value=st.session_state.app_state["full_text"],
    key="full_text_input",
    height=300,
)
st.session_state.app_state["full_text"] = full_text

# start extraction when button pressed
if st.button("Extract COL Section"):
    st.session_state.extract_started = True
    # clear previous runner slots
    for k in ["col_state", "coler", "waiting_for"]:
        st.session_state.pop(k, None)

# if extraction has started, run one step on every rerun and show suggestion
if st.session_state.get("extract_started", False):
    # run a single step of the extractor
    run_col_section_extraction(st.session_state.app_state)
    # display current suggestion
    st.subheader("Extracted COL Section")
    col_list = []
    if "col_state" in st.session_state:
        col_list = [m.content for m in st.session_state.col_state.get("col_section", [])]
    st.json(col_list)
    # debug: dump session state
    print_state("UI session_state", dict(st.session_state))
# end of file