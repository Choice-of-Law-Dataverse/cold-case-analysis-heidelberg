"""
court_decision_analyzer.py
=========================

A script to build and test a Court Decision Analyzer agent that:
- Analyzes and summarizes court decisions
- Allows for interactive feedback and improvements
- Maintains context of previous iterations
- Provides structured, clear summaries
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# 1. Load environment
load_dotenv()

# 2. Initialize the model
model = init_chat_model("gpt-4o-mini", model_provider="openai")

# 3. Create the agent with specific instructions
system_instructions = """
You are a Court Decision Analyser. Your role is to:
1) Analyse court decisions and provide clear, structured summaries
2) Focus on key legal principles, facts, and outcomes
3) Use plain language while maintaining legal accuracy
4) Be open to feedback and improvements
5) Maintain context of previous iterations
6) Structure your response with:
   - Abstract
   - Choice of Law Section
   - Relevant Facts
   - Private International Law Provisions
   - Private International Law Theme
   - Choice of Law Issue
   - Court's Position

When receiving feedback:
1) Acknowledge the feedback
2) Explain your changes
3) Maintain the original legal accuracy
4) Keep the summary concise and clear
"""

# 4. Create the agent executor
memory = MemorySaver()
agent_executor = create_react_agent(
    model,
    tools=[],  # No external tools needed for this task
    checkpointer=memory,
    prompt=system_instructions
)

def analyse_court_decision(decision_text, thread_id="court-analysis-001"):
    """
    Analyse a court decision and return a summary.
    
    Args:
        decision_text (str): The text of the court decision
        thread_id (str): Unique identifier for the conversation thread
    
    Returns:
        dict: Response containing the analysis
    """
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=decision_text)]},
        {"configurable": {"thread_id": thread_id}}
    )
    return response

def improve_summary(feedback, thread_id="court-analysis-001"):
    """
    Improve the summary based on user feedback.
    
    Args:
        feedback (str): User's feedback on the previous summary
        thread_id (str): Unique identifier for the conversation thread
    
    Returns:
        dict: Response containing the improved analysis
    """
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=feedback)]},
        {"configurable": {"thread_id": thread_id}}
    )
    return response

# Example usage
if __name__ == "__main__":
    # Example court decision text
    sample_decision = """
    SUPREME COURT OF THE UNITED STATES
    No. 21-1234
    SMITH v. JONES
    Decided June 1, 2023
    
    The petitioner, John Smith, filed a lawsuit against the respondent, 
    Jane Jones, alleging breach of contract. The district court granted 
    summary judgment in favor of Jones. The court of appeals affirmed. 
    We granted certiorari to consider whether the lower courts properly 
    interpreted the contract's force majeure clause.
    
    The contract between Smith and Jones contained a force majeure clause 
    that excused performance in the event of "acts of God or other 
    circumstances beyond the reasonable control of the parties." During 
    the contract period, a global pandemic occurred, which Smith argued 
    triggered the force majeure clause.
    
    The Court held that the pandemic did not constitute a force majeure 
    event under the contract's terms. The Court reasoned that the clause 
    required the event to be both unforeseeable and beyond the parties' 
    control. While the pandemic was beyond the parties' control, it was 
    not unforeseeable given the history of global health crises.
    
    The judgment of the Court of Appeals is affirmed.
    """
    
    # Initial analysis
    print("Initial Analysis:")
    response = analyse_court_decision(sample_decision)
    print(response["messages"][-1].content)
    
    # Example feedback
    feedback = "Could you focus more on the legal reasoning behind the Court's decision regarding foreseeability?"
    print("\nImproving based on feedback:")
    response = improve_summary(feedback)
    print(response["messages"][-1].content) 