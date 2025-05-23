"""
agent_graph.py
==============

LangGraph-based version of the Court Decision Analyzer agent.
- Analyzes and summarizes court decisions using specialized tools
- Allows for interactive feedback and improvements
- Maintains context of previous iterations
- Provides structured, clear summaries
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import Tool
from typing_extensions import TypedDict
from typing import Annotated

# Import analysis functions and prompt loader from the case_analyzer module
from case_analyzer import (
    extract_col_section,
    extract_abstract,
    extract_relevant_facts,
    extract_rules_of_law,
    extract_choice_of_law_issue,
    extract_courts_position,
    load_prompt,
)

# 1. Load environment
load_dotenv()

# 2. Initialize the model
model = init_chat_model("gpt-4o-mini", model_provider="openai")
concepts = []  # Placeholder for concepts

# 3. Define Tool Input Schemas (as in agent.py)
from pydantic import BaseModel, Field
class ExtractColSectionInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
class ExtractAbstractInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")
class ExtractRelevantFactsInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")
class ExtractRulesOfLawInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")
class ExtractChoiceOfLawIssueInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")
class ExtractCourtsPositionInput(BaseModel):
    text: str = Field(description="The full text of the court decision.")
    col_section: str = Field(description="The previously extracted Choice of Law section.")
    coli: str = Field(description="The previously extracted Choice of Law Issue.")

# 4. Define Tool Functions (Wrappers)
def run_extract_col_section(text: str) -> str:
    prompt = load_prompt("col_section.txt")
    return extract_col_section(text, prompt, model)
def run_extract_abstract(text: str, col_section: str) -> str:
    prompt = load_prompt("abstract.txt")
    return extract_abstract(text, col_section, prompt, model)
def run_extract_relevant_facts(text: str, col_section: str) -> str:
    prompt = load_prompt("facts.txt")
    return extract_relevant_facts(text, col_section, prompt, model)
def run_extract_rules_of_law(text: str, col_section: str) -> str:
    prompt = load_prompt("rules.txt")
    return extract_rules_of_law(text, col_section, prompt, model)
def run_extract_choice_of_law_issue(text: str, col_section: str) -> dict:
    classification_prompt = load_prompt("issue_classification.txt")
    issue_prompt = load_prompt("issue.txt")
    classification, choice_of_law_issue = extract_choice_of_law_issue(
        text, col_section, classification_prompt, issue_prompt, model, concepts
    )
    return {"theme": classification, "issue": choice_of_law_issue}
def run_extract_courts_position(text: str, col_section: str, coli: str) -> str:
    prompt = load_prompt("position.txt")
    return extract_courts_position(text, col_section, prompt, coli, model)

# 5. Create Langchain Tools
# (You can swap in a demo tool for debugging if needed)
tools = [
    Tool(
        name="ExtractChoiceOfLawSection",
        func=run_extract_col_section,
        description="Extracts the relevant Choice of Law (Private International Law) section from the full text of a court decision. This should usually be the first step.",
        args_schema=ExtractColSectionInput,
    ),
    Tool(
        name="ExtractAbstract",
        func=run_extract_abstract,
        description="Creates a concise abstract summarizing the key aspects of the court decision, based on the full text and the extracted Choice of Law section.",
        args_schema=ExtractAbstractInput,
    ),
    Tool(
        name="ExtractRelevantFacts",
        func=run_extract_relevant_facts,
        description="Extracts the relevant facts pertinent to the Choice of Law issue from the court decision, based on the full text and the extracted Choice of Law section.",
        args_schema=ExtractRelevantFactsInput,
    ),
    Tool(
        name="ExtractRulesOfLaw",
        func=run_extract_rules_of_law,
        description="Identifies and extracts the specific Private International Law provisions or legal rules applied or discussed in the Choice of Law section of the court decision.",
        args_schema=ExtractRulesOfLawInput,
    ),
    Tool(
        name="ExtractChoiceOfLawIssueAndTheme",
        func=run_extract_choice_of_law_issue,
        description="Determines the central Choice of Law issue presented in the case and classifies its primary theme, based on the full text and the extracted Choice of Law section. Returns both the theme and the issue.",
        args_schema=ExtractChoiceOfLawIssueInput,
    ),
    Tool(
        name="ExtractCourtsPosition",
        func=run_extract_courts_position,
        description="Extracts the court's final position, reasoning, or holding specifically regarding the identified Choice of Law Issue, based on the full text, the Choice of Law section, and the Choice of Law Issue.",
        args_schema=ExtractCourtsPositionInput,
    ),
]

# 6. System instructions
system_instructions = f"""
You are a Court Decision Analyser. Your role is to analyse court decisions focusing on Private International Law (Choice of Law) aspects and provide clear, structured summaries.

