import re
import time

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st

from config import llm, thread_id
from schemas.appstate import AppState
from prompts.col_section_prompt import COL_SECTION_PROMPT
from utils.evaluator import prompt_evaluation
from utils.debug_print_state import print_state
from utils.input_handler import INPUT_FUNC
from utils.output_handler import OUTPUT_FUNC


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

    # Ask user for evaluation and record time
    #score = prompt_evaluation(state, "col_section_evaluation", "Please evaluate the extracted Choice of Law section", input_key=key)

    print("NOW CALLING OUTPUT_FUNC FROM col_section_node")
    OUTPUT_FUNC(col_section, key)

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
    # Initialize session_state once
    if "col_state" not in st.session_state:
        st.session_state.col_state = dict(state)
        st.session_state.coler = app.stream(st.session_state.col_state, config=thread_config)
        st.session_state.waiting_for = None
        #print_state("col_extractor init session_state", dict(st.session_state))
    # Resume after previous feedback
    if st.session_state.waiting_for is not None:
        app.invoke(Command(resume=st.session_state.waiting_for), config=thread_config)
        st.session_state.waiting_for = None

    # Process chunks in a loop until interrupt or END
    while True:
        try:
            chunk = next(st.session_state.coler)
        except StopIteration:
            print_state("col_extractor final state", dict(st.session_state))
            return st.session_state.col_state

        # extraction output
        if "col_section_node" in chunk:
            st.session_state.col_state.update(chunk["col_section_node"])
            continue

        # feedback Command
        if "col_section_feedback_node" in chunk:
            cmd = chunk["col_section_feedback_node"]
            if isinstance(cmd, Command):
                st.session_state.col_state.update(cmd.update)
                print_state("col_extractor feedback cmd update", dict(st.session_state))
                if cmd.goto == END:
                    print_state("col_extractor final state after END", dict(st.session_state))
                    return st.session_state.col_state
                # else continue loop
                continue

        # LLM interrupt for user feedback
        if "__interrupt__" in chunk:
            payload = chunk["__interrupt__"][0].value
            iter_count = st.session_state.col_state.get("col_section_eval_iter", 1)
            # render feedback widget and pause
            user_fb = INPUT_FUNC(payload["message"], key=f"col_fb_{iter_count}")
            st.session_state.app_state["col_section_feedback"].append(user_fb)
            st.session_state.col_state["col_section_feedback"].append(user_fb)
            if st.button("Submit feedback", key=f"col_submit_{iter_count}"):
                st.session_state.waiting_for = user_fb
                #print_state("col_extractor set waiting_for", dict(st.session_state))
            st.stop()
        # otherwise ignore and continue looping
        continue
    # end while
