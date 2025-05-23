import json
import re

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.analysis_prompts import ABSTRACT_PROMPT, FACTS_PROMPT, PIL_PROVISIONS_PROMPT, COL_ISSUE_PROMPT, COURTS_POSITION_PROMPT
from schemas.appstate import AppState
from utils.themes_extractor import filter_themes_by_list


# ========== NODES ==========

# Helper function to extract content from the last message in a list of messages
def _get_last_message_content(messages: list | None) -> str:
    if messages and isinstance(messages, list) and messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content') and last_message.content is not None:
            return str(last_message.content)
    return ""

# Helper function to extract and format classification content
def _get_classification_content_str(messages: list | None) -> str:
    content_str = ""
    if messages and isinstance(messages, list) and messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content') and last_message.content is not None:
            raw_content = last_message.content
            if isinstance(raw_content, list):
                content_str = ", ".join(str(item) for item in raw_content if item) if any(raw_content) else ""
            elif isinstance(raw_content, str):
                content_str = raw_content
    return content_str

# ===== ABSTRACT =====
def abstract_node(state: AppState):
    print("\n--- ABSTRACT ---")
    text = state["full_text"]
    # ABSTRACT_PROMPT only needs {text}
    prompt = ABSTRACT_PROMPT.format(text=text)
    #print(f"\nPrompting LLM with:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    abstract = response.content
    print(f"\nAbstract:\n{abstract}\n")
    
    return {
        "abstract": [AIMessage(content=abstract)]
    }

# ===== RELEVANT FACTS =====
def facts_node(state: AppState):
    print("\n--- RELEVANT FACTS ---")
    text = state["full_text"]
    col_section_content = _get_last_message_content(state.get("col_section"))
    
    prompt = FACTS_PROMPT.format(text=text, col_section=col_section_content)
    #print(f"\nPrompting LLM with:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    facts = response.content
    print(f"\nRelevant Facts:\n{facts}\n")
    
    return {
        "relevant_facts": [AIMessage(content=facts)]
    }

# ===== PIL PROVISIONS =====
def pil_provisions_node(state: AppState):
    print("\n--- PIL PROVISIONS ---")
    text = state["full_text"]
    col_section_content = _get_last_message_content(state.get("col_section"))

    prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=col_section_content)
    #print(f"\nPrompting LLM with:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    try:
        pil_provisions = json.loads(response.content)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse PIL provisions as JSON. Content: {response.content}")
        pil_provisions = [response.content.strip()] # Fallback to list with raw content
        
    print(f"\nPIL Provisions:\n{pil_provisions}\n")
    
    return {
        "pil_provisions": [AIMessage(content=pil_provisions)]
    }

# ===== CHOICE OF LAW ISSUE =====
def col_issue_node(state: AppState):
    print("\n--- CHOICE OF LAW ISSUE ---")
    text = state["full_text"]
    col_section_content = _get_last_message_content(state.get("col_section"))
    # Extract the list of theme strings from the last classification AIMessage
    classification_messages = state.get("classification", [])
    themes_list: list[str] = []
    if classification_messages:
        last_msg = classification_messages[-1]
        if hasattr(last_msg, 'content'):
            content_value = last_msg.content
            if isinstance(content_value, list):
                themes_list = content_value
            elif isinstance(content_value, str) and content_value:
                themes_list = [content_value]
    # Filter definitions by the extracted theme names
    classification_definitions = filter_themes_by_list(themes_list)

    prompt = COL_ISSUE_PROMPT.format(
        text=text, 
        col_section=col_section_content, 
        classification_definitions=classification_definitions
    )
    print(f"\nPrompting LLM with:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    col_issue = response.content
    print(f"\nChoice of Law Issue:\n{col_issue}\n")
    
    return {
        "col_issue": [AIMessage(content=col_issue)]
    }

# ===== COURT'S POSITION =====
def courts_position_node(state: AppState):
    print("\n--- COURT'S POSITION ---")
    text = state["full_text"]
    col_section_content = _get_last_message_content(state.get("col_section"))
    classification_content = _get_classification_content_str(state.get("classification"))

    prompt = COURTS_POSITION_PROMPT.format(
        text=text, 
        col_section=col_section_content, 
        classification=classification_content
    )
    #print(f"\nPrompting LLM with:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    courts_position = response.content
    print(f"\nCourt's Position:\n{courts_position}\n")
    
    return {
        "courts_position": [AIMessage(content=courts_position)]
    }


# ========== GRAPH ==========

graph = StateGraph(AppState)

graph.add_node("abstract_node", abstract_node)
graph.add_node("facts_node", facts_node)
graph.add_node("pil_provisions_node", pil_provisions_node)
graph.add_node("col_issue_node", col_issue_node)
graph.add_node("courts_position_node", courts_position_node)

graph.set_entry_point("abstract_node")
graph.add_edge("abstract_node", "facts_node")
graph.add_edge("facts_node", "pil_provisions_node")
graph.add_edge("pil_provisions_node", "col_issue_node")
graph.add_edge("col_issue_node", "courts_position_node")
graph.add_edge("courts_position_node", END)

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
thread_config = {"configurable": {"thread_id": thread_id}}


# ========== RUNNER ==========

def run_analysis(state: AppState):
    current_state = state.copy()
    for chunk in app.stream(current_state, config=thread_config):
        # chunk will be like {"node_name": {"output_key": value}}
        # We update current_state with the output of the node that just ran
        for key, value in chunk.items():
            if key != "__end__": # LangGraph sometimes includes an "__end__" key
                if isinstance(value, dict): # Should be the output from our nodes
                    current_state.update(value)
                else:
                    # This case might occur if a node returns something other than a dict
                    print(f"Warning: Node {key} returned non-dict value: {value}")
    # After the stream is exhausted, all nodes have run in sequence.
    return current_state
