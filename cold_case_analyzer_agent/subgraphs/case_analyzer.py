from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.analysis_prompt import ANALYSIS_PROMPT
from schemas.appstate import AppState


# ========== NODES ==========

def analysis_node(state: AppState):
    print("\n--- ANALYSIS ---")
    text = state["full_text"]
    col_section = state["col_section"]
    classification = state["classification"]
    prompt = ANALYSIS_PROMPT.format(text=text, col_section=col_section, classification=classification)
    analysis_feedback = state["analysis_feedback"] if "analysis_feedback" in state else ["No feedback yet"]
    if analysis_feedback:
        prompt += f"\n\nPrevious feedback: {analysis_feedback[-1]}\n"
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    analysis = response.content
    print(f"\nAnalysis:\n{analysis}\n")
    # Append new analysis to analysis_feedback
    updated_analysis_feedback = analysis_feedback + [analysis]
    # Update state with new analysis and feedback
    updated_state = state.copy()
    updated_state["analysis"] = analysis
    updated_state["analysis_feedback"] = updated_analysis_feedback
    return updated_state

def final_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: FINAL ANALYSIS ---")
    final_feedback = interrupt(
        {
            "analysis": state["analysis"],
            "message": "Provide feedback for the analysis or type 'done' to finish: ",
            "workflow": "final_feedback"
        }
    )
    updated_state = state.copy()
    if final_feedback.lower() == "done":
        updated_state["user_approved_analysis"] = True
        return updated_state
    # Append feedback to final_feedback list
    if "final_feedback" in updated_state:
        updated_state["final_feedback"] = updated_state["final_feedback"] + [final_feedback]
    else:
        updated_state["final_feedback"] = [final_feedback]
    updated_state["user_approved_analysis"] = False
    return updated_state


# ========== GRAPH ==========

graph = StateGraph(AppState)
graph.set_entry_point("analysis_node")
graph.add_node("analysis_node", analysis_node)
graph.add_node("final_feedback_node", final_feedback_node)
graph.add_edge(START, "analysis_node")
graph.add_edge("analysis_node", "final_feedback_node")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
thread_config = {"configurable": {"thread_id": thread_id}}


# ========== RUNNER ==========

def run_analysis(state: AppState):
    current_state = state.copy()
    for chunk in app.stream(current_state, config=thread_config):
        for node_id, value in chunk.items():
            if node_id == "__interrupt__" and value[0].value['workflow'] == "final_feedback":
                print("final_feedback detected, now waiting for user feedback...")
                while True:
                    final_feedback = input(value[0].value['message'])
                    if final_feedback.lower() == "done":
                        current_state["user_approved_analysis"] = True
                        return current_state
                    else:
                        # Update state with new feedback
                        if "final_feedback" in current_state:
                            current_state["final_feedback"] = current_state["final_feedback"] + [final_feedback]
                        else:
                            current_state["final_feedback"] = [final_feedback]
                        current_state["user_approved_analysis"] = False
                        app.invoke(Command(resume=final_feedback), config=thread_config)
    return current_state
