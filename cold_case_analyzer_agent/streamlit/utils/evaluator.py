"""
Utility for prompting the user to evaluate generated output and return a score.
"""
from typing import Any, Dict
from utils.input_handler import INPUT_FUNC

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

    # Prompt user for new score until valid integer 0-100
    while True:
        user_input = INPUT_FUNC(f"{question} (0-100): ")
        try:
            score = int(user_input)
        except (ValueError, TypeError):
            print("Invalid input. Please enter an integer between 0 and 100.")
            continue
        if score < 0 or score > 100:
            print("Score must be between 0 and 100.")
            continue
        return score
