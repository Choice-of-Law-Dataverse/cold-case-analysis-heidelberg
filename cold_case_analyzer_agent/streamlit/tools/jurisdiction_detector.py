# tools/jurisdiction_detector.py
"""
Detects the jurisdiction type of a court decision: Civil-law, Common-law, or No court decision using an LLM.
"""
import re
from config import llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from prompts.prompt_selector import get_prompt_module

# Always use civil-law prompt for initial detection (since jurisdiction is not yet known)
JURISDICTION_DETECTION_PROMPT = get_prompt_module('Civil-law jurisdiction', 'jurisdiction_detection').JURISDICTION_DETECTION_PROMPT

def detect_jurisdiction(text: str) -> str:
    """
    Uses an LLM to classify the input text as:
    - 'Civil-law jurisdiction'
    - 'Common-law jurisdiction'
    - 'No court decision'
    """
    if not text or len(text.strip()) < 50:
        return "No court decision"
    prompt = JURISDICTION_DETECTION_PROMPT.format(text=text)
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
