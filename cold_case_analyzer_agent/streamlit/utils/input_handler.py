# Switch inputs to Streamlit widgets
import builtins
import streamlit as st
from typing import Callable
# add random int to key
import random

# core input function via Streamlit
def streamlit_input(prompt: str, key: str) -> str:
    """Use Streamlit widget: number_input for 0–100 prompts, text_input otherwise."""
    print("Now using Streamlit input handler with key: ", key)
    if "(0-100)" in prompt:
        value = st.number_input(prompt, min_value=0, max_value=100, value=0, key=key)
        return str(value)
    return st.text_input(prompt, key=key)
    st.session_state.messages.append({"role": "user", "content": prompt})
# override default
INPUT_FUNC: Callable[[str], str] = streamlit_input
# patch builtins.input so that all input() calls use our Streamlit function
builtins.input = INPUT_FUNC

def set_input_func(fn: Callable[[str], str]) -> None:
    """
    Override the global INPUT_FUNC.
    Call this once (in app.py) before anything else.
    """
    global INPUT_FUNC
    INPUT_FUNC = fn
    builtins.input = fn