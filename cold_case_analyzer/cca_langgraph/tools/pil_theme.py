from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import PIL_THEME_PROMPT
import json

@tool
def pil_theme_tool(text: str, quote: str, themes_table: str, llm: ChatOpenAI) -> dict:
    """Classifies the case based on its CoL issue into predefined themes."""
    prompt = PIL_THEME_PROMPT.format(text=text, quote=quote, themes_table=themes_table)
    response = llm.invoke(prompt)
    # Assuming the LLM returns a string representation of a list, e.g., "['Theme 1', 'Theme 2']"
    try:
        classification = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback or error handling if the response is not a valid JSON list string
        classification = [response.content] # Treat as a single theme if parsing fails
    return {"classification": classification}
