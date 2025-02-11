import os
import time
from. col_section import extract_col_section
from .abstracts import extract_abstract
from .relevant_facts import extract_relevant_facts
from .rules_of_law import extract_rules_of_law
from .choice_of_law_issue import extract_choice_of_law_issue
from .courts_position import extract_courts_position


def load_prompt(filename):
    """Utility function to load a prompt from a text file in the prompts folder."""
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    filepath = os.path.join(prompts_dir, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


class CaseAnalyzer:
    def __init__(self, text, quote, model, concepts):
        self.text = text
        self.quote = quote
        self.model = model
        self.concepts = concepts

    def get_col_section(self):
        prompt = load_prompt("col_section.txt")
        return extract_col_section(self.text, prompt, self.model)

    def get_abstract(self, col_section):
        prompt = load_prompt("abstract.txt")
        return extract_abstract(self.text, col_section, prompt, self.model)

    def get_relevant_facts(self, col_section):
        prompt = load_prompt("facts.txt")
        return extract_relevant_facts(self.text, col_section, prompt, self.model)

    def get_rules_of_law(self, col_section):
        prompt = load_prompt("rules.txt")
        return extract_rules_of_law(self.text, col_section, prompt, self.model)

    def get_choice_of_law_issue(self, col_section):
        classification_prompt = load_prompt("issue_classification.txt")
        prompt = load_prompt("issue.txt")
        classification, choice_of_law_issue = extract_choice_of_law_issue(
            self.text,
            col_section,
            classification_prompt,
            prompt,
            self.model,
            self.concepts,
        )
        return classification, choice_of_law_issue

    def get_courts_position(self, coli, col_section):
        prompt = load_prompt("position.txt")
        return extract_courts_position(self.text, col_section, prompt, coli, self.model)

    def analyze(self):
        """Runs all analysis methods and returns results in a dictionary."""
        start_time = time.time()
        col_section = self.get_col_section()
        classification, coli = self.get_choice_of_law_issue(col_section)
        results = {
            """
            "Col Section": col_section,
            "Abstract": self.get_abstract(col_section),
            "Relevant Facts": self.get_relevant_facts(col_section),
            "Rules of Law": self.get_rules_of_law(col_section),
            "Choice of Law Issue Classification": classification,
            "Choice of Law Issue": coli,
            "Court's Position": self.get_courts_position(coli, col_section),
            """
            "Quote": col_section,
            "Abstract": self.get_abstract(col_section),
            "Relevant facts / Summary of the case": self.get_relevant_facts(col_section),
            "PIL provisions": self.get_rules_of_law(col_section),
            "Themes": classification,
            "Choice of law issue": coli,
            "Court's position": self.get_courts_position(coli, col_section),
        }

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Format the elapsed time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        formatted_time = (
            f"{int(hours)}h {int(minutes)}m {int(seconds)}s {int(milliseconds)}ms"
        )

        print(f"Analyze function execution time: {formatted_time}")
        return results
