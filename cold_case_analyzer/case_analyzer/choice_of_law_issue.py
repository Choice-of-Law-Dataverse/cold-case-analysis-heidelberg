from llm_handler.model_access import prompt_llama

def extract_choice_of_law_issue(text, prompt):
    prompt_issue = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_llama(prompt_issue)
