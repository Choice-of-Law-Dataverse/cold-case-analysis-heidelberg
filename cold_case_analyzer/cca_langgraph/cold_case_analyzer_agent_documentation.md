# LangGraph AI Agent for Court Decision Analysis

This documentation provides detailed technical guidance for developing an AI Agent based on LangGraph. The agent is designed to process the full text of court decisions and produce a structured, user-interactive analysis of choice of law (CoL) issues.

## Overview

### Goal
The agent analyzes a court decision by:
1. Extracting the Choice of Law section.
2. Validating the extraction with the user.
3. Classifying the decision into predefined themes.
4. Validating the classification with the user.
5. Performing a five-part analytical breakdown using specialized prompts.
6. Presenting the full analysis and incorporating iterative user feedback.

### Core Technologies
- LangGraph for agent flow orchestration
- LangChain for LLM-based tool calls
- Interrupt handling for human-in-the-loop feedback
- Python for backend logic and orchestration

### Workflow Overview

1. Text Input Node
- Input `full_text` (str) - The entire court decision as raw text.
- Output: Forwarded to the CoL extraction tool.

2. Tool: `col_section`
- Prompt logic: Uses rule-based pattern matching & semantic search to extract the CoL section from the text.
- Inputs:
    - {text}: Full decision text
- Output:
     {quote}: Extracted CoL section (1–2 paragraphs, verbatim)

3. User Feedback Node (Interrupt)
- Prompt user: "Is this the correct Choice of Law section? Would you like to refine it?"
- Logic:
    - If user refines: loop back to col_section (with updated hints if needed)
    - If confirmed: continue to classification

4. Tool: pil_theme
- Purpose: Classifies the case based on its CoL issue.
- Inputs:
    - {text}: Full decision text
    - {quote}: Extracted CoL section
    - {themes_table}: List of themes with definitions and keywords
- Output:
    - ["Theme 1", "Theme 2"] (one or more from predefined theme list)

5. User Feedback Node (Interrupt)
- Prompt user: "Do these themes reflect the main issue of the case? Want to modify or refine them?"
- Logic:
    - If refinement needed: loop back to pil_theme
    - If confirmed: continue to deep analysis

6. Five-Part Legal Analysis
Executed in sequence, all tools receive:
- {text}: Full decision text
- {quote}: Extracted CoL section
- Additional inputs (e.g. classification) when required

Tool: abstract
- Output: One concise paragraph summarizing the case or a translated Regeste.

Tool: relevant_facts
- Output: Structured summary of facts essential to PIL/CoL.

Tool: pil_provisions
- Output: ["Provision 1", "Provision 2"] — sorted by relevance.
- Use English names for provisions.

Tool: col_issue
- Input: {classification} (themes)
- Output: A general Yes/No PIL-style issue in question form.

Tool: courts_position
- Input: {col_issue}
- Output: The court's general position on the identified CoL issue.

7. Formatted Output Presentation
- Agent compiles outputs into a structured document with headers:
```
## Abstract
[abstract output]

## Relevant Facts
[relevant_facts output]

## Applicable Provisions
[pil_provisions output]

## Main Issue
[col_issue output]

## Court's Position
[courts_position output]
```

8. User Feedback Loop
- Prompt user: “Here is the full legal analysis. Would you like to modify any of the sections?”
- User selects any of the 5 analysis types to refine.
- Agent reruns the corresponding tool(s).
- Loop continues until the user explicitly confirms completion.

---

## LangGraph Flow Configuration

```python
from langgraph.graph import StateGraph
from langgraph.graph.schema import Schema

# Define schema
class CourtAnalysisSchema(Schema):
    text: str
    quote: str
    classification: list[str]
    user_approved: bool

# Define the graph
workflow = StateGraph(CourtAnalysisSchema)
workflow.add_node("col_section", col_section_tool)
workflow.add_node("ask_user_col_confirmation", interrupt_for_col_validation)
workflow.add_node("pil_theme", pil_theme_tool)
workflow.add_node("ask_user_theme_confirmation", interrupt_for_theme_validation)
workflow.add_node("abstract", abstract_tool)
workflow.add_node("relevant_facts", relevant_facts_tool)
workflow.add_node("pil_provisions", pil_provisions_tool)
workflow.add_node("col_issue", col_issue_tool)
workflow.add_node("courts_position", courts_position_tool)
workflow.add_node("present_result", present_analysis_result)

workflow.set_entry_point("col_section")
workflow.add_edge("col_section", "ask_user_col_confirmation")
workflow.add_conditional_edges(
    "ask_user_col_confirmation",
    condition=lambda state: "continue" if state.user_approved else "col_section"
)
workflow.add_edge("ask_user_col_confirmation/continue", "pil_theme")
workflow.add_edge("pil_theme", "ask_user_theme_confirmation")
workflow.add_conditional_edges(
    "ask_user_theme_confirmation",
    condition=lambda state: "continue" if state.user_approved else "pil_theme"
)
workflow.add_edge("ask_user_theme_confirmation/continue", "abstract")
workflow.add_edge("abstract", "relevant_facts")
workflow.add_edge("relevant_facts", "pil_provisions")
workflow.add_edge("pil_provisions", "col_issue")
workflow.add_edge("col_issue", "courts_position")
workflow.add_edge("courts_position", "present_result")

app = workflow.compile()
```

