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
    #print("State \n", state)
    text = state["full_text"]
    quote = state["quote"]
    classification = state["classification"]
    prompt = ANALYSIS_PROMPT.format(text=text, quote=quote, classification=classification)
    analysis_feedback = state["analysis"] if "analysis" in state else ["No feedback yet"]
    if analysis_feedback:
        prompt += f"\n\nPrevious feedback: {analysis_feedback[-1]}\n"
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    analysis = response.content
    print(f"\nAnalysis:\n{analysis}\n")
    return {"analysis": [AIMessage(content=analysis)], "analysis_feedback": analysis_feedback}

def final_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: FINAL ANALYSIS ---")
    #print("State \n", state)
    final_feedback = interrupt(
        {
            "analysis": state["analysis"],
            "message": "Provide feedback for the analysis or type 'done' to finish: ",
            "workflow": "final_feedback"
        }
    )
    if final_feedback.lower() == "done":
        return Command(update={"user_approved_analysis": True}, goto=END)
    return Command(update={"user_approved_analysis": False, "final_feedback": state["final_feedback"] + [final_feedback]}, goto="analysis_node")


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
    for chunk in app.stream(state, config=thread_config):
        for node_id, value in chunk.items():
            if node_id == "__interrupt__" and value[0].value['workflow'] == "final_feedback":
                print("final_feedback detected, now waiting for user feedback...")
                while True:
                    final_feedback = input(value[0].value['message'])

                    if final_feedback.lower() == "continue":
                        return state
                    
                    else:
                        app.invoke(Command(resume=final_feedback), config=thread_config)
