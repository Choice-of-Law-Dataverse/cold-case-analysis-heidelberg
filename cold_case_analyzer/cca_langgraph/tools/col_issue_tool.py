from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompts.prompt_templates import COL_ISSUE_PROMPT

@tool
def col_issue_tool(text: str, quote: str, classification: list[str], themes_table: dict, llm: ChatOpenAI) -> dict:
    """Identifies the main CoL issue as a Yes/No question."""
    # Assuming themes_table is a dict where keys are theme names and values are definitions
    # For simplicity, just using the first theme's definition if multiple themes are present.
    # A more sophisticated approach might concatenate definitions or require a single theme for this tool.
    main_theme = classification[0] if classification else ""
    definition = themes_table.get(main_theme, "No definition available for the provided theme.")
    
    prompt = COL_ISSUE_PROMPT.format(text=text, quote=quote, classification=classification, definition=definition)
    response = llm.invoke(prompt)
    return {"col_issue": response.content}
