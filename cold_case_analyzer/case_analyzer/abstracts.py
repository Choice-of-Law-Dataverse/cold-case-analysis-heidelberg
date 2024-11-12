from llm_handler.model_access import prompt_model

def extract_abstract(text, prompt, model):
    prompt_abstract = f"""{prompt}
    
                Court Decision:
                {text}
                """
    return prompt_model(prompt_abstract, model)
