from llm_handler.model_access import prompt_model

def extract_choice_of_law_issue(text, prompt, model):
    prompt_issue = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_model(prompt_issue, model)
