import json

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
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
    col_section_messages = state.get("col_section", [])
    col_section = ""  # Default if not found or empty
    if col_section_messages:
        last_message = col_section_messages[-1]
        if hasattr(last_message, 'content'):
            col_section = last_message.content
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
    return {
        "classification": [AIMessage(content=classification)],
        "theme_feedback": theme_feedback
    }

def theme_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: THEME ---")
    theme_feedback = interrupt(
        {
            "classification": state["classification"],
            "message": "Provide feedback for the Private International Law classification or type 'continue' to proceed with the analysis: "
        }
    )
    if theme_feedback.lower() == "continue":
        return Command(
            update={
                "user_approved_theme": True,
                "theme_feedback": state["theme_feedback"] + ["Finalised"]
            },
            goto=END
        )
    
    return Command(
        update={
            "user_approved_theme": False,
            "theme_feedback": state["theme_feedback"] + [theme_feedback]
        },
        goto="theme_classification_node"
    )


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
        # merge output from theme_classification_node
        if "theme_classification_node" in chunk:
            out = chunk["theme_classification_node"]
            if isinstance(out, dict):
                current_state.update(out)
        
        # merge output from feedback node (Command or dict)
        if "theme_feedback_node" in chunk:
            cmd_or_dict = chunk["theme_feedback_node"]
            if isinstance(cmd_or_dict, Command):
                current_state.update(cmd_or_dict.update)
                if cmd_or_dict.goto == END:
                    return current_state
                return run_theme_classification(current_state)
            
            elif isinstance(cmd_or_dict, dict):
                current_state.update(cmd_or_dict)

        if "__interrupt__" in chunk:
            payloud = chunk["__interrupt__"][0].value
            print("waiting for user feedback...")
            while True:
                user_feedback = input(payloud["message"])
                if user_feedback.lower() == "continue":
                    app.invoke(Command(resume=user_feedback), config=thread_config)
                    final_updated_state = app.get_state(config=thread_config)
                    return final_updated_state
                else:
                    current_state.setdefault("theme_feedback", []).append(user_feedback)
                    current_state["user_approved_theme"] = False
                    app.invoke(Command(resume=user_feedback), config=thread_config)
    return current_state
