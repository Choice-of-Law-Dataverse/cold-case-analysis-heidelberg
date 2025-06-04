import json
import re
import time

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from config import llm, thread_id
from prompts.pil_theme_prompt import PIL_THEME_PROMPT
from utils.themes_extractor import THEMES_TABLE_STR


def theme_classification_node(state):
    # mirror extract_col_section pattern for theme classification
    print("\n--- THEME CLASSIFICATION ---")
    text = state["full_text"]
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    # bump iteration counter
    iter_count = state.get("theme_eval_iter", 0) + 1
    state["theme_eval_iter"] = iter_count
    # build prompt
    prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)
    # add previous classification if exists
    existing = state.get("classification", [])
    if existing:
        prev = existing[-1]
        if prev:
            prompt += f"\n\nPrevious classification: {prev}\n"
    # invoke LLM
    print(f"\nPrompting LLM with:\n{prompt}\n")
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="You are an expert in private international law"),
        HumanMessage(content=prompt)
    ])
    theme_time = time.time() - start_time
    # parse classification list
    try:
        cls_list = json.loads(response.content)
    except Exception:
        cls_list = [response.content.strip()]
    # convert to string for display
    cls_str = ", ".join(str(item) for item in cls_list)
    print(f"\nClassified theme(s): {cls_list}\n")
    # append classification
    state.setdefault("classification", []).append(cls_str)
    # return updated lists
    return {
        "classification": state["classification"],
        "theme_feedback": state.get("theme_feedback", []),
        "theme_classification_time": theme_time
    }
