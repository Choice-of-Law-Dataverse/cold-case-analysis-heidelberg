from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import ABSTRACT_PROMPT

@tool
def abstract_tool(text: str, quote: str, llm: ChatOpenAI) -> dict:
    """Generates a concise abstract or translates a Regeste for the court decision."""
    prompt = ABSTRACT_PROMPT.format(text=text, quote=quote)
    response = llm.invoke(prompt)
    return {"abstract": response.content}
