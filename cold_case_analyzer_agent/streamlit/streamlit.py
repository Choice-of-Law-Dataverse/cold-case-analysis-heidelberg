import streamlit as st
import json
from utils.input_handler import set_input_func, streamlit_input
from utils.output_handler import set_output_func, streamlit_output
from utils.debug_print_state import print_state

# wire up Streamlit I/O
set_input_func(streamlit_input)
set_output_func(streamlit_output)

from subgraphs.col_extractor import streamlit_col_extractor_runner
from utils.sample_cd import SAMPLE_COURT_DECISION

# init app_state once
if "app_state" not in st.session_state:
    st.session_state.app_state = {
        "full_text": SAMPLE_COURT_DECISION,
        "col_section": [],
        "col_section_feedback": [],
        "col_section_evaluation": 101,
        "user_approved_col": False,
        "col_section_time": 0.0,
    }

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
    streamlit_col_extractor_runner()
    # display current suggestion
    st.subheader("Extracted COL Section")
    col_list = []
    if "col_state" in st.session_state:
        col_list = [m.content for m in st.session_state.col_state.get("col_section", [])]
    st.json(col_list)
    # debug: dump session state
    print_state("UI session_state", dict(st.session_state))
# end of file