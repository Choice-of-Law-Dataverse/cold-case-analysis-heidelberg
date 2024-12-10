import pandas as pd
from fuzzywuzzy import process
from llm_handler.model_access import prompt_model

def classify_choice_of_law_issue(text, quote, classification_prompt, model, concepts):
    prompt_issue_classification = f"""{classification_prompt}
                    {concepts}

                    Here is the text of the Court Decision:
                    {text}

                    Here is the section of the Court Decision containing Choice of Law related information:
                    {quote}
                    """
    return prompt_model(prompt_issue_classification, model)

def extract_choice_of_law_issue(text, quote, classification_prompt, prompt, model, concepts):
    classification = classify_choice_of_law_issue(text, quote, classification_prompt, model, concepts)
    #print("This court decision has been classified as: ", classification)
    definition = concepts.loc[concepts['Keywords'] == process.extractOne(classification, concepts['Keywords'])[0], 'Definition'].values[0]
    #print("The definition of this classification is: ", definition)
    prompt_issue = f"""{prompt}
                The issue in this case is related to this theme: {classification}, which can be defined as: {definition}
    
                Here is the text of the Court Decision:
                {text}

                Here is the section of the Court Decision containing Choice of Law related information:
                {quote}
                """
    return classification, prompt_model(prompt_issue, model)
