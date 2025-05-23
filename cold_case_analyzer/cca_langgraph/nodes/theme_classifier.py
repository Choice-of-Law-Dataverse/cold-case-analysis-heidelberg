from tools.pil_theme import pil_theme_tool

def theme_classification_node(state, llm_instance):
    """Node to call the pil_theme_tool."""
    print("--- THEME CLASSIFICATION NODE ---")
    full_text = state.get("full_text")
    quote = state.get("quote")
    themes_table = state.get("themes_table") # This needs to be loaded into the state

    if not all([full_text, quote, themes_table]):
        raise ValueError("Missing full_text, quote, or themes_table in state for theme classification.")

    result = pil_theme_tool.invoke({
        "text": full_text, 
        "quote": quote, 
        "themes_table": themes_table, 
        "llm": llm_instance
    })
    print(f"Classified themes: {result.get('classification')}")
    return {"classification": result.get("classification")}
