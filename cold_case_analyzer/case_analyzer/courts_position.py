from llm_handler.model_access import prompt_model

def extract_courts_position(text, prompt, issue, model):
    prompt_position = f"""{prompt}

                {issue}
    
                Here is the text of the Court Decision:
                {text}
                """
    return prompt_model(prompt_position, model)
