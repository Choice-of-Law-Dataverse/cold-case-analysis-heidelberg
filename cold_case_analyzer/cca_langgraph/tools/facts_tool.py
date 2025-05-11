from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import RELEVANT_FACTS_PROMPT

@tool
def relevant_facts_tool(text: str, quote: str, llm: ChatOpenAI) -> dict:
    """Extracts and summarizes relevant facts for PIL/CoL from the court decision."""
    prompt = RELEVANT_FACTS_PROMPT.format(text=text, quote=quote)
    response = llm.invoke(prompt)
    return {"relevant_facts": response.content}
