import json

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.pil_theme_prompt import PIL_THEME_PROMPT
from schemas.appstate import AppState
from utils.themes_extractor import THEMES_TABLE_STR


# ========== NODES ==========

def theme_classification_node(state: AppState):
    print("\n--- THEME CLASSIFICATION ---")
    text = state["full_text"]
    col_section = state["col_section"]
    theme_feedback = state["theme_feedback"] if "theme_feedback" in state else ["No feedback yet"]
    prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)
    if theme_feedback:
        prompt += f"\n\nPrevious feedback: {theme_feedback[-1]}\n"
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    try:
        classification = json.loads(response.content)
    except Exception:
        classification = [response.content.strip()]
    print(f"\nClassified theme(s): {classification}\n")
    updated_theme_feedback = theme_feedback + [classification]
    updated_state = state.copy()
    updated_state["classification"] = classification
    updated_state["theme_feedback"] = updated_theme_feedback
    return updated_state

def theme_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: THEME ---")
    theme_feedback = interrupt(
        {
            "classification": state["classification"],
            "message": "Provide feedback for the Private International Law classification or type 'continue' to proceed with the analysis: ",
            "workflow": "theme_feedback"
        }
    )
    updated_state = state.copy()
    if theme_feedback.lower() == "continue":
        updated_state["user_approved_theme"] = True
        return updated_state
    updated_state["user_approved_theme"] = False
    updated_state["theme_feedback"] = updated_state.get("theme_feedback", []) + [theme_feedback]
    return updated_state


# ========== GRAPH ==========

graph = StateGraph(AppState)
graph.set_entry_point("theme_classification_node")
graph.add_node("theme_classification_node", theme_classification_node)
graph.add_node("theme_feedback_node", theme_feedback_node)
graph.add_edge(START, "theme_classification_node")
graph.add_edge("theme_classification_node", "theme_feedback_node")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
thread_config = {"configurable": {"thread_id": thread_id}}


# ========== RUNNER ==========

def run_theme_classification(state: AppState):
    current_state = state.copy()
    for chunk in app.stream(current_state, config=thread_config):
        for node_id, value in chunk.items():
            if node_id == "__interrupt__":
                print("theme_feedback detected, now waiting for user feedback...")
                while True:
                    user_theme_feedback = input(value[0].value['message'])
                    if user_theme_feedback.lower() == "continue":
                        current_state["user_approved_theme"] = True
                        return current_state
                    else:
                        current_state["theme_feedback"] = current_state.get("theme_feedback", []) + [user_theme_feedback]
                        current_state["user_approved_theme"] = False
                        app.invoke(Command(resume=user_theme_feedback), config=thread_config)
    return current_state