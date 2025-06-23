import json
import re
import time
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import llm
from prompts.prompt_selector import get_prompt_module
from utils.themes_extractor import filter_themes_by_list


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
def abstract(state):
    print("\n--- ABSTRACT ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    ABSTRACT_PROMPT = get_prompt_module(jurisdiction, 'analysis').ABSTRACT_PROMPT
    prompt = ABSTRACT_PROMPT.format(text=text)
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    abstract_time = time.time() - start_time
    abstract = response.content
    print(f"\nAbstract:\n{abstract}\n")
    # append abstract
    state.setdefault("abstract", []).append(abstract)
    # return full updated lists
    return {
        "abstract": state["abstract"],
        "abstract_time": abstract_time
    }


# ===== RELEVANT FACTS =====
def relevant_facts(state):
    print("\n--- RELEVANT FACTS ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    FACTS_PROMPT = get_prompt_module(jurisdiction, 'analysis').FACTS_PROMPT
    col_section_content = _get_last_message_content(state.get("col_section"))
    prompt = FACTS_PROMPT.format(text=text, col_section=col_section_content)
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    facts_time = time.time() - start_time
    facts = response.content
    print(f"\nRelevant Facts:\n{facts}\n")
    # append relevant facts
    state.setdefault("relevant_facts", []).append(facts)
    # return full updated lists
    return {
        "relevant_facts": state["relevant_facts"],
        "relevant_facts_time": facts_time
    }

# ===== PIL PROVISIONS =====
def pil_provisions(state):
    print("\n--- PIL PROVISIONS ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    PIL_PROVISIONS_PROMPT = get_prompt_module(jurisdiction, 'analysis').PIL_PROVISIONS_PROMPT
    col_section_content = _get_last_message_content(state.get("col_section"))

    prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=col_section_content)
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    provisions_time = time.time() - start_time
    try:
        pil_provisions = json.loads(response.content)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse PIL provisions as JSON. Content: {response.content}")
        pil_provisions = [response.content.strip()]
    print(f"\nPIL Provisions:\n{pil_provisions}\n")
    # append pil_provisions
    state.setdefault("pil_provisions", []).append(pil_provisions)
    # return full updated lists
    return {
        "pil_provisions": state["pil_provisions"],
        "pil_provisions_time": provisions_time
    }

# ===== CHOICE OF LAW ISSUE =====
def col_issue(state):
    print("\n--- CHOICE OF LAW ISSUE ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    COL_ISSUE_PROMPT = get_prompt_module(jurisdiction, 'analysis').COL_ISSUE_PROMPT
    col_section_content = _get_last_message_content(state.get("col_section"))
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
    classification_definitions = filter_themes_by_list(themes_list)

    prompt = COL_ISSUE_PROMPT.format(
        text=text, 
        col_section=col_section_content, 
        classification_definitions=classification_definitions
    )
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    issue_time = time.time() - start_time
    col_issue = response.content
    print(f"\nChoice of Law Issue:\n{col_issue}\n")
    # append col_issue
    state.setdefault("col_issue", []).append(col_issue)
    # return full updated lists
    return {
        "col_issue": state["col_issue"],
        "col_issue_time": issue_time
    }

# ===== COURT'S POSITION =====
def courts_position(state):
    print("\n--- COURT'S POSITION ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    COURTS_POSITION_PROMPT = get_prompt_module(jurisdiction, 'analysis').COURTS_POSITION_PROMPT
    col_section_content = _get_last_message_content(state.get("col_section"))
    classification_content = _get_classification_content_str(state.get("classification"))

    prompt = COURTS_POSITION_PROMPT.format(
        text=text, 
        col_section=col_section_content, 
        classification=classification_content
    )
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    position_time = time.time() - start_time
    courts_position = response.content
    print(f"\nCourt's Position:\n{courts_position}\n")
    # append courts_position
    state.setdefault("courts_position", []).append(courts_position)
    # return full updated lists
    return {
        "courts_position": state["courts_position"],
        "courts_position_time": position_time
    }
