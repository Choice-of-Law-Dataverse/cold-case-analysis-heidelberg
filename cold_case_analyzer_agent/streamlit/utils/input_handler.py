# Switch inputs to Streamlit widgets
import builtins
import streamlit as st
from typing import Callable, Optional
# add random int to key
import random

# core input function via Streamlit
def streamlit_input(prompt: str, key: Optional[str] = None) -> str:
    """
    Render a Streamlit widget for the prompt, then return its value as a str.
    If no key is supplied, we generate a random one so that multiple calls
    in the same render pass don’t collide.
    """
    if key is None:
        key = f"input_{random.randint(0, 1_000_000)}"

    # record prompt as a message
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    if "(0-100)" in prompt:
        val = st.number_input(prompt, min_value=0, max_value=100, value=0, key=key)
    else:
        val = st.text_input(prompt, key=key)

    # ensure it’s always a string
    return str(val)

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