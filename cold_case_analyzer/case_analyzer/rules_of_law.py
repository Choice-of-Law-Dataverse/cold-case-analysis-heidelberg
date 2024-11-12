from llm_handler.model_access import prompt_model

def extract_rules_of_law(text, prompt, model):
    prompt_rules = f"""{prompt}
    
                Here is the text of the Court Decision:
                {text}
                """
    return prompt_model(prompt_rules, model)