You have access to the following tools:
{[tool.name for tool in tools]}

Use these tools to gather the necessary information. Follow this workflow:
1.  Receive the full text of the court decision.
2.  Use `ExtractChoiceOfLawSection` to identify the relevant section(s) discussing Choice of Law.
3.  Use `ExtractChoiceOfLawIssueAndTheme` on the full text and the extracted section to find the core issue and its theme. Store the results (theme and issue).
4.  Use the other extraction tools (`ExtractAbstract`, `ExtractRelevantFacts`, `ExtractRulesOfLaw`, `ExtractCourtsPosition`) using the full text, the extracted Choice of Law section, and the identified Choice of Law Issue (for `ExtractCourtsPosition`) as needed.
5.  Synthesize the results from the tools into a final, structured response with the following sections:
    - Abstract
    - Choice of Law Section (Quote the extracted section)
    - Relevant Facts
    - Private International Law Provisions
    - Private International Law Theme (from ExtractChoiceOfLawIssueAndTheme)
    - Choice of Law Issue (from ExtractChoiceOfLawIssueAndTheme)
    - Court's Position

When receiving feedback:
1) Acknowledge the feedback.
2) Explain your changes, potentially by re-running specific tools or refining the synthesis.
3) Maintain legal accuracy.
4) Keep the summary concise and clear.
"""

# 7. LangGraph State and Graph
class CourtGraphState(TypedDict):
    messages: Annotated[list, add_messages]

memory = MemorySaver()

# Bind tools to the model
model_with_tools = model.bind_tools(tools)

def court_agent_node(state: CourtGraphState):
    """Node that runs the LLM with tools."""
    return {"messages": [model_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(CourtGraphState)
graph_builder.add_node("court_agent", court_agent_node)
graph_builder.add_node("tools", ToolNode(tools=tools))
graph_builder.add_conditional_edges(
    "court_agent", tools_condition
)
graph_builder.add_edge("tools", "court_agent")
graph_builder.set_entry_point("court_agent")

court_graph = graph_builder.compile(checkpointer=memory)

# 8. Analysis and improvement functions
def analyse_court_decision_graph(decision_text, thread_id="court-graph-001"):
    """
    Analyse a court decision using the LangGraph agent and its tools.
    """
    state = {"messages": [HumanMessage(content=decision_text)]}
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 3}
    response = court_graph.invoke(state, config=config)
    return response

def improve_summary_graph(feedback, thread_id="court-graph-001"):
    """
    Improve the summary based on user feedback using the LangGraph agent.
    """
    state = {"messages": [HumanMessage(content=feedback)]}
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 3}
    response = court_graph.invoke(state, config=config)
    return response

# 9. Example usage
def _demo():
    sample_decision = """
        Urteilskopf
        136 III 392
        58. Extrait de l'arrêt de la Ire Cour de droit civil dans la cause X. SA contre A. (recours en matière civile)
        4A_91/2010 du 29 juin 2010
        ... (truncated for brevity) ...
    """
    print("Using the following court decision text for analysis:")
    print(sample_decision)
    thread_id = "court-graph-test-002"
    print("--- Initial Analysis (LangGraph) ---")
    try:
        initial_response = analyse_court_decision_graph(sample_decision, thread_id=thread_id)
        if initial_response and "messages" in initial_response and initial_response["messages"]:
            last_message = initial_response["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(last_message.content)
            else:
                print("Agent did not return an AI message.")
        else:
            print("Invalid response format from agent.")
    except Exception as e:
        print(f"An error occurred during initial analysis: {e}")
        import traceback
        traceback.print_exc()
    print("\n--- Improving Summary (LangGraph) ---")
    demo_feedback = "Add more details about the court's position."
    try:
        improved_response = improve_summary_graph(demo_feedback, thread_id=thread_id)
        if improved_response and "messages" in improved_response and improved_response["messages"]:
            last_message = improved_response["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(last_message.content)
            else:
                print("Agent did not return an AI message.")
        else:
            print("Invalid response format from agent.")
    except Exception as e:
        print(f"An error occurred during improvement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    _demo()
