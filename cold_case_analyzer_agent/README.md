# CoLD Case Analyzer as an Agent

Implementing the CoLD case analyzer using LangGraph as an agent framework and building an interface that allows legal specialists to operate the LLM system.

## Project Structure

📦 cold_case_analyzer_agent
├── 📁 feedback_loops/              # Raw and processed data files
│   ├── 1_col_extractor.py          # Feedback loop for extracting the Choice of Law section
│   ├── 2_themes_classifier.py      # Feedback loop for classifying themes
│   └── 2_case_analyzer.py          # Feedback loop for the case law analysis
├── 📁 services/                    # Jupyter or Quarto notebooks
│   └── themes_extractor.py         # Retrieves data used as reference for classification into themes
├── .gitignore                      # Git ignore file
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
├── main.py                         # Source code
├── config.py                       # Import of environment variables
└── LICENSE                         # Project license
