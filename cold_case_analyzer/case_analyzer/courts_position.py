from llm_handler.model_access import prompt_model

def extract_courts_position(text, quote, prompt, issue, model):
    prompt_position = f"""{prompt}
                {issue}
    
                Here is the text of the Court Decision:
                {text}

                Here is the section of the Court Decision containing Choice of Law related information:
                {quote}
                """
    return prompt_model(prompt_position, model)
