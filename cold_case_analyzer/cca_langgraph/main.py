import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from graph_config import create_graph, CourtAnalysisSchema

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

# Initialize the LLM
# Ensure your OPENAI_API_KEY is set in your .env file or environment
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# Predefined themes table (as a string for the prompt, and as a dict for logic)
# This should ideally be loaded from a config file or database in a real application
THEMES_TABLE_STR = """
| Keyword                 | Definition                                                                                                |
|-------------------------|-----------------------------------------------------------------------------------------------------------|
| Contractual Obligations | Issues related to the choice of law for contracts, including validity, interpretation, and performance.   |
| Non-Contractual         | Concerns torts, unjust enrichment, and other obligations not arising from a contract.                     |
| Property Rights         | Deals with jurisdiction and applicable law for disputes over movable and immovable property.              |
| Family Law              | Covers marriage, divorce, child custody, and other familial relationships across borders.                 |
| Corporate Law           | Involves the law applicable to companies, including incorporation, governance, and insolvency.            |
| Intellectual Property   | Addresses cross-border protection and enforcement of IP rights like patents, trademarks, and copyrights.  |
| Procedure & Enforcement | Relates to international jurisdiction, recognition of foreign judgments, and procedural aspects of CoL.   |
"""
THEMES_TABLE_DATA = {
    "Contractual Obligations": "Issues related to the choice of law for contracts, including validity, interpretation, and performance.",
    "Non-Contractual": "Concerns torts, unjust enrichment, and other obligations not arising from a contract.",
    "Property Rights": "Deals with jurisdiction and applicable law for disputes over movable and immovable property.",
    "Family Law": "Covers marriage, divorce, child custody, and other familial relationships across borders.",
    "Corporate Law": "Involves the law applicable to companies, including incorporation, governance, and insolvency.",
    "Intellectual Property": "Addresses cross-border protection and enforcement of IP rights like patents, trademarks, and copyrights.",
    "Procedure & Enforcement": "Relates to international jurisdiction, recognition of foreign judgments, and procedural aspects of CoL."
}

def run_analyzer():
    """Runs the Cold Case Analyzer agent."""
    # Create the graph
    # checkpointer = MemorySaver() # In-memory checkpointer for simplicity
    # app = create_graph(llm_instance=llm).with_checkpointer(checkpointer)
    app = create_graph(llm_instance=llm)

    print("Cold Case Analyzer Agent Initialized.")
    print("Graph (ASCII):")
    app.get_graph().print_ascii()

    # Example: Load a court decision (replace with actual loading mechanism)
    # For testing, using a placeholder text. In a real app, you'd get this from a file or UI.
    sample_court_decision_text = """
    Decision of the Supreme Court, Case No. 123/2024.
    Regarding a dispute between Company A (Swiss) and Company B (German) over a software licensing agreement.
    The agreement stated that Swiss law should apply. However, Company B argued that German consumer protection law was mandatory.
    The Choice of Law section explicitly states: 'The parties agree that this contract shall be governed by the laws of Switzerland, excluding its conflict of laws rules.'
    The lower court applied Swiss law. Company B appealed.
    The Supreme Court examined the PILA (Swiss Private International Law Act) and relevant EU regulations.
    The court found that while Swiss law was chosen, certain mandatory provisions of German law could apply if they serve a strong public interest.
    However, in this specific case, the commercial nature of the agreement and the sophistication of the parties led the court to uphold the choice of Swiss law.
    The court's position was that party autonomy in contractual choice of law is paramount unless overridden by exceptionally strong public policy considerations of another jurisdiction closely connected to the dispute.
    The main issue was whether mandatory provisions of a foreign law can override an explicit choice of law clause in a B2B contract under Swiss PIL.
    The abstract (Regeste) noted: Upholding party autonomy in choice of law for B2B software contracts.
    Relevant facts: B2B software license, Swiss and German companies, explicit choice of Swiss law.
    PIL Provisions: Art. 116 PILA, Rome I Regulation (indirectly considered for context).
    """

    initial_state: CourtAnalysisSchema = {
        "full_text": sample_court_decision_text,
        "quote": None,
        "themes_table": THEMES_TABLE_STR,
        "themes_table_data": THEMES_TABLE_DATA,
        "classification": None,
        "user_approved_col": None,
        "user_approved_theme": None,
        "abstract": None,
        "relevant_facts": None,
        "pil_provisions": None,
        "col_issue": None,
        "courts_position": None,
        "formatted_analysis": None,
        "goto_node": None,
    }

    # config = {"configurable": {"thread_id": "cold-case-thread-1"}}
    config = {} # No checkpointer used for now, so thread_id is not strictly necessary for basic invoke

    print("\n--- STARTING ANALYSIS ---")
    # Stream events to see the flow. Use .invoke for a single final result.
    # for event in app.stream(initial_state, config=config):
    #     for key, value in event.items():
    #         print(f"Node: {key}, Output: {value}")
    #     print("---")
    
    final_result = app.invoke(initial_state, config=config)
    print("\n--- ANALYSIS COMPLETE ---")
    print("Final State:", final_result)

    if final_result.get("formatted_analysis"):
        print("\n--- FINAL FORMATTED ANALYSIS (from final_result) ---")
        print(final_result["formatted_analysis"])
    else:
        print("Formatted analysis not found in the final result.")

if __name__ == "__main__":
    run_analyzer()
