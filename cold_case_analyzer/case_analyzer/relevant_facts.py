from llm_handler.model_access import prompt_model

def extract_relevant_facts(text, quote, prompt, model):
    prompt_facts = f"""{prompt}
    
                Here is the text of the Court Decision:
                {text}

                Here is the section of the Court Decision containing Choice of Law related information:
                {quote}
                """
    return prompt_model(prompt_facts, model)