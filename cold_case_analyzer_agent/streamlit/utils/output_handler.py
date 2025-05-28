import builtins
import streamlit as st

def streamlit_output(message: str, key: str) -> None:
    """Display a message in Streamlit."""
    st.write(message)
    # Store the message in session state for later retrieval
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": message})

OUTPUT_FUNC: Callable[[str, str], None] = streamlit_output
builtins.print = OUTPUT_FUNC
def set_output_func(fn: Callable[[str, str], None]) -> None:
    """
    Override the global OUTPUT_FUNC.
    Call this once (in app.py) before anything else.
    """
    global OUTPUT_FUNC
    OUTPUT_FUNC = fn
    builtins.print = fn