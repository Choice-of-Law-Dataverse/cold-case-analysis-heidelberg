from llm_handler.model_access import prompt_llama

def extract_courts_position(text, prompt):
    prompt_position = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_llama(prompt_position)
