from typing import TypedDict, List, Annotated
from langgraph.graph import add_messages

class AppState(TypedDict):
    full_text: str
    quote: str
    classification: List[str]
    user_approved_col: bool
    col_section_feedback: Annotated[List[str], add_messages]
    user_approved_theme: bool
    theme_feedback: Annotated[List[str], add_messages]
    analysis: str
    user_approved_analysis: bool
    final_feedback: Annotated[List[str], add_messages]
