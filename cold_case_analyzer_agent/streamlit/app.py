import streamlit as st

from subgraphs.col_extractor import run_col_section_extraction
from subgraphs.themes_classifier import run_theme_classification
from subgraphs.case_analyzer import run_analysis
from utils.sample_cd import SAMPLE_COURT_DECISION

# Streamlit interface for Cold Case Analyzer Agent

def initialize_state():
    return {
        "full_text": "",
        "col_section": [],
        "col_feedback": [],
        "user_approved_col": False,
        "classification": [],
        "theme_feedback": [],
        "user_approved_theme": False,
        # Final results
        "abstract": "",
        "relevant_facts": "",
        "pil_provisions": "",
        "col_issue": "",
        "courts_position": ""
    }


def main():
    st.set_page_config(page_title="Cold Case Analyzer", layout="wide")
    st.title("Cold Case Analyzer Agent")

    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'input_fulltext'
        st.session_state.state = initialize_state()

    # Stage: Input full text
    if st.session_state.stage == 'input_fulltext':
        st.subheader("1. Upload Court Decision Text")
        full_text = st.text_area(
            "Paste the full text of the court decision below:",
            height=300,
            value=SAMPLE_COURT_DECISION
        )
        if st.button("Start Analysis"):
            st.session_state.state['full_text'] = full_text
            st.session_state.stage = 'col_section'
            return

    # Stage: Choice of Law Extraction
    if st.session_state.stage == 'col_section':
        st.subheader("2. Choice of Law Section Extraction")
        # run extraction
        st.session_state.state = run_col_section_extraction(st.session_state.state)
        # display last section
        col_sec = st.session_state.state['col_section'][-1]
        st.markdown("**Extracted COL Section:**")
        st.write(col_sec)
        feedback = st.text_area(
            "Provide feedback or type 'continue' to approve section:",
            height=150,
            key='col_feedback'
        )
        if st.button("Submit COL Feedback"):
            if feedback.strip().lower() == 'continue':
                st.session_state.state['user_approved_col'] = True
                st.session_state.stage = 'theme_classification'
            else:
                st.session_state.state['col_feedback'].append(feedback)
            return

    # Stage: Theme Classification
    if st.session_state.stage == 'theme_classification':
        st.subheader("3. Theme Classification")
        # run classification
        st.session_state.state = run_theme_classification(st.session_state.state)
        theme = st.session_state.state['classification'][-1]
        st.markdown("**Classified Themes:**")
        st.write(theme)
        feedback = st.text_area(
            "Provide feedback or type 'continue' to approve themes:",
            height=150,
            key='theme_feedback'
        )
        if st.button("Submit Theme Feedback"):
            if feedback.strip().lower() == 'continue':
                st.session_state.state['user_approved_theme'] = True
                st.session_state.stage = 'final_analysis'
            else:
                st.session_state.state['theme_feedback'].append(feedback)
            return

    # Stage: Final Analysis
    if st.session_state.stage == 'final_analysis':
        st.subheader("4. Final Analysis Results")
        st.session_state.state = run_analysis(st.session_state.state)

        st.markdown("### Abstract")
        st.write(st.session_state.state['abstract'])
        st.markdown("### Relevant Facts")
        st.write(st.session_state.state['relevant_facts'])
        st.markdown("### PIL Provisions")
        st.write(st.session_state.state['pil_provisions'])
        st.markdown("### Choice of Law Issue")
        st.write(st.session_state.state['col_issue'])
        st.markdown("### Court's Position")
        st.write(st.session_state.state['courts_position'])

        if st.button("Restart"):
            for key in ['stage', 'state']:
                del st.session_state[key]
            return


if __name__ == '__main__':
    main()