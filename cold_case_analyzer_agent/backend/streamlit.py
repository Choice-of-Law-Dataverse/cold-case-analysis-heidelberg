import streamlit as st
import json

from subgraphs.col_extractor import run_col_section_extraction
from subgraphs.themes_classifier import run_theme_classification
from subgraphs.case_analyzer import run_analysis
from utils.sample_cd import SAMPLE_COURT_DECISION

# Streamlit prototype for Cold Case Analyzer Agent

def main():
    st.title("Cold Case Analyzer Agent")

    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'input_fulltext'
        st.session_state.state = {
            "full_text": "",
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
            "courts_position_evaluation": 101
        }

    # Stage: Input full text
    if st.session_state.stage == 'input_fulltext':
        st.subheader("1. Upload Court Decision Text")
        full_text = st.text_area(
            "Paste the full text of the court decision below:",
            height=300,
            value=SAMPLE_COURT_DECISION
        )
        if st.button("Start Analysis"):
            # Save full text and run initial COL section extraction
            st.session_state.state["full_text"] = full_text
            result = run_col_section_extraction(st.session_state.state)
            st.session_state.state = getattr(result, 'values', result)
            st.session_state.stage = 'col_section'
            return

    # Stage: COL section extraction with feedback loop
    elif st.session_state.stage == 'col_section':
        st.subheader("2. Choice of Law Section Extraction")
        # Always run extraction to incorporate any new feedback
        result = run_col_section_extraction(st.session_state.state)
        st.session_state.state = getattr(result, 'values', result)

        # Display latest COL section
        latest = st.session_state.state["col_section"][-1].content
        st.write(latest)
        feedback = st.text_area(
            "Provide feedback or type 'continue' to approve section:", height=150,
            key='col_feedback'
        )
        if st.button("Submit COL Feedback"):
            if feedback.strip().lower() == 'continue':
                st.session_state.state["user_approved_col"] = True
                st.session_state.stage = 'theme_classification'
            else:
                st.session_state.state["col_section_feedback"].append(feedback)
                result = run_col_section_extraction(st.session_state.state)
                st.session_state.state = getattr(result, 'values', result)
            return

    # Stage: Theme classification with feedback loop
    elif st.session_state.stage == 'theme_classification':
        st.subheader("3. Theme Classification")
        # Run classification if first time or after feedback
        if not st.session_state.state["classification"]:
            result = run_theme_classification(st.session_state.state)
            st.session_state.state = getattr(result, 'values', result)

        latest = st.session_state.state["classification"][-1].content
        st.write(latest)
        feedback = st.text_area(
            "Provide feedback or type 'continue' to approve themes:",
            height=150,
            key='theme_feedback'
        )
        if st.button("Submit Theme Feedback"):
            if feedback.strip().lower() == 'continue':
                st.session_state.state["user_approved_theme"] = True
                st.session_state.stage = 'final_analysis'
            else:
                st.session_state.state["theme_feedback"].append(feedback)
                result = run_theme_classification(st.session_state.state)
                st.session_state.state = getattr(result, 'values', result)
            return

    # Stage: Final analysis and display results
    elif st.session_state.stage == 'final_analysis':
        st.subheader("4. Final Analysis Results")
        result = run_analysis(st.session_state.state)
        st.session_state.state = getattr(result, 'values', result)

        st.markdown("### Abstract")
        st.write(st.session_state.state.get("abstract", ""))
        st.markdown("### Relevant Facts")
        st.write(st.session_state.state.get("relevant_facts", ""))
        st.markdown("### PIL Provisions")
        st.write(st.session_state.state.get("pil_provisions", ""))
        st.markdown("### Choice of Law Issue")
        st.write(st.session_state.state.get("col_issue", ""))
        st.markdown("### Court's Position")
        st.write(st.session_state.state.get("courts_position", ""))

        if st.button("Restart Analysis"):
            for key in ['stage', 'state']:
                del st.session_state[key]
            return


if __name__ == "__main__":
    main()
