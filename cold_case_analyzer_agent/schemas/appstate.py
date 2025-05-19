from typing import TypedDict, List, Annotated
from langgraph.graph import add_messages

class AppState(TypedDict):
    full_text: str
    col_section: str
    col_section_feedback: Annotated[List[str], add_messages]
    user_approved_col: bool
    classification: List[str]
    theme_feedback: Annotated[List[str], add_messages]
    user_approved_theme: bool
    analysis: str
    analysis_feedback: Annotated[List[str], add_messages]
    user_approved_analysis: bool
