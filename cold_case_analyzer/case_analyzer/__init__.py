import os
import time
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
    def __init__(self, text, model):
        self.text = text
        self.model = model

    def get_abstract(self):
        prompt = load_prompt('abstract.txt')
        return extract_abstract(self.text, prompt, self.model)

    def get_relevant_facts(self):
        prompt = load_prompt('facts.txt')
        return extract_relevant_facts(self.text, prompt, self.model)

    def get_rules_of_law(self):
        prompt = load_prompt('rules.txt')
        return extract_rules_of_law(self.text, prompt, self.model)

    def get_choice_of_law_issue(self):
        classification_prompt = load_prompt('issue_classification.txt')
        prompt = load_prompt('issue.txt')
        return extract_choice_of_law_issue(self.text, classification_prompt, prompt, self.model)

    def get_courts_position(self):
        prompt = load_prompt('position.txt')
        return extract_courts_position(self.text, prompt, self.model)

    def analyze(self):
        """Runs all analysis methods and returns results in a dictionary."""
        start_time = time.time()
        results = {
            "Abstract": self.get_abstract(),
            "Relevant Facts": self.get_relevant_facts(),
            "Rules of Law": self.get_rules_of_law(),
            "Choice of Law Issue": self.get_choice_of_law_issue(),
            "Court's Position": self.get_courts_position(),
        }

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Format the elapsed time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        formatted_time = f"{int(hours)}h {int(minutes)}m {int(seconds)}s {int(milliseconds)}ms"
        
        print(f"Analyze function execution time: {formatted_time}")
        return results