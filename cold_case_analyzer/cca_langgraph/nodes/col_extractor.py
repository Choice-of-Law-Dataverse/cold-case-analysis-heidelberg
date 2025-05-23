from tools.col_section import col_section_tool

def col_extraction_node(state, llm_instance):
    """Node to call the col_section_tool."""
    print("--- COL EXTRACTION NODE ---")
    full_text = state.get("full_text")
    if not full_text:
        raise ValueError("full_text not found in state for CoL extraction.")
    
    # Get refinement hints if they exist (from a previous loop)
    # refinement_hints = state.get("col_refinement_hints", "") 
    # The tool itself doesn't explicitly take hints in its current signature,
    # but the prompt could be dynamically adjusted if hints were provided.

    result = col_section_tool.invoke({"text": full_text, "llm": llm_instance})
    print(f"Extracted CoL section: {result.get('quote')}")
    return {"quote": result.get("quote")}
