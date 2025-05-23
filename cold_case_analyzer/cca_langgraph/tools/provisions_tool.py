from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import PIL_PROVISIONS_PROMPT
import json

@tool
def pil_provisions_tool(text: str, quote: str, llm: ChatOpenAI) -> dict:
    """Extracts relevant PIL provisions, sorted by relevance."""
    prompt = PIL_PROVISIONS_PROMPT.format(text=text, quote=quote)
    response = llm.invoke(prompt)
    try:
        provisions = json.loads(response.content)
    except json.JSONDecodeError:
        provisions = [response.content] # Treat as a single provision if parsing fails
    return {"pil_provisions": provisions}
