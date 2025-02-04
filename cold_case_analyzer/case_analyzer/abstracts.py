from llm_handler.model_access import prompt_model


def extract_abstract(text, quote, prompt, model):
    prompt_abstract = f"""{prompt}
    
                Here is the text of the Court Decision:
                {text}

                Here is the section of the Court Decision containing Choice of Law related information:
                {quote}
                """
    return prompt_model(prompt_abstract, model)
