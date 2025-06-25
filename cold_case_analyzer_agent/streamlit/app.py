import streamlit as st
import csv
from pathlib import Path
from tools.col_extractor import extract_col_section
from utils.debug_print_state import print_state
from utils.sample_cd import SAMPLE_COURT_DECISION
import config
import json
import psycopg2
from tools.jurisdiction_detector import detect_jurisdiction

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

/* Sliders */
.stSlider {
    /* constrain slider width */
    max-width: 400px;
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
            if st.button("Extract COL Section", type="primary"):
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

# Sidebar with login and instructions
with st.sidebar:
    st.subheader("Login")
    # Display login form only if not logged in
    if not st.session_state.get("logged_in"):
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_button"):
            if credentials.get(username) == password:
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
                st.success(f"Logged in as {username}")
                st.rerun()
            else:
                st.error("Invalid username or password")
    # Display logout only when logged in
    else:
        st.write(f"Logged in as: {st.session_state['user']}")
        if st.button("Logout", key="logout_button"):
            st.session_state["logged_in"] = False
            st.session_state["user"] = ""
            st.success("Logged out")
            st.rerun()
    
    st.header("How to Use")
    st.markdown("""
    1. (Optional) Log in to access more advanced models
    2. Select the model you want to use
    3. Enter the case citation for the court decision
    4. Paste the full text of the court decision
    5. Click "Detect Jurisdiction" to classify the jurisdiction of the decision, evaluate its accuracy and optionally edit it
    6. Extract the Choice of Law section, evaluate it, and provide feedback
    7. Classify the court decision into themes, evaluate the classification, and edit if necessary
    8. Analyze the decision step-by-step, providing evaluations and edits as needed
    
    The analysis will include:
    - Abstract
    - Relevant Facts
    - Private International Law Provisions
    - Choice of Law Issue
    - Court's Position
                
    After evaluating and optionally editing the Court's Position, the analysis will be saved to a database. Note that results are only saved if you complete the analysis steps and click "Submit" at the end.
    You can clear the history at any time to start fresh.
    """)
    
    # Add a button to clear history
    if st.button("Clear History", key="clear_history"):
        # Remove analysis state to reset the interface
        for k in [
            'col_state', 'full_text_input',
            'jurisdiction', 'jurisdiction_detected', 'jurisdiction_eval_score',
            'jurisdiction_eval_submitted', 'jurisdiction_edit',
            'jurisdiction_edit_submitted', 'jurisdiction_confirmed']:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()