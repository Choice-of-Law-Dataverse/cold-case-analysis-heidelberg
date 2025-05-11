from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import COURTS_POSITION_PROMPT

@tool
def courts_position_tool(text: str, quote: str, col_issue: str, llm: ChatOpenAI) -> dict:
    """Summarizes the court's general position on the identified CoL issue."""
    prompt = COURTS_POSITION_PROMPT.format(text=text, quote=quote, col_issue=col_issue)
    response = llm.invoke(prompt)
    return {"courts_position": response.content}
