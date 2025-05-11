
def text_input_node(state):
    """Handles the initial text input."""
    print("--- TEXT INPUT NODE ---")
    # In a real application, this node might load text from a file or UI.
    # For this example, we assume 'full_text' is already in the initial state.
    if not state.get("full_text"):
        raise ValueError("full_text not provided in the initial state.")
    print(f"Received full_text (first 100 chars): {state.get('full_text')[:100]}...")
    return {"full_text": state.get("full_text")}
