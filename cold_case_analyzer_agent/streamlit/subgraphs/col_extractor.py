import re
import time

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from schemas.appstate import AppState
from prompts.col_section_prompt import COL_SECTION_PROMPT
from utils.evaluator import prompt_evaluation
from utils.debug_print_state import print_state


# ========== NODES ==========

def col_section_node(state: AppState):
    print("\n--- COL SECTION EXTRACTION ---")
    text = state["full_text"]
    feedback = state.get("col_section_feedback", ["No feedback yet"])
    print("\nFeedback for col section:", feedback, "\n")
    prompt = COL_SECTION_PROMPT.format(text=text)

    # ===== BUMP AND READ COUNTER =====
    iter_count = state.get("col_section_eval_iter", 0) + 1
    state["col_section_eval_iter"] = iter_count
    key = f"col_section_eval_{iter_count}"

    # ===== ADD EXISTING COL SECTION TO PROMPT =====
    existing_col_section_messages = state.get("col_section")
    if existing_col_section_messages and isinstance(existing_col_section_messages, list) and len(existing_col_section_messages) > 0:
        last_col_section_message = existing_col_section_messages[-1]
        # The str() conversion and regex will handle AIMessage or HumanMessage objects
        match = re.search(r"content='([^']*)'", str(last_col_section_message))
        if match:
            previous_col_section_text = match.group(1)
            # Only add to prompt if the extracted text is not empty
            if previous_col_section_text: 
                prompt += f"\n\nFirst answer suggestion: {previous_col_section_text}\n"

    # ===== ADD FEEDBACK TO PROMPT =====
    if feedback:
        last_feedback_item_str = str(feedback[-1])
        match = re.search(r"content='([^']*)'", last_feedback_item_str)
        if match:
            previous_suggestion_text = match.group(1)
        else:
            previous_suggestion_text = last_feedback_item_str
        prompt += f"\n\nFeedback: {previous_suggestion_text}\n"
    #print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    col_time = time.time() - start_time
    col_section = response.content
    state["col_section"].append(col_section)
    print(f"\nExtracted Choice of Law section:\n{col_section}\n")

    return {
        "col_section": [AIMessage(content=col_section)],
        "col_section_feedback": feedback,
        #"col_section_evaluation": score,
        "col_section_time": col_time
    }

def col_section_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: COL SECTION ---")
    user_feedback = interrupt({
        "col_section": state["col_section"],
        "message": "Provide feedback for the col section or type 'continue': "
    })
    #print("\nNow calling the OUTPUT_FUNC for user feedback from the col_section_feedback_node")
    #OUTPUT_FUNC(f"User feedback: {user_feedback}", key=f"col_section_feedback_{state['col_section_eval_iter']}")
    if user_feedback.lower() == "continue":
        return Command(
            update={
                "user_approved_col": True,
                "col_section_feedback": state["col_section_feedback"] + ["Finalised"]
            },
            goto=END
        )

    return Command(
        update={
            "user_approved_col": False,
            "col_section_feedback": state["col_section_feedback"] + [user_feedback]
        },
        goto="col_section_node"
    )


# ========== GRAPH ==========

graph = StateGraph(AppState)
graph.set_entry_point("col_section_node")
graph.add_node("col_section_node", col_section_node)
graph.add_node("col_section_feedback_node", col_section_feedback_node)
graph.add_edge(START, "col_section_node")
graph.add_edge("col_section_node", "col_section_feedback_node")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
thread_config = {"configurable": {"thread_id": thread_id}}


# ========== RUNNER ==========

def run_col_section_extraction(state: AppState):
    """
    Stream raw graph execution chunks (node outputs, commands, interrupts) for UI to handle.
    """
    return app.stream(state, config=thread_config)
