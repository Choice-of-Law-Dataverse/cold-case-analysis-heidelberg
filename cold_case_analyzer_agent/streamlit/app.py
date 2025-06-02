import streamlit as st
from tools.col_extractor import extract_col_section
from utils.debug_print_state import print_state

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

# Initial extraction input or feedback loop
if not st.session_state.col_state.get("full_text"):
    full_text = st.text_area(
        "Paste the court decision text here:",
        height=200,
        help="Enter the full text of the court decision to extract the Choice of Law section."
    )
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
else:
    # Display all past extractions and feedback in chronological order
    extractions = st.session_state.col_state.get("col_section", [])
    feedbacks = st.session_state.col_state.get("col_section_feedback", [])
    for i, col in enumerate(extractions):
        #st.markdown(f"**Extraction {i+1}:**")
        st.markdown("**CoLD Case Analyzer:**")
        # machine-generated extraction
        st.markdown(f"<div class='machine-message'>{col}</div>", unsafe_allow_html=True)
        # corresponding user feedback if available
        if i < len(feedbacks):
            st.markdown("**User:**")
            st.markdown(f"<div class='user-message'>{feedbacks[i]}</div>", unsafe_allow_html=True)

    # Feedback input for improving extraction
    feedback = st.text_area(
        "Enter feedback to improve COL section extraction:",
        height=150,
        help="Provide feedback to refine the extracted Choice of Law section."
    )
    if st.button("Submit Feedback"):
        if feedback:
            st.session_state.col_state["col_section_feedback"].append(feedback)
            result = extract_col_section(st.session_state.col_state)
            st.session_state.col_state.update(result)
            st.rerun()
        else:
            st.warning("Please enter feedback to improve the extraction.")

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
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.session_state.current_thread_id = f"court-analysis-{st.session_state.current_thread_id.split('-')[-1]}"
        st.rerun()

# Debugging state printout
#print_state("Current CoLD State", st.session_state.col_state)