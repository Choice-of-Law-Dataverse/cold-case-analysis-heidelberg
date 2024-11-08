import os
from .abstracts import extract_abstract
from .relevant_facts import extract_relevant_facts
from .rules_of_law import extract_rules_of_law
from .choice_of_law_issue import extract_choice_of_law_issue
from .courts_position import extract_courts_position

def load_prompt(filename):
    """Utility function to load a prompt from a text file in the prompts folder."""
    prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
    filepath = os.path.join(prompts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

class CaseAnalyzer:
    def __init__(self, text):
        self.text = text

    def get_abstract(self):
        prompt = load_prompt('abstract.txt')
        return extract_abstract(self.text, prompt)

    def get_relevant_facts(self):
        prompt = load_prompt('facts.txt')
        return extract_relevant_facts(self.text, prompt)

    def get_rules_of_law(self):
        prompt = load_prompt('rules.txt')
        return extract_rules_of_law(self.text, prompt)

    def get_choice_of_law_issue(self):
        prompt = load_prompt('issue.txt')
        return extract_choice_of_law_issue(self.text, prompt)

    def get_courts_position(self):
        prompt = load_prompt('position.txt')
        return extract_courts_position(self.text, prompt)

    def analyze(self):
        """Runs all analysis methods and returns results in a dictionary."""
        return {
            "Abstract": "mock abstract",#self.get_abstract(),
            "Relevant Facts": "mock facts",#self.get_relevant_facts(),
            "Rules of Law": "mock rules",#self.get_rules_of_law(),
            "Choice of Law Issue": "mock issue",#self.get_choice_of_law_issue(),
            "Court's Position": "mock position",#self.get_courts_position(),
        }
