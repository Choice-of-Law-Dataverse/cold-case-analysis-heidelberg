from typing import TypedDict, List, Annotated
from langgraph.graph import add_messages

class AppState(TypedDict):
    full_text: str
    col_section: Annotated[List[str], add_messages]
    col_section_feedback: Annotated[List[str], add_messages]
    col_section_evaluation: int
    user_approved_col: bool
    classification: List[str]
    theme_feedback: Annotated[List[str], add_messages]
    theme_evaluation: int
    user_approved_theme: bool
    abstract: str
    abstract_evaluation: int
    relevant_facts: str
    relevant_facts_evaluation: int
    pil_provisions: str
    pil_provisions_evaluation: int
    col_issue: str
    col_issue_evaluation: int
    courts_position: str
    courts_position_evaluation: int
