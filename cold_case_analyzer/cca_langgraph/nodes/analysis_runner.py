from tools.abstract_tool import abstract_tool
from tools.facts_tool import relevant_facts_tool
from tools.provisions_tool import pil_provisions_tool
from tools.col_issue_tool import col_issue_tool
from tools.courts_position_tool import courts_position_tool

# These functions will be wrapped into nodes in the graph_config

def run_abstract_tool(state, llm_instance):
    print("--- RUNNING ABSTRACT TOOL ---")
    result = abstract_tool.invoke({
        "text": state["full_text"], 
        "quote": state["quote"], 
        "llm": llm_instance
    })
    return {"abstract": result["abstract"]}

def run_relevant_facts_tool(state, llm_instance):
    print("--- RUNNING RELEVANT FACTS TOOL ---")
    result = relevant_facts_tool.invoke({
        "text": state["full_text"], 
        "quote": state["quote"], 
        "llm": llm_instance
    })
    return {"relevant_facts": result["relevant_facts"]}

def run_pil_provisions_tool(state, llm_instance):
    print("--- RUNNING PIL PROVISIONS TOOL ---")
    result = pil_provisions_tool.invoke({
        "text": state["full_text"], 
        "quote": state["quote"], 
        "llm": llm_instance
    })
    return {"pil_provisions": result["pil_provisions"]}

def run_col_issue_tool(state, llm_instance):
    print("--- RUNNING COL ISSUE TOOL ---")
    # themes_table is needed by the tool for the definition
    themes_table_data = state.get("themes_table_data", {}) # Ensure this is loaded in main.py
    result = col_issue_tool.invoke({
        "text": state["full_text"],
        "quote": state["quote"],
        "classification": state["classification"],
        "themes_table": themes_table_data, # Pass the actual themes_table data
        "llm": llm_instance
    })
    return {"col_issue": result["col_issue"]}

def run_courts_position_tool(state, llm_instance):
    print("--- RUNNING COURTS POSITION TOOL ---")
    result = courts_position_tool.invoke({
        "text": state["full_text"],
        "quote": state["quote"],
        "col_issue": state["col_issue"],
        "llm": llm_instance
    })
    return {"courts_position": result["courts_position"]}
