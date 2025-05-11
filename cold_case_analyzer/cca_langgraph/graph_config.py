from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict, Any
from langchain_openai import ChatOpenAI # Added for llm_instance typing

# Import node functions
from nodes.input_node import text_input_node
from nodes.col_extractor import col_extraction_node
from nodes.theme_classifier import theme_classification_node
from nodes.analysis_runner import (
    run_abstract_tool,
    run_relevant_facts_tool,
    run_pil_provisions_tool,
    run_col_issue_tool,
    run_courts_position_tool
)
from nodes.formatter import present_analysis_result_node
from nodes.interrupt_handler import (
    interrupt_for_col_validation,
    interrupt_for_theme_validation,
    interrupt_for_full_analysis_review
)

# Define schema based on documentation + tool outputs
class CourtAnalysisSchema(TypedDict):
    full_text: str              # Initial input
    quote: Optional[str]        # From col_section_tool
    themes_table: str           # Predefined themes table (string format for prompt)
    themes_table_data: Dict[str, str] # Parsed themes table for col_issue_tool definition lookup
    classification: Optional[List[str]] # From pil_theme_tool
    user_approved_col: Optional[bool]
    user_approved_theme: Optional[bool]
    # col_refinement_hints: Optional[str] # For future refinement loops
    abstract: Optional[str]
    relevant_facts: Optional[str]
    pil_provisions: Optional[List[str]]
    col_issue: Optional[str]
    courts_position: Optional[str]
    formatted_analysis: Optional[str]
    # For conditional routing after interrupts
    goto_node: Optional[str]
    # For final review loop (future enhancement)
    # refine_section: Optional[str]


def create_graph(llm_instance: ChatOpenAI):
    workflow = StateGraph(CourtAnalysisSchema)

    # Add nodes
    # Wrapping tool/logic nodes to pass llm_instance
    workflow.add_node("text_input_node", text_input_node)
    workflow.add_node("col_section_node", lambda state: col_extraction_node(state, llm_instance))
    workflow.add_node("ask_user_col_confirmation_node", interrupt_for_col_validation)
    workflow.add_node("pil_theme_node", lambda state: theme_classification_node(state, llm_instance))
    workflow.add_node("ask_user_theme_confirmation_node", interrupt_for_theme_validation)
    workflow.add_node("abstract_node", lambda state: run_abstract_tool(state, llm_instance))
    workflow.add_node("relevant_facts_node", lambda state: run_relevant_facts_tool(state, llm_instance))
    workflow.add_node("pil_provisions_node", lambda state: run_pil_provisions_tool(state, llm_instance))
    workflow.add_node("col_issue_node", lambda state: run_col_issue_tool(state, llm_instance))
    workflow.add_node("courts_position_node", lambda state: run_courts_position_tool(state, llm_instance))
    workflow.add_node("present_result_node", present_analysis_result_node)
    workflow.add_node("final_review_node", interrupt_for_full_analysis_review)


    # Define edges
    workflow.set_entry_point("text_input_node")
    workflow.add_edge("text_input_node", "col_section_node")
    workflow.add_edge("col_section_node", "ask_user_col_confirmation_node")

    # Conditional edge for CoL validation
    def after_col_validation_condition(state: CourtAnalysisSchema) -> str:
        if state.get("user_approved_col"):
            return "pil_theme_node" # Continue
        return "col_section_node" # Loop back to refine
    
    workflow.add_conditional_edges(
        "ask_user_col_confirmation_node",
        after_col_validation_condition,
        {
            "pil_theme_node": "pil_theme_node",
            "col_section_node": "col_section_node"
        }
    )

    workflow.add_edge("pil_theme_node", "ask_user_theme_confirmation_node")

    # Conditional edge for Theme validation
    def after_theme_validation_condition(state: CourtAnalysisSchema) -> str:
        if state.get("user_approved_theme"):
            return "abstract_node" # Continue
        return "pil_theme_node" # Loop back to refine

    workflow.add_conditional_edges(
        "ask_user_theme_confirmation_node",
        after_theme_validation_condition,
        {
            "abstract_node": "abstract_node",
            "pil_theme_node": "pil_theme_node"
        }
    )

    # Sequential analysis
    workflow.add_edge("abstract_node", "relevant_facts_node")
    workflow.add_edge("relevant_facts_node", "pil_provisions_node")
    workflow.add_edge("pil_provisions_node", "col_issue_node")
    workflow.add_edge("col_issue_node", "courts_position_node")
    workflow.add_edge("courts_position_node", "present_result_node")
    workflow.add_edge("present_result_node", "final_review_node") # Lead to final review

    # Final review node leads to END (or loops back for refinement in a more complex setup)
    workflow.add_edge("final_review_node", END)


    # Compile the graph
    app = workflow.compile()
    return app

# For testing the graph structure (optional)
if __name__ == '__main__':
    # This part won't run during import, only if graph_config.py is executed directly
    # You'd need a mock LLM or a real one to fully test compilation and drawing.
    # from langchain_openai import ChatOpenAI
    # mock_llm = ChatOpenAI(api_key="test", model="gpt-3.5-turbo") # Replace with your actual setup if testing
    # app = create_graph(mock_llm)
    # print("Graph compiled. Drawing ASCII diagram:")
    # app.get_graph().print_ascii()
    pass
