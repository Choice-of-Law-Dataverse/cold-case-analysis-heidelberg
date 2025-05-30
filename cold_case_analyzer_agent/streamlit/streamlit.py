import streamlit as st
import json
from utils.input_handler import set_input_func, streamlit_input
from utils.output_handler import set_output_func, streamlit_output

# Override builtins.input to use Streamlit UI
set_input_func(streamlit_input)
# route print() through Streamlit chat
set_output_func(streamlit_output)

from subgraphs.col_extractor import streamlit_col_extractor_runner
from subgraphs.themes_classifier import streamlit_theme_classification_runner
from subgraphs.case_analyzer import streamlit_case_analyzer_runner
from schemas.appstate import AppState
from utils.sample_cd import SAMPLE_COURT_DECISION

# Initialize session state
if "app_state" not in st.session_state:
    st.session_state["app_state"] = {
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

# no-arg runner wiring through session_state and Streamlit subgraph runners
def run_cold_case_analysis():
    # Extract COL section
    streamlit_col_extractor_runner()
    # Classify themes
    streamlit_theme_classification_runner()
    # Final analysis
    streamlit_case_analyzer_runner()
    return st.session_state["app_state"]

st.title("Cold Case Analysis")
# full text input bound to session_state
full_text = st.text_area(
    "Court decision text:",
    value=st.session_state["app_state"]["full_text"],
    key="full_text_input",
    height=300,
)
st.session_state["app_state"]["full_text"] = full_text

if st.button("Run analysis"):
    # clear previous runners
    for key in [
        "col_state",
        "coler",
        "waiting_for",
        "theme_state",
        "themeer",
        "theme_waiting_for",
        "analysis_state",
        "caser",
    ]:
        st.session_state.pop(key, None)
    with st.spinner("Analyzing…"):
        final_state = run_cold_case_analysis()
        st.session_state["app_state"] = final_state
        st.success("Analysis complete")
        st.subheader("Final State")
        st.json(final_state)

# chat log display
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
