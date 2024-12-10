# cold-case-analysis-llm
automated analysis of court decisions

| Category | Description | Task |
| --- | --- | --- |
| Abstract | Official abstract of the decision, otherwise AI-generated | Extraction |
| Relevant Facts | A short summary of the facts of the case (who are the parties, what happened, what is the dispute about, the different stages of court proceedings, etc.). This field prioritizes information on choice of law. | Extraction/Summarization |
| Relevant Rules of Law | The relevant legal provisions that are related to choice of law from the choice of law issue(s)/agreement/clause/interpretation(s). This field might also include important precedents or other decisions that were used as a reference in the judgment. | Extraction |
| Choice of Law Issue | Questions arising from the choice of law issue(s)/agreement/clause/interpretation(s) | Classification → Interpretation |
| Court’s Position | The opinion of the court in regard to the statements made in the "Choice of law issue" column. | Extraction/Interpretation |

## project structure

├── cold_case_analyzer/  
│   ├── config.py  
│   ├── main.py  
│   ├── case_analyzer/  
│   │   ├── __init__.py  
│   │   ├── abstracts.py  
│   │   ├── relevant_facts.py  
│   │   ├── rules_of_law.py  
│   │   ├── choice_of_law_issue.py  
│   │   └── courts_position.py  
│   ├── data_handler/  
│   │   ├── __init__.py  
│   │   └── airtable_retrieval.py  
│   ├── llm_handler/  
│   │   ├── __init__.py  
│   │   ├── fine_tuning.py  
│   │   └── model_access.py  
│   ├── prompts/  
│   │   ├── abstract.txt  
│   │   ├── facts.txt  
│   │   ├── rules.txt  
│   │   ├── issue.txt  
│   │   ├── issue_classification.txt  
│   │   └── position.txt  
