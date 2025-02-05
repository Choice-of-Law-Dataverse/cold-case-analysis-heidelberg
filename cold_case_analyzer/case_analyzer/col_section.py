from llm_handler.model_access import prompt_model


def extract_col_section(text, prompt, model):
    prompt_col_section = f"""{prompt}
    
                Here is the text of the Court Decision:
                {text}
                """
    return prompt_model(prompt_col_section, model)
