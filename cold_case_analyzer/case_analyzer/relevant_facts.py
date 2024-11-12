from llm_handler.model_access import prompt_model

def extract_relevant_facts(text, prompt, model):
    prompt_facts = f"""{prompt}
    
                Here is the text of the Court Decision:
                {text}
                """
    return prompt_model(prompt_facts, model)