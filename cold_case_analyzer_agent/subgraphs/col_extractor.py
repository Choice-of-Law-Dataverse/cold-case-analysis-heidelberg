from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.col_section_prompt import COL_SECTION_PROMPT
from schemas.appstate import AppState


# ========== NODES ==========

def col_section_node(state: AppState):
    print("\n--- COL SECTION EXTRACTION ---")
    #print("State \n", state)
    text = state["full_text"]
    col_section_feedback = state["col_section_feedback"] if "col_section_feedback" in state else ["No feedback yet"]
    prompt = COL_SECTION_PROMPT.format(text=text)
    if col_section_feedback:
        prompt += f"\n\nPrevious feedback: {col_section_feedback[-1]}\n"
    #print(f"\nPrompt for CoL section extraction:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    quote = response.content
    print(f"\nExtracted Choice of Law section:\n{quote}\n")
    return {
        "quote": [AIMessage(content=quote)],
        "col_section_feedback": col_section_feedback
    }

def col_section_feedback_node(state: AppState):
    print("\n--- USER FEEDBACK: COL SECTION ---")
    #print("State \n", state)
    col_section_feedback = interrupt(
        {
            "col_section": state["quote"],
            "message": "Provide feedback for the Choice of Law section or type 'continue' to proceed with the analysis: ",
            "workflow": "col_section_feedback"
        }
    )
    
    if col_section_feedback.lower() == "continue":
        return Command(update={"user_approved_col": True, "col_section_feedback": state["col_section_feedback"] + ["Finalised"]}, goto="theme_classification_node")
    
    return Command(update={"col_section_feedback": state["col_section_feedback"] + [col_section_feedback]}, goto="col_section_node")


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
    for chunk in app.stream(state, config=thread_config):
        for node_id, value in chunk.items():
            if node_id == "__interrupt__":# and value[0].value['workflow'] == "col_section_feedback":
                print("col_section_feedback detected, now waiting for user feedback...")
                while True:
                    user_col_feedback = input(value[0].value['message'])

                    if user_col_feedback.lower() == "continue":
                        return state

                    else:
                        app.invoke(Command(resume=user_col_feedback), config=thread_config)