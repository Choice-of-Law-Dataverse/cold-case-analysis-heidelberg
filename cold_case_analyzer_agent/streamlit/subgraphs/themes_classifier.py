import json
import re
import time

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.pil_theme_prompt import PIL_THEME_PROMPT
from schemas.appstate import AppState
from utils.themes_extractor import THEMES_TABLE_STR
from utils.evaluator import prompt_evaluation
from utils.input_handler import INPUT_FUNC


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
    
    # ===== BUMP AND READ COUNTER =====
    iter_count = state.get("theme_classification_iter", 0) + 1
    state["theme_classification_iter"] = iter_count
    key = f"theme_classification{iter_count}"

    # ===== ADD EXISTING CLASSIFICATION TO PROMPT =====
    previous_classification_text = ""
    existing_classification_messages = state.get("classification")
    #print(f"Existing classification messages: {existing_classification_messages}") # Kept for debugging as in original
    
    if existing_classification_messages and isinstance(existing_classification_messages, list) and len(existing_classification_messages) > 0:
        last_classification_message = existing_classification_messages[-1]
        
        # Directly access the content and handle if it's a list or string
        if hasattr(last_classification_message, 'content'):
            content_value = last_classification_message.content
            processed_content = ""
            if isinstance(content_value, list):
                if content_value: # If list is not empty
                    processed_content = ", ".join(str(item) for item in content_value)
            elif isinstance(content_value, str):
                processed_content = content_value
            # Add other type handling here if necessary

            if processed_content: # Only use if non-empty
                actual_previous_classification_text = processed_content
                prompt += f"\n\nfirst answer suggestion: {actual_previous_classification_text}\n"

    # ===== ADD FEEDBACK TO PROMPT =====
    if theme_feedback:
        fast_feedback_item_str = str(theme_feedback[-1])
        match = re.search(r"content='([^']*)'", fast_feedback_item_str)
        if match:
            feedback_text_to_add = match.group(1)
        else:
            feedback_text_to_add = theme_feedback[-1]

        if feedback_text_to_add and feedback_text_to_add != "No feedback yet":
            prompt += f"\n\nFeedback: {feedback_text_to_add}\n"
        elif feedback_text_to_add == "No feedback yet" and not (existing_classification_messages and previous_classification_text):
            prompt += f"\n\nFeedback: {feedback_text_to_add}\n"

    #print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    theme_time = time.time() - start_time
    try:
        classification = json.loads(response.content)
    except Exception:
        classification = [response.content.strip()]
    print(f"\nClassified theme(s): {classification}\n")
    # Ask user for evaluation using the shared utility
    score = prompt_evaluation(state, "theme_evaluation", "Please evaluate the theme classification", key=key)
    return {
        "classification": [AIMessage(content=classification)],
        "theme_feedback": theme_feedback,
        "theme_evaluation": score,
        "theme_classification_time": theme_time
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
                # ===== BUMP AND READ COUNTER =====
                cnt = current_state.get("theme_interrupt_iter", 0) + 1
                current_state["theme_interrupt_iter"] = cnt
                key = f"theme_interrupt_{cnt}"

                user_feedback = INPUT_FUNC(payloud["message"], key=key)
                if user_feedback.lower() == "continue":
                    app.invoke(Command(resume=user_feedback), config=thread_config)
                    final_updated_state = app.get_state(config=thread_config)
                    return final_updated_state
                else:
                    current_state.setdefault("theme_feedback", []).append(user_feedback)
                    current_state["user_approved_theme"] = False
                    app.invoke(Command(resume=user_feedback), config=thread_config)
    return current_state