---

## Tool Descriptions and Prompts

### 1. `col_section`
**Purpose:** Extracts the Choice of Law section.
**Prompt:**
```
Your task is to identify and extract the Choice of Law section from the original text of a court decision. To find and extract the choice of law section from a court decision, first, scan the headings and section titles for any terms that might be related to private international law. If no explicit section exists, search the text for key phrases such as "this dispute shall be governed by," "under the laws of," "according to the law of," or references to private international law principles. Once identified, extract the relevant passages, ensuring they include any reasoning, statutory references, or precedents used by the court to determine the applicable law. You can return a maximum of two paragraphs. Most likely, it will be just one. In any case, it has to be a perfect copy of the text you find in the original version of the court decision.

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

### 2. `interrupt_for_col_validation`
**Purpose:** Interrupt to ask the user to confirm the correctness of the CoL extraction.

### 3. `pil_theme`
**Purpose:** Classifies the decision into one or more predefined themes.
**Prompt:**
```
Your task is to assign specific themes to a court decision. Your response consists of the most fitting value(s) from the "Keywords" column in the format \"keyword\". You assign the themes by finding the choice of law issue from the court decision and figuring out which Definition fits most. THE OUTPUT HAS TO BE ONE OR MULTIPLE OF THE VALUES FROM THE TABLE. Your output should adhere to the following format:
"["Theme 1", "Theme 2"]"

Here is the table with all keywords and their definitions:
{themes_table}

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

### 4. `interrupt_for_theme_validation`
**Purpose:** Asks the user whether the theme classification is appropriate.

### 5. `abstract`
**Prompt:**
```
Your task is to extract the abstract from a court decision. Your response consists of the abstract only, no explanations or other additional information. The official abstract stated in the case is usually right at the beginning, sometimes called "Regeste". If the abstract is not in english, translate it to english. If there is no dedicated abstract to be found, and only then, you have to return a general description of the information in the file. It has to be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less.
If there are any legal provisions mentioned, use their English name/abbreviation.

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

### 6. `relevant_facts`
**Prompt:**
```
Your task is to extract and summarise the relevant facts from a court decision. Your response consists of the relevant facts only, no explanations or other additional information. You return a structured paragraph meaningful for private international law practitioners. The relevant facts summed up from the case must provide a concise account of the factual background that is essential to understanding the legal dispute, avoiding extraneous details. Relevant information includes who are the parties, what happened, what is the dispute about and what are the different stages of court proceedings. Your response prioritizes information on choice of law and can only contain accurate information. Under no circumstance can you add assumptions that are not stated in the case. If there are any legal provisions mentioned, use their English name/abbreviation.

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

### 7. `pil_provisions`
**Prompt:**
```
Your task is to extract rules of law from a court decision that is related to choice of law. Your response is a list object of the rules of law sorted by the impact of the rules for the choice of law issue present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant rule of law usually stems from the most prominent legislation dealing with private international law in the respective jurisdiction. In Switzerland, for instance, it is usually the PILA. If there is no provision from such a prominent legislation found, double-check whether there is any other legal provision or another court decision, cited as a precedent, used in regards to the choice of law context in this court decision. The output adheres to this format: ["provision_1", "provision_2", ...]. If you do not find rules of law in the court decision or you are not sure, return [\"NA\"]. If any language other than English is used to describe a provision, use their English name/abbreviation.

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

### 8. `col_issue`
**Prompt:**
```
Your task is to identify the main Private International Law issue from a court decision. Your response will be a concise yes or no question. The issue you extract will have to do with Choice of Law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case, but rather the overall choice of law issue behind the case. If there are any legal provisions mentioned, use their English name/abbreviation.
The issue in this case is related to this theme: {classification}, which can be defined as: {definition}

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

### 9. `courts_position`
**Prompt:**
```
Summarize the court's position on the choice of law issue within a court decision. Your response is phrased in a general way, generalizing the issue so that it could be applied to other private international law cases. If there are any legal provisions mentioned, use their English name/abbreviation.
Your output is a direct answer to the issue laid out here:

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
{quote}
```

## Suggested Directory Structure
```
/langgraph_agent/
├── main.py
├── graph_config.py
├── nodes/
│   ├── input_node.py
│   ├── col_extractor.py
│   ├── theme_classifier.py
│   ├── analysis_runner.py
│   ├── formatter.py
│   └── interrupt_handler.py
├── tools/
│   ├── col_section.py
│   ├── pil_theme.py
│   ├── abstract_tool.py
│   ├── facts_tool.py
│   ├── provisions_tool.py
│   ├── col_issue_tool.py
│   └── courts_position_tool.py
└── prompts/
    └── prompt_templates.py
```