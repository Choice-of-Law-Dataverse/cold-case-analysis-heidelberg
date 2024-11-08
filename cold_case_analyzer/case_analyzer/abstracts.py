from llm_handler.model_access import prompt_llama

def extract_abstract(text, prompt):
    prompt_abstract = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_llama(prompt_abstract)
