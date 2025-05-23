from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from config import llm, thread_id
from prompts.analysis_prompts import ABSTRACT_PROMPT, FACTS_PROMPT, PIL_PROVISIONS_PROMPT, COL_ISSUE_PROMPT, COURTS_POSITION_PROMPT
from schemas.appstate import AppState


# ========== NODES ==========

# ===== ABSTRACT =====
def abstract_node(state: AppState):
    print("\n--- ABSTRACT ---")
    text = state["full_text"]
    col_section_messages = state.get("col_section", [])
    col_section = ""  # Default if not found or empty
    if col_section_messages:
        last_message = col_section_messages[-1]
        if hasattr(last_message, 'content'):
            col_section = last_message.content
    classification_messages = state.get("classification", [])
    classification = ""  # Default if not found or empty
    if classification_messages:
        last_message = classification_messages[-1]
        if hasattr(last_message, 'content'):
            classification = last_message.content
    prompt = ANALYSIS_PROMPT.format(text=text, col_section=col_section, classification=classification)
    print(f"\nPrompting LLM with:\n{prompt}\n")
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    abstract = response.content
    print(f"\nAbstract:\n{abstract}\n")
    
    return {
        "abstract": [AIMessage(content=abstract)]
    }

# ===== RELEVANT FACTS =====

# ===== PIL PROVISIONS =====

# ===== CHOICE OF LAW ISSUE =====

# ===== COURT'S POSITION =====


# ========== GRAPH ==========

graph = StateGraph(AppState)
graph.set_entry_point("analysis_node")
graph.add_node("analysis_node", analysis_node)
graph.add_node("final_feedback_node", analysis_feedback_node)
graph.add_edge(START, "analysis_node")
graph.add_edge("analysis_node", "final_feedback_node")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
thread_config = {"configurable": {"thread_id": thread_id}}


# ========== RUNNER ==========

def run_analysis(state: AppState):
    current_state = state.copy()

    for chunk in app.stream(current_state, config=thread_config):
        # merge output from analysis_node
        if "analysis_node" in chunk:
            out = chunk["analysis_node"]
            if isinstance(out, dict):
                current_state.update(out)

        # merge output from final_feedback_node
        if "analysis_feedback_node" in chunk:
            cmd_or_dict = chunk["analysis_feedback_node"]
            if isinstance(cmd_or_dict, Command):
                current_state.update(cmd_or_dict.update)
                if cmd_or_dict.goto == END:
                    return current_state
                return run_analysis(current_state)
            
            elif isinstance(cmd_or_dict, dict):
                current_state.update(cmd_or_dict)

        if "__interrupt__" in chunk:
            payload = chunk["__interrupt__"][0].value
            print("waiting for user feedback...")
            while True:
                user_input = input(payload["message"])
                if user_input.lower() == "done":
                    final_updated_state = app.get_state(config=thread_config)
                    return final_updated_state
                else:
                    current_state.setdefault("analysis_feedback", []).append(user_input)
                    current_state["user_approved_analysis"] = False
                    app.invoke(Command(resume=user_input), config=thread_config)
    return current_state
