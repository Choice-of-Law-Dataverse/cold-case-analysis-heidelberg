import streamlit as st
import json
from utils.input_handler import INPUT_FUNC
from utils.output_handler import OUTPUT_FUNC
from utils.debug_print_state import print_state

from subgraphs.col_extractor import run_col_section_extraction, app as col_app, thread_config as col_thread_config
from langgraph.types import Command
from langgraph.graph import END
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

if "col_section_feedback" not in st.session_state.app_state:
    st.session_state.app_state["col_section_feedback"] = []

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
    # initialize stream and state containers
    st.session_state['col_stream'] = run_col_section_extraction(st.session_state.app_state)
    st.session_state['messages'] = []
    st.session_state['waiting_for_feedback'] = False
    st.session_state['interrupt_payload'] = None

if st.session_state.get("extract_started", False):
    # handle pending user feedback
    if st.session_state['waiting_for_feedback']:
        payload = st.session_state['interrupt_payload'] or {}
        prompt = payload.get('message', '')
        key_fb = f"col_fb_{st.session_state.app_state.get('col_section_eval_iter',1)}"
        user_fb = st.text_input(prompt, key=key_fb)
        if st.button("Submit feedback", key=f"col_submit_{st.session_state.app_state.get('col_section_eval_iter',1)}"):
            # resume graph with user input
            col_app.invoke(Command(resume=user_fb), config=col_thread_config)
            st.session_state['waiting_for_feedback'] = False
            st.rerun()
    else:
        # get next LangGraph chunk
        chunk = next(st.session_state['col_stream'], None)
        if chunk is None:
            st.write("Extraction complete.")
        elif 'col_section_node' in chunk:
            # node output: update state and append message
            state_u = chunk['col_section_node']
            st.session_state.app_state.update(state_u)
            for ai_msg in state_u.get('col_section', []):
                OUTPUT_FUNC(ai_msg.content, key=f"message_{len(st.session_state['messages'])}")
                st.session_state['messages'].append({'content': ai_msg.content})
            st.rerun()
        elif '__interrupt__' in chunk:
            # LLM interrupt: save payload and wait
            payload = chunk['__interrupt__'][0].value
            st.session_state['waiting_for_feedback'] = True
            st.session_state['interrupt_payload'] = payload
        elif 'col_section_feedback_node' in chunk:
            # feedback command: update state and finish or continue
            cmd = chunk['col_section_feedback_node']
            st.session_state.app_state.update(cmd.update)
            if cmd.goto == END:
                st.write("User approved. Extraction finished.")
            else:
                st.rerun()

    # render message history
    st.subheader("Extracted COL Section")
    for i, msg in enumerate(st.session_state.get('messages', [])):
        OUTPUT_FUNC(msg['content'], key=f"message_{i}")