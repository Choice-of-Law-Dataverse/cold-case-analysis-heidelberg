import streamlit as st
from tools.col_extractor import extract_col_section
from utils.debug_print_state import print_state
from utils.sample_cd import SAMPLE_COURT_DECISION

# Demo loader callback
def load_demo_case():
    # populate the text widget state (on_click will trigger rerun automatically)
    st.session_state.full_text_input = SAMPLE_COURT_DECISION

# Set page config
st.set_page_config(
    page_title="CoLD Case Analyser",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for chat styling
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* Base styles */
body {
    font-family: 'Inter', sans-serif;
    color: #0F0035 !important;
}

/* Typography */
h1 {
    font-size: 32px !important;
    font-weight: 700 !important;
    color: #0F0035 !important;
}

h2 {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #0F0035 !important;
}

h3 {
    font-size: 20px !important;
    font-weight: 400 !important;
    color: #0F0035 !important;
}

p {
    font-size: 14px !important;
    line-height: 28px !important;
    color: #0F0035 !important;
}

/* Message containers */
.message-container {
    display: flex;
    flex-direction: column;
    margin: 12px 0;
}

.message-header {
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    margin-bottom: 6px;
    color: #0F0035;
}

/* User messages */
.user-message {
    background-color: #f3f2fa;  /* cold-purple-fake-alpha */
    color: #0F0035;  /* cold-night */
    padding: 15px;
    border-radius: 0;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
    margin-right: 0;
    border: 1px solid #6F4DFA;  /* cold-purple */
    font-size: 14px !important;
    line-height: 28px !important;
}

/* Machine messages */
.machine-message {
    background-color: #FAFAFA;  /* cold-bg */
    color: #0F0035;  /* cold-night */
    padding: 15px;
    border-radius: 0;
    margin: 8px 0;
    max-width: 80%;
    margin-left: 0;
    margin-right: auto;
    border: 1px solid #E2E8F0;  /* cold-gray */
    font-size: 14px !important;
    line-height: 28px !important;
}

/* Input areas */
.stTextArea textarea {
    font-family: 'Inter', sans-serif;
    font-size: 14px !important;
    line-height: 28px !important;
    color: #0F0035 !important;
    caret-color: #0F0035 !important;
    border: 1px solid #E2E8F0 !important;  /* cold-gray */
    border-radius: 0 !important;
    padding: 12px !important;
    background-color: #FAFAFA; !important;
}

.stTextArea textarea:focus {
    border-color: #6F4DFA !important;  /* cold-purple */
    box-shadow: none !important;
}

/* Buttons */
.stButton button {
    font-family: 'Inter', sans-serif;
    font-size: 14px !important;
    font-weight: 400 !important;
    background-color: #6F4DFA !important;  /* cold-purple */
    color: white !important;
    border-radius: 0 !important;
    padding: 8px 16px !important;
    border: none !important;
    box-shadow: none !important;
}

.stButton button:hover {
    background-color: #5a3fd9 !important;  /* slightly darker cold-purple */
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FAFAFA !important;
    color: #0F0035 !important;
    border-right: 1px solid #E2E8F0 !important; /* optional, clean border */
}

/* Header */
header[data-testid="stHeader"] {
    background-color: white !important;
    /*border-bottom: 1px solid #E2E8F0 !important;   cold-gray */
}

/* Warnings */
.stWarning {
    background-color: #FFF0D9 !important;  /* cold-cream */
    border: 1px solid #FF9D00 !important;  /* label-legal-instrument */
    color: #0F0035 !important;  /* cold-night */
}

/* Main container */
.stApp {
    background-color: white !important;
}

/* Lists */
ul {
    list-style-type: disc;
    margin: 0 !important;
    padding: 0.5rem 0 1.5rem 1.5rem !important;
}

li {
    margin: 0 !important;
    color: #0F0035 !important;  /* cold-night */
}

li::marker {
    color: #0F0035 !important;  /* cold-night */
}

/* Links */
a {
    color: #6F4DFA !important;  /* cold-purple */
    text-decoration: none !important;
    font-weight: 400 !important;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("CoLD Case Analyser")
st.markdown("""
This tool helps you analyze court decisions and get structured summaries. 
You can provide feedback to improve the analysis until you're satisfied with the result.
""")

# Initialize state for COL section extraction
if 'col_state' not in st.session_state:
    st.session_state.col_state = {}


# ===== Phase 1 & 2: initial extraction and COL feedback =====

if not st.session_state.col_state.get("full_text"):
    # Ensure default session state for text input
    if "full_text_input" not in st.session_state:
        st.session_state.full_text_input = ""
    # Initial COL extraction input
    full_text = st.text_area(
        "Paste the court decision text here:",
        height=200,
        help="Enter the full text of the court decision to extract the Choice of Law section.",
        key="full_text_input"
    )
    # Extraction and demo buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Extract COL Section", type="primary"):
            if full_text:
                state = {
                    "full_text": full_text,
                    "col_section": [],
                    "col_section_feedback": [],
                    "col_section_eval_iter": 0
                }
                result = extract_col_section(state)
                state.update(result)
                st.session_state.col_state = state
                st.rerun()
            else:
                st.warning("Please enter a court decision to analyze.")
    with col2:
        st.button("Use Demo Case", on_click=load_demo_case, key="demo_button")
else:
    # Display the full court decision text at the top as a user message
    st.markdown("**Your Input (Court Decision Text):**")
    st.markdown(f"<div class='user-message'>{st.session_state.col_state['full_text']}</div>", unsafe_allow_html=True)
    # Always show COL extraction history
    extractions = st.session_state.col_state.get("col_section", [])
    feedbacks = st.session_state.col_state.get("col_section_feedback", [])
    for i, col in enumerate(extractions):
        st.markdown(f"**Extraction {i+1}:**")
        st.markdown(f"<div class='machine-message'>{col}</div>", unsafe_allow_html=True)
        if i == 0:
            # One-time score input for extraction 1
            if not st.session_state.col_state.get("col_first_score_submitted"):
                # Score input restricted to 0–100
                score_input = st.number_input(
                    "Evaluate this first extraction (0-100):",
                    min_value=0,
                    max_value=100,
                    step=1,
                    help="Provide a score for the quality of the first extraction",
                    key="col_first_score_input"
                )
                if st.button("Submit Score", key="submit_col_score"):
                    st.session_state.col_state["col_first_score"] = score_input
                    st.session_state.col_state["col_first_score_submitted"] = True
                    st.rerun()
            else:
                score = st.session_state.col_state.get("col_first_score", 0)
                st.markdown("**Your score for extraction 1:**")
                st.markdown(f"<div class='user-message'>Score: {score}</div>", unsafe_allow_html=True)
        if i < len(feedbacks):
            st.markdown("**User:**")
            st.markdown(f"<div class='user-message'>{feedbacks[i]}</div>", unsafe_allow_html=True)
    
    # If still refining COL, manage feedback and editing flows
    if not st.session_state.col_state.get("col_done"):
        col_state = st.session_state.col_state
        # Step 1: feedback and proceed to edit
        if not col_state.get("col_ready_edit"):
            # Only allow feedback after initial score
            if not col_state.get("col_first_score_submitted"):
                st.info("Please submit the extraction score before providing feedback.")
            else:
                feedback = st.text_area(
                    "Enter feedback to improve COL section:",
                    height=150,
                    key="col_feedback",
                    help="Provide feedback to refine the extracted Choice of Law section."
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Submit Feedback", key="submit_col_feedback"):
                        if feedback:
                            col_state["col_section_feedback"].append(feedback)
                            result = extract_col_section(col_state)
                            col_state.update(result)
                            st.rerun()
                        else:
                            st.warning("Please enter feedback to improve the extraction.")
                with col2:
                    if st.button("Proceed to Edit Section", key="proceed_col_edit"):
                        col_state["col_ready_edit"] = True
                        st.rerun()
        # Step 2: show edit area and final classification
        else:
            last_extraction = col_state.get("col_section", [""])[-1]
            edited_extraction = st.text_area(
                "Edit extracted Choice of Law section:",
                value=last_extraction,
                height=200,
                key="col_edit_section",
                help="Modify the extracted section before proceeding to theme classification"
            )
            print_state("\n\n\nCurrent CoLD State\n\n", st.session_state.col_state)
            if st.button("Submit and Classify"):
                if edited_extraction:
                    # Save edited extraction and run classification
                    col_state["col_section"].append(edited_extraction)
                    col_state["col_done"] = True
                    col_state["classification"] = []
                    col_state["theme_feedback"] = []
                    col_state["theme_eval_iter"] = 0
                    from tools.themes_classifier import theme_classification_node
                    init_result = theme_classification_node(col_state)
                    col_state.update(init_result)
                    print_state("\n\n\nUpdated CoLD State after classification\n\n", st.session_state.col_state)
                    st.rerun()
                else:
                    st.warning("Please edit the extracted section before proceeding.")
    
    # Once COL is done, show theme classification section below
    if st.session_state.col_state.get("col_done"):
        from tools.themes_classifier import theme_classification_node
        state = st.session_state.col_state
        # Display past theme classifications and feedback
        classifications = state.get("classification", [])
        theme_feedbacks = state.get("theme_feedback", [])
        # Theme classification evaluation and refinement
        for j, cls in enumerate(classifications):
            st.markdown(f"**Classification {j+1}:**")
            st.markdown(f"<div class='machine-message'>{cls}</div>", unsafe_allow_html=True)
            # One-time score input for first classification
            if j == 0:
                if not state.get("theme_first_score_submitted"):
                    # Score input restricted to 0–100
                    score_in = st.number_input(
                        "Evaluate this first classification (0-100):",
                        min_value=0,
                        max_value=100,
                        step=1,
                        help="Provide a score for the quality of the first theme classification",
                        key="theme_first_score_input"
                    )
                    if st.button("Submit Classification Score", key="submit_theme_score"):
                        state["theme_first_score"] = score_in
                        state["theme_first_score_submitted"] = True
                        st.rerun()
                else:
                    sc = state.get("theme_first_score", 0)
                    st.markdown("**Your score for classification 1:**")
                    st.markdown(f"<div class='user-message'>Score: {sc}</div>", unsafe_allow_html=True)
            # show any existing user feedback
            if j < len(theme_feedbacks):
                st.markdown("**User:**")
                st.markdown(f"<div class='user-message'>{theme_feedbacks[j]}</div>", unsafe_allow_html=True)
        # If still refining theme, manage feedback and editing flows
        if not state.get("theme_done"):
            # Only allow feedback after initial score
            if not state.get("theme_first_score_submitted"):
                st.info("Please submit the classification score before providing feedback.")
            else:
                # Step 1: feedback and proceed to edit
                if not state.get("theme_ready_edit"):
                    theme_fb = st.text_area(
                        "Enter feedback to improve theme classification:",
                        height=150,
                        key="theme_feedback_step1",
                        help="Provide feedback to refine the theme classification."
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Submit Theme Feedback", key="submit_theme_feedback_step1"):
                            if theme_fb:
                                state["theme_feedback"].append(theme_fb)
                                result = theme_classification_node(state)
                                state.update(result)
                                st.rerun()
                            else:
                                st.warning("Please enter feedback to improve the theme classification.")
                    with c2:
                        if st.button("Proceed to Edit Theme"):
                            state["theme_ready_edit"] = True
                            st.rerun()
                # Step 2: show edit area and final classification
                else:
                    last_cls = state.get("classification", [""])[-1]
                    edited_cls = st.text_area(
                        "Edit theme classification:",
                        value=last_cls,
                        height=200,
                        key="theme_edit_section",
                        help="Modify the classification before rerunning"
                    )
                    if st.button("Submit and Classify Theme"):
                        if edited_cls:
                            state["classification"][-1] = edited_cls
                            # perform classification iteration
                            result = theme_classification_node(state)
                            state.update(result)
                            # reset edit flag for next loop
                            state.pop("theme_ready_edit", None)
                            st.rerun()
                        else:
                            st.warning("Please edit the classification before proceeding.")
        else:
            # If theme classification is done, show nothing or final summary
            pass
    
    # Once themes are done, trigger analysis phase
    # Prepare state reference
    state = st.session_state.col_state
    if state.get("theme_done") and not state.get("analysis_ready"):
        if st.button("Submit Themes and Start Analysis"):
            state["analysis_ready"] = True
            state["analysis_step"] = 0
            st.rerun()

    # Sequential analysis steps
    if state.get("analysis_ready"):
        from tools.case_analyzer import (
            abstract_node, facts_node,
            pil_provisions_node, col_issue_node,
            courts_position_node
        )
        steps = [
            ("abstract", abstract_node),
            ("relevant_facts", facts_node),
            ("pil_provisions", pil_provisions_node),
            ("col_issue", col_issue_node),
            ("courts_position", courts_position_node)
        ]
        name, func = steps[state["analysis_step"]]
        # run node if not yet in state
        if name not in state or not state.get(f"{name}"):
            result = func(state)
            state.update(result)
        # display last output
        content = state.get(name)
        last = content[-1] if isinstance(content, list) else content
        st.markdown(f"**{name.replace('_',' ').title()}:**")
        st.markdown(f"<div class='machine-message'>{last}</div>", unsafe_allow_html=True)
        # one-time scoring for this step
        score_key = f"{name}_score_submitted"
        if not state.get(score_key):
            # Score input restricted to 0–100
            score = st.number_input(
                f"Evaluate this {name.replace('_',' ')} (0-100):",
                min_value=0,
                max_value=100,
                step=1,
                key=f"{name}_score_input"
            )
            if st.button(f"Submit {name.replace('_',' ').title()} Score", key=f"submit_{name}_score"):
                state[f"{name}_score"] = score
                state[score_key] = True
                st.rerun()
        else:
            sc = state.get(f"{name}_score", 0)
            st.markdown(f"**Your score for {name.replace('_',' ')}:** {sc}")
        # editable correction
        edit_key = f"{name}_edited"
        if state.get(score_key):
            edited = st.text_area(
                f"Edit {name.replace('_',' ')}:",
                value=state.get(edit_key, last),
                height=200,
                key=f"{name}_edit_area"
            )
            if st.button(f"Submit Edited {name.replace('_',' ').title()}"):
                state[name][-1] = edited
                state[edit_key] = edited
                st.rerun()
        # proceed to next
        if state.get(score_key) and state.get(edit_key) is not None:
            if st.button("Next"):
                if state["analysis_step"] < len(steps)-1:
                    state["analysis_step"] += 1
                else:
                    state["analysis_done"] = True
                st.rerun()
    # ...existing code...

# Sidebar with instructions
with st.sidebar:
    st.header("How to Use")
    st.markdown("""
    1. **Input**: Paste the court decision text
    2. **Analyse**: Click the 'Analyse Decision' button
    3. **Review**: Check the initial analysis
    4. **Feedback**: Provide feedback to improve the analysis
    5. **Iterate**: Continue providing feedback until satisfied
    
    The analysis will include:
    - Abstract
    - Choice of Law Section
    - Relevant Facts
    - Private International Law Provisions
    - Private International Law Theme
    - Choice of Law Issue
    - Court's Position
    """)
    
    # Add a button to clear history
    if st.button("Clear History", key="clear_history"):
        # Remove analysis state to reset the interface
        for k in ['col_state', 'full_text_input']:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

# Debugging state printout
#print_state("Current CoLD State", st.session_state.col_state)