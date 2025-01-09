## project structure
```
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
```
