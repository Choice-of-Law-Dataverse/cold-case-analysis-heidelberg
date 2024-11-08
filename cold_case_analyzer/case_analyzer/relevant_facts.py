from llm_handler.model_access import prompt_llama

def extract_relevant_facts(text, prompt):
    prompt_facts = f"""Here is the text of a Court Decision:
                {text}
                {prompt}
                """
    return prompt_llama(prompt_facts)