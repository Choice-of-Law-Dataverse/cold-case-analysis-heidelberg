from llm_handler.model_access import prompt_model

def extract_courts_position(text, prompt, model):
    prompt_position = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_model(prompt_position, model)
