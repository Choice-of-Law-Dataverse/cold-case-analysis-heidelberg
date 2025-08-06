import streamlit as st
import csv
from pathlib import Path
from tools.col_extractor import extract_col_section
from utils.debug_print_state import print_state
from utils.sample_cd import SAMPLE_COURT_DECISION
import config
import json
import psycopg2
from components.css import load_css
from components.sidebar import render_sidebar
from tools.jurisdiction_detector import detect_jurisdiction
from utils.pdf_handler import extract_text_from_pdf

# Database persistence helper
def save_to_db(state):
    """
    Persist the analysis state as JSON into PostgreSQL.
    """
    try:
        # Load Postgres credentials from Streamlit secrets
        creds = st.secrets["connections"]["postgresql"]
        with psycopg2.connect(
            host=creds.get("host"),
            port=creds.get("port", 5432),
            dbname=creds.get("database"),
            user=creds.get("user"),
            password=creds.get("password")
        ) as conn_pg:
            with conn_pg.cursor() as cur:
                # Ensure table and columns
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                cur.execute("ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS username TEXT;")
                cur.execute("ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS model TEXT;")
                cur.execute("ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS case_citation TEXT;")
                cur.execute("ALTER TABLE analysis_results ADD COLUMN IF NOT EXISTS data JSONB;")
                # Insert record with user, model, and citation
                cur.execute(
                    "INSERT INTO analysis_results(username, model, case_citation, data) VALUES (%s, %s, %s, %s)",
                    (
                        state.get("username"),
                        state.get("model"),
                        state.get("case_citation"),
                        json.dumps(state)
                    )
                )
            conn_pg.commit()
    except Exception as e:
        st.error(f"Failed to save results: {e}")

# Predefined user credentials (loaded from .env via config)
credentials = config.USER_CREDENTIALS
# Initialize login state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = ""
# Initialize jurisdiction detection state
if "jurisdiction" not in st.session_state:
    st.session_state["jurisdiction"] = None
if "jurisdiction_detected" not in st.session_state:
    st.session_state["jurisdiction_detected"] = False
if "jurisdiction_eval_score" not in st.session_state:
    st.session_state["jurisdiction_eval_score"] = None
if "jurisdiction_eval_submitted" not in st.session_state:
    st.session_state["jurisdiction_eval_submitted"] = False
if "jurisdiction_edit" not in st.session_state:
    st.session_state["jurisdiction_edit"] = None
if "jurisdiction_edit_submitted" not in st.session_state:
    st.session_state["jurisdiction_edit_submitted"] = False
if "jurisdiction_confirmed" not in st.session_state:
    st.session_state["jurisdiction_confirmed"] = False

