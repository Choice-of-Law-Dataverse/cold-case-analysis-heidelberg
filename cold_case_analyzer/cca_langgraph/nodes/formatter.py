
def present_analysis_result_node(state):
    """Node to compile and present the final analysis."""
    print("--- PRESENT ANALYSIS RESULT NODE ---")
    
    abstract = state.get("abstract", "N/A")
    relevant_facts = state.get("relevant_facts", "N/A")
    pil_provisions = state.get("pil_provisions", ["N/A"])
    col_issue = state.get("col_issue", "N/A")
    courts_position = state.get("courts_position", "N/A")

    formatted_output = f"""
## Abstract
{abstract}

## Relevant Facts
{relevant_facts}

## Applicable Provisions
{', '.join(pil_provisions) if isinstance(pil_provisions, list) else pil_provisions}

## Main Issue
{col_issue}

## Court's Position
{courts_position}
"""
    print("\n--- FINAL ANALYSIS ---")
    print(formatted_output)
    print("--- END OF ANALYSIS ---")
    
    # This node would typically lead to the final user feedback loop
    # For now, it will just store the formatted output.
    return {"formatted_analysis": formatted_output}
