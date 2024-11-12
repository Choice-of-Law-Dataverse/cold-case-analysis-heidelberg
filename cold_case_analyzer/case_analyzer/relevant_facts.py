from llm_handler.model_access import prompt_model

def extract_relevant_facts(text, prompt, model):
    prompt_facts = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_model(prompt_facts, model)