# Load valid themes list immediately after imports
themes_csv = Path(__file__).parent / 'data' / 'themes.csv'
valid_themes = []
with open(themes_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        valid_themes.append(row['Theme'])

# Demo loader callback
def load_demo_case():
    # populate the text widget state (on_click will trigger rerun automatically)
    st.session_state.full_text_input = SAMPLE_COURT_DECISION

# Set page config
st.set_page_config(
    page_title="CoLD Case Analyzer",
    page_icon="https://choiceoflawdataverse.blob.core.windows.net/assets/favicon/favicon.ico",
    layout="wide"
)

# LLM model selection (single choice)
# Set available models based on authentication status
if st.session_state.get("logged_in"):
    model_options = ["gpt-4.1-nano", "o4-mini", "o3"]
else:
    model_options = ["gpt-4.1-nano"]
chosen_model = st.selectbox(
    "Select LLM Model:",
    model_options,
    index=0,
    key="llm_model_select"
)
config.llm = config.get_llm(chosen_model)

load_css()
render_sidebar()

# Title and description
st.title("CoLD Case Analyzer")
st.markdown("""
This tool helps you analyze court decisions and get structured summaries. 
You can provide feedback to improve the analysis until you're satisfied with the result.
""")

# Initialize state for COL section extraction
if 'col_state' not in st.session_state:
    st.session_state.col_state = {}


# ===== Phase 1 & 2: initial extraction and COL feedback =====

if not st.session_state.col_state.get("full_text"):
    # Case citation input stored in session state
    case_citation = st.text_input(
        "Case Citation:",
        key="case_citation",
        help="Enter the case citation for this decision"
    )
    # Ensure default session state for text input
    if "full_text_input" not in st.session_state:
        st.session_state.full_text_input = ""
    # PDF uploader and automatic extraction
    pdf_file = st.file_uploader(
        "Or drag and drop a PDF file here:",
        type=["pdf"],
        key="pdf_upload",
        help="Upload a PDF to extract the full text automatically"
    )
    if pdf_file is not None:
        try:
            extracted = extract_text_from_pdf(pdf_file)
            st.session_state.full_text_input = extracted
            st.success("Extracted text from PDF successfully.")
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {e}")
    # Initial COL extraction input
    full_text = st.text_area(
        "Paste the court decision text here:",
        height=200,
        help="Enter the full text of the court decision to extract the Choice of Law section.",
        key="full_text_input"
    )

    # Place Detect Jurisdiction and Use Demo Case buttons on the same line
    button_col1, button_col2 = st.columns([2, 1])
    with button_col1:
        detect_clicked = st.button("Detect Jurisdiction", key="detect_jurisdiction_btn")
    with button_col2:
        demo_clicked = False
        if not full_text.strip():
            demo_clicked = st.button("Use Demo Case", on_click=load_demo_case, key="demo_button")

    if detect_clicked:
        if full_text.strip():
            detected = detect_jurisdiction(full_text)
            st.session_state["jurisdiction"] = detected
            st.session_state["jurisdiction_detected"] = True
            st.session_state["jurisdiction_eval_score"] = None
            st.session_state["jurisdiction_eval_submitted"] = False
            st.session_state["jurisdiction_edit"] = detected
            st.session_state["jurisdiction_edit_submitted"] = False
            st.session_state["jurisdiction_confirmed"] = False
            st.rerun()
        else:
            st.warning("Please enter the court decision text before detecting jurisdiction.")

    if st.session_state["jurisdiction_detected"]:
        st.markdown(f"**Detected Jurisdiction:** <span style='color:#6F4DFA'>{st.session_state['jurisdiction']}</span>", unsafe_allow_html=True)
        # Evaluation step
        if not st.session_state["jurisdiction_eval_submitted"]:
            score = st.slider(
                "How accurate is this jurisdiction detection? (0-100)",
                min_value=0, max_value=100, value=100, step=1, key="jurisdiction_eval_slider"
            )
            if st.button("Submit Jurisdiction Evaluation", key="submit_jurisdiction_eval"):
                st.session_state["jurisdiction_eval_score"] = score
                st.session_state["jurisdiction_eval_submitted"] = True
                st.rerun()
        else:
            st.markdown(f"**Your evaluation score:** <span class='user-message'>Score: {st.session_state['jurisdiction_eval_score']}</span>", unsafe_allow_html=True)
        # Edit step
        if st.session_state["jurisdiction_eval_submitted"] and not st.session_state["jurisdiction_edit_submitted"]:
            edited = st.selectbox(
                "Edit or confirm the jurisdiction classification:",
                ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"],
                index=["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"].index(st.session_state["jurisdiction"]),
                key="jurisdiction_edit_select"
            )
            if st.button("Confirm Jurisdiction", key="confirm_jurisdiction_edit"):
                st.session_state["jurisdiction_edit"] = edited
                st.session_state["jurisdiction_edit_submitted"] = True
                st.session_state["jurisdiction_confirmed"] = True
                st.rerun()
        elif st.session_state["jurisdiction_edit_submitted"]:
            st.markdown(f"**Final Jurisdiction:** <span style='color:#6F4DFA'>{st.session_state['jurisdiction_edit']}</span>", unsafe_allow_html=True)

    # Only allow COL extraction after jurisdiction confirmed
    if st.session_state["jurisdiction_edit_submitted"]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Extract Choice of Law Section", type="primary"):
                if full_text:
                    # carry over case citation into analysis state
                    state = {
                        "case_citation": st.session_state.get("case_citation"),
                        "username": st.session_state.get("user"),
                        "model": st.session_state.get("llm_model_select"),
                        "full_text": full_text,
                        "col_section": [],
                        "col_section_feedback": [],
                        "col_section_eval_iter": 0,
                        "jurisdiction": st.session_state["jurisdiction_edit"]
                    }
                    result = extract_col_section(state)
                    state.update(result)
                    st.session_state.col_state = state
                    st.rerun()
                else:
                    st.warning("Please enter a court decision to analyze.")
else:
    # Display the case citation and full court decision text
    citation = st.session_state.col_state.get("case_citation")
    if citation:
        st.markdown("**Case Citation:**")
        st.markdown(f"<div class='user-message'>{citation}</div>", unsafe_allow_html=True)
    # Display the full court decision text at the top as a user message
    st.markdown("**Your Input (Court Decision Text):**")
    st.markdown(f"<div class='user-message'>{st.session_state.col_state['full_text']}</div>", unsafe_allow_html=True)
    # Always show COL extraction history
    extractions = st.session_state.col_state.get("col_section", [])
    feedbacks = st.session_state.col_state.get("col_section_feedback", [])
    for i, col in enumerate(extractions):
        # show all extractions as machine messages, but if final edited extraction has been submitted, show it as a user message
        if i == len(extractions) - 1 and st.session_state.col_state.get("col_done"):
            st.markdown("**Your Edited Choice of Law Section:**")
            st.markdown(f"<div class='user-message'>{col}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Choice of Law Section Extraction {i+1}:**")
            st.markdown(f"<div class='machine-message'>{col}</div>", unsafe_allow_html=True)
        if i == 0:
            # One-time score input for extraction 1
            if not st.session_state.col_state.get("col_first_score_submitted"):
                # Score input restricted to 0–100
                score_input = st.slider(
                    "Evaluate this first extraction (0-100):",
                    min_value=0,
                    max_value=100,
                    value=100,
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
    
    # Once COL is done, show a single theme classification and evaluation
    if st.session_state.col_state.get("col_done"):
        state = st.session_state.col_state
        # Show machine classification once
        themes = state.get("classification", [])
        if themes:
            last_theme = themes[-1]
            st.markdown("**Themes:**")
            st.markdown(f"<div class='machine-message'>{last_theme}</div>", unsafe_allow_html=True)
        # First-time scoring
        if not state.get("theme_first_score_submitted"):
            score = st.slider(
                "Evaluate these themes (0-100):",
                min_value=0,
                max_value=100,
                value=100,
                step=1,
                key="theme_first_score_input"
            )
            if st.button("Submit Theme Score", key="submit_theme_score"):
                state["theme_first_score"] = score
                state["theme_first_score_submitted"] = True
                st.rerun()
        else:
            sc = state.get("theme_first_score", 0)
            st.markdown("**Your score for themes:**")
            st.markdown(f"<div class='user-message'>Score: {sc}</div>", unsafe_allow_html=True)
            # Allow editing via multiselect
            if not state.get("theme_done"):
                default_sel = [t.strip() for t in last_theme.split(",") if t.strip()]
                selected = st.multiselect(
                    "Adjust themes:",
                    options=valid_themes,
                    default=default_sel,
                    key="theme_select"
                )
                if st.button("Submit Final Themes"):
                    if selected:
                        new_sel = ", ".join(selected)
                        state.setdefault("classification", []).append(new_sel)
                        state["theme_done"] = True
                        state["analysis_ready"] = True
                        state["analysis_step"] = 0
                        st.rerun()
                    else:
                        st.warning("Select at least one theme before proceeding.")
        # Display user’s final edited classification
        if state.get("theme_done"):
            final = state.get("classification", [])[-1]
            st.markdown("**Final Themes:**")
            st.markdown(f"<div class='user-message'>{final}</div>", unsafe_allow_html=True)
    
    # Once themes are done, trigger analysis phase
    # Prepare state reference
    state = st.session_state.col_state

    # Sequential analysis steps
    if state.get("analysis_ready"):
        # display chronological chat history of analysis
        for speaker, msg in state.get("chat_history", []):
            if speaker == 'machine':
                # Separate step label and content if formatted as 'Step: content'
                if ': ' in msg:
                    step_label, content = msg.split(': ', 1)
                    # display step label in bold
                    st.markdown(f"**{step_label}**")
                    # display content as machine message
                    st.markdown(f"<div class='machine-message'>{content}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='machine-message'>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='user-message'>{msg}</div>", unsafe_allow_html=True)
        # Show final thank-you message after last analysis step
        if state.get("analysis_done"):
            print("\n\n\nAnalysis completed, saving state to database...\n\n")
            save_to_db(state)
            st.markdown(
                "<div class='machine-message'>Thank you for using the CoLD Case Analyzer.<br>If you would like to find out more about the project, please visit <a href=\"https://cold.global\" target=\"_blank\">cold.global</a></div>",
                unsafe_allow_html=True
            )
        else:
            from tools.case_analyzer import (
                abstract, relevant_facts,
                pil_provisions, col_issue,
                courts_position
            )
            steps = [
                ("abstract", abstract),
                ("relevant_facts", relevant_facts),
                ("pil_provisions", pil_provisions),
                ("col_issue", col_issue),
                ("courts_position", courts_position)
            ]
            name, func = steps[state["analysis_step"]]
            # run node once, record machine output
            if not state.get(f"{name}_printed"):
                result = func(state)
                state.update(result)
                # append machine message to history
                out = state.get(name)
                last = out[-1] if isinstance(out, list) else out
                # display analysis step label
                st.markdown(f"**{name.replace('_',' ').title()}**")
                # use st.markdown to display the analysis content
                st.markdown(f"<div class='machine-message'>{last}</div>", unsafe_allow_html=True)
                state.setdefault("chat_history", []).append(("machine", f"{name.replace('_',' ').title()}: {last}"))
                state[f"{name}_printed"] = True
                st.rerun()
            # one-time scoring for this step
            score_key = f"{name}_score_submitted"
            if not state.get(score_key):
                # Score input restricted to 0–100
                score = st.slider(
                    f"Evaluate this {name.replace('_',' ')} (0-100):",
                    min_value=0,
                    max_value=100,
                    value=100,
                    step=1,
                    key=f"{name}_score_input"
                )
                if st.button(f"Submit {name.replace('_',' ').title()} Score", key=f"submit_{name}_score"):
                    # record user score and add to history
                    state[f"{name}_score"] = score
                    state[score_key] = True
                    state.setdefault("chat_history", []).append(("user", f"Score for {name.replace('_',' ').title()}: {score}"))
                    st.rerun()
            # determine last output for default in edit area
            content = state.get(name)
            last = content[-1] if isinstance(content, list) else content
            # editable correction after score submission
            edit_key = f"{name}_edited"
            if state.get(score_key):
                edited = st.text_area(
                    f"Edit {name.replace('_',' ')}:",
                    value=state.get(edit_key, last),
                    height=200,
                    key=f"{name}_edit_area"
                )
                if st.button(f"Submit Edited {name.replace('_',' ').title()}", key=f"submit_edited_{name}"):
                    # record user edit and advance to next step
                    state[name][-1] = edited
                    state[edit_key] = edited
                    state.setdefault("chat_history", []).append(("user", edited))
                    if state["analysis_step"] < len(steps)-1:
                        state["analysis_step"] += 1
                    else:
                        state["analysis_done"] = True
                    print_state("\n\n\nUpdated CoLD State after analysis step\n\n", st.session_state.col_state)
                    st.rerun()

render_sidebar()