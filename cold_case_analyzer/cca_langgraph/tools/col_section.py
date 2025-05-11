from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import COL_SECTION_PROMPT

@tool
def col_section_tool(text: str, llm: ChatOpenAI) -> dict:
    """Extracts the Choice of Law section from the court decision text."""
    prompt = COL_SECTION_PROMPT.format(text=text, quote="") # Initial extraction, so quote is empty
    response = llm.invoke(prompt)
    return {"quote": response.content}
