# components/main_workflow.py
"""
Main workflow orchestrator for the CoLD Case Analyzer.
"""
import streamlit as st
from tools.col_extractor import extract_col_section
from components.jurisdiction_detection import render_jurisdiction_detection, get_final_jurisdiction_data
from components.input_handler import render_input_phase
from components.col_processor import render_col_processing
from components.theme_classifier import render_theme_classification
from components.analysis_workflow import render_analysis_workflow
from utils.state_manager import create_initial_analysis_state, get_col_state, update_col_state


def render_initial_input_phase():
    """
    Render the initial input phase before any processing has begun.
    
    Returns:
        bool: True if ready to proceed to COL extraction, False otherwise
    """
    # Render input components
    case_citation, full_text = render_input_phase()
    
    if not full_text.strip():
        return False
    
    # Enhanced Jurisdiction Detection
    st.markdown("## Jurisdiction Identification")
    st.markdown("The first step consists of identifying the precise jurisdiction and legal system type from the court decision.")
    
    jurisdiction_confirmed = render_jurisdiction_detection(full_text)
    
    # Only allow COL extraction after jurisdiction confirmed
    if jurisdiction_confirmed:
        st.markdown("## Choice of Law Analysis")
        
        if st.button("Extract Choice of Law Section", type="primary", key="extract_col_btn"):
            if full_text:
                # Get final jurisdiction data
                final_jurisdiction_data = get_final_jurisdiction_data()
                
                # Create initial analysis state
                state = create_initial_analysis_state(
                    case_citation=st.session_state.get("case_citation"),
                    username=st.session_state.get("user"),
                    model=st.session_state.get("llm_model_select"),
                    full_text=full_text,
                    final_jurisdiction_data=final_jurisdiction_data
                )
                
                # Extract COL section
                result = extract_col_section(state)
                state.update(result)
                
                # Update session state
                st.session_state.col_state = state
                st.rerun()
            else:
                st.warning("Please enter a court decision to analyze.")
    
    return False


def render_processing_phases():
    """Render the COL processing, theme classification, and analysis phases."""
    col_state = get_col_state()
    
    # COL processing phase
    render_col_processing(col_state)
    
    # Theme classification phase
    render_theme_classification(col_state)
    
    # Analysis workflow phase
    render_analysis_workflow(col_state)


def render_main_workflow():
    """Render the complete main workflow."""
    if not get_col_state().get("full_text"):
        render_initial_input_phase()
    else:
        render_processing_phases()
