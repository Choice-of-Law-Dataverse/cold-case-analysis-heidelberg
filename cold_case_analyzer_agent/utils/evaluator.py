"""
Utility for prompting the user to evaluate generated output and return a score.
"""
from typing import Any, Dict

def prompt_evaluation(state: Dict[str, Any], key: str, question: str) -> int:
    """
    Ask the user to provide an evaluation score (0-100) for a generated item.
    If the state already contains a score between 0 and 100 inclusive, returns it directly.

    Args:
        state: the current state dict
        key: the state key for this evaluation (e.g., 'abstract_evaluation')
        question: the text to display when prompting the user

    Returns:
        An integer score between 0 and 100.
    """
    existing_score = state.get(key, 101)
    # Return existing valid score
    if isinstance(existing_score, int) and 0 <= existing_score <= 100:
        return existing_score

    # Prompt user for new score
    try:
        user_input = input(f"{question} (0-100): ")
        score = int(user_input)
    except (ValueError, TypeError):
        score = 0
    # Clamp between 0 and 100
    return max(0, min(100, score))
