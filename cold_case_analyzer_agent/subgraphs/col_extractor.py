from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.col_section_prompt import COL_SECTION_PROMPT
from schemas.appstate import AppState


# ========== NODES ==========

def col_section_node(state: AppState):
    print("\n--- COL SECTION EXTRACTION ---")
    text = state["full_text"]
    col_section_feedback = state["col_section_feedback"] if "col_section_feedback" in state else ["No feedback yet"]
    prompt = COL_SECTION_PROMPT.format(text=text)
    if col_section_feedback:
        prompt += f"\n\nPrevious feedback: {col_section_feedback[-1]}\n"
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    col_section = response.content
    print(f"\nExtracted Choice of Law section:\n{col_section}\n")
    # Append new col_section to col_section_feedback
    updated_col_section_feedback = col_section_feedback + [col_section]
    updated_state = state.copy()
    updated_state["col_section"] = col_section
    updated_state["col_section_feedback"] = updated_col_section_feedback
    return updated_state

def col_section_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: COL SECTION ---")
    col_section_feedback = interrupt(
        {
            "col_section": state["col_section"],
            "message": "Provide feedback for the Choice of Law section or type 'continue' to proceed with the analysis: ",
            "workflow": "col_section_feedback"
        }
    )
    updated_state = state.copy()
    if col_section_feedback.lower() == "continue":
        updated_state["user_approved_col"] = True
        updated_state["col_section_feedback"] = updated_state.get("col_section_feedback", []) + ["Finalised"]
        return Command(update={"user_approved_col": True, "col_section_feedback": state["col_section_feedback"] + ["Finalised"]}, goto=END)

    return Command(update={"col_section_feedback": state["col_section_feedback"] + [col_section_feedback], "user_approved_col": False}, goto="col_section_node")


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
    current_state = state.copy()
    for chunk in app.stream(current_state, config=thread_config):
        for node_id, value in chunk.items():
            if node_id == "__interrupt__":
                print("col_section_feedback detected, now waiting for user feedback...")
                while True:
                    user_col_feedback = input(value[0].value['message'])
                    if user_col_feedback.lower() == "continue":
                        current_state["user_approved_col"] = True
                        return current_state
                    else:
                        current_state["col_section"] = value[0].value['col_section']
                        current_state["col_section_feedback"] = current_state.get("col_section_feedback", []) + [user_col_feedback]
                        current_state["user_approved_col"] = False
                        app.invoke(Command(resume=user_col_feedback), config=thread_config)
    return current_state

"""
def run_col_section_extraction(state: AppState):
    current_state = state.copy()

    for chunk in app.stream(current_state, config=thread_config):
        # 1) handle user-feedback interrupts
        if "__interrupt__" in chunk:
            interrupt_payload = chunk["__interrupt__"][0].value
            print("col_section_feedback detected, now waiting for user feedback...")
            user_input = input(interrupt_payload["message"])

            # record feedback
            current_state.setdefault("col_section_feedback", [])
            if user_input.lower() == "continue":
                current_state["col_section_feedback"].append("Finalised")
                current_state["user_approved_col"] = True
            else:
                current_state["col_section_feedback"].append(user_input)
                current_state["user_approved_col"] = False

            # resume the graph with that input
            app.invoke(Command(resume=user_input), config=thread_config)
            continue

        # 2) handle normal node output
        if "col_section_node" in chunk:
            output = chunk["col_section_node"]
            # the compiled graph now returns a dict here
            if isinstance(output, dict):
                current_state.update(output)
            # (if you ever get a list of MessageOutputs, you’d do:)
            # elif isinstance(output, list):
            #     current_state.update(output[0].value)
            continue

    return current_state
"""