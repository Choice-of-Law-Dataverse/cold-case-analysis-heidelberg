# tools/jurisdiction_detector.py
"""
Detects the jurisdiction type of a court decision: Civil-law, Common-law, or No court decision using an LLM.
"""
import re
from config import llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

JURISDICTION_PROMPT = '''
You are a legal expert. Your task is to classify the following text as coming from a "Civil-law jurisdiction", a "Common-law jurisdiction", or as "No court decision".

- If the text is a court decision from a civil law country (e.g., Germany, France, Italy, Spain, Switzerland, Austria, etc.), respond with exactly: Civil-law jurisdiction
- If the text is a court decision from a common law country (e.g., United States, England, Australia, Canada, etc.), respond with exactly: Common-law jurisdiction
- If the text is not a court decision, or you cannot tell, respond with exactly: No court decision

Return only one of these three options, and nothing else.

Text:
{text}
'''

def detect_jurisdiction(text: str) -> str:
    """
    Uses an LLM to classify the input text as:
    - 'Civil-law jurisdiction'
    - 'Common-law jurisdiction'
    - 'No court decision'
    """
    if not text or len(text.strip()) < 50:
        return "No court decision"
    prompt = JURISDICTION_PROMPT.format(text=text)
    response = llm.invoke([
        SystemMessage(content="You are an expert in legal systems and court decisions."),
        HumanMessage(content=prompt)
    ])
    result = response.content.strip()
    # Enforce output to be one of the three categories
    allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
    for option in allowed:
        if option.lower() in result.lower():
            return option
    return "No court decision"
