import streamlit as st
import json
from utils.input_handler import INPUT_FUNC
from utils.output_handler import OUTPUT_FUNC
from utils.debug_print_state import print_state

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
user_id = INPUT_FUNC("Identify yourself please:", key="user_id_input")
if user_id:
    st.session_state.user_id = user_id
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
    #for k in ["col_state", "coler", "waiting_for"]:
        #st.session_state.pop(k, None)

if st.session_state.get("extract_started", False):
    # 1) only invoke the runner when we're _not_ waiting for feedback
    if not st.session_state.get("waiting_for"):
        # reset chat history so OUTPUT_FUNC writes fresh messages
        st.session_state["messages"] = []
        # run until first interrupt or END, then capture the new app state
        new_state = run_col_section_extraction(st.session_state.app_state)
        st.session_state.app_state = new_state

    # 2) render whatever messages we have so far
    st.subheader("Extracted COL Section")
    for i, msg in enumerate(st.session_state.get("messages", [])):
        OUTPUT_FUNC(msg["content"], key=f"message_{i}")