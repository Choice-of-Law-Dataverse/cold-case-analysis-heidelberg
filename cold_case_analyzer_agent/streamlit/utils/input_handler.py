import builtins
from typing import Callable

# this will *hold* our real input() function
INPUT_FUNC: Callable[[str], str] = builtins.input

def set_input_func(fn: Callable[[str], str]) -> None:
    """
    Override the global INPUT_FUNC.
    Call this once (in app.py) before anything else.
    """
    global INPUT_FUNC
    INPUT_FUNC = fn