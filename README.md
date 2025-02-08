# CoLD Case Analysis LLM
Consult the Choice of Law Dataverse (CoLD) [**Website**](https://www.choiceoflawdataverse.com/) to learn more about our main research project.

## How to run it on your machine?
1. Create a file for API secrets under ".env". Use the blueprint.env file for reference
2. Prepare the dataset under "cold_case_analyzer/data/cases.xlsx". Please note that you have to adhere to the given format with the pre-defined column names*
3. (Optional) Create a new virtual environment using `python -m venv .venv`
4. Install dependencies using `pip install -r requirements.txt`
5. Run the case analyzer using `python cold_case_analyzer/main.py`

\*Disclaimer note: It is still necessary to include a separate column with the "Quote"/the Choice of Law section of the original case text. We aim to make this column obsolete soon.

## What is the Case Analysis LLM?
An automated analysis of court decisions related to choice of law in international commercial contracts. From each court decision, we analyze the following categories:

| Category | Description | Task |
| --- | --- | --- |
| Abstract | Official abstract of the decision, otherwise AI-generated | Extraction |
| Relevant Facts | A short summary of the facts of the case (who the parties are, what happened, what the dispute is about, the different stages of court proceedings, etc.). This field prioritizes information on choice of law. | Extraction/Summarization |
| Relevant Rules of Law | The relevant legal provisions that are related to choice of law from the choice of law issue(s)/agreement/clause/interpretation(s). This field might also include important precedents or other decisions that were used as a reference in the judgment. | Extraction |
| Choice of Law Issue | Questions arising from the choice of law issue(s)/agreement/clause/interpretation(s) | Classification → Interpretation |
| Court’s Position | The opinion of the court in regard to the statements made in the "Choice of law issue" column. | Extraction/Interpretation |

## What is the Choice of Law Dataverse (CoLD)?
CoLD is a research project at the University of Lucerne, aiming to make Private International Law more accessible by developing and leveraging digital tools.

## Data
To develop the Case Analysis LLM, we used Swiss Court Decisions in the first iteration. Here is an overview of the cases used:

| **Nr.** | **ID**   | **Case**                                                                                                                                                   | **Year** | **Language** |
|---------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------|---------:|-------------:|
| 1       | CHE-1017 | [BGE 131 III 289](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F131-III-289%3Ade&lang=de&type=show_document)            | 2005     | DE           |
| 2       | CHE-1019 | [BGE 81 II 175](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F81-II-175%3Ade&lang=de&type=show_document)              | 1955     | DE           |
| 3       | CHE-1020 | [BGE 78 II 74](https://entscheide.weblaw.ch/dumppdf.php?link=BGE-78-II-74)                                                                                 | 1952     | FR          |
| 4       | CHE-1021 | [BGE 138 III 750](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F138-III-750%3Ade&lang=de&type=show_document) | 2012     | FR          |
| 5       | CHE-1022 | [BGer 4A 264/2008](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F23-09-2008-4A_264-2008&lang=de&type=show_document) | 2008     | FR          |
| 6       | CHE-1023 | [BGE 138 III 489](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F138-III-489%3Ade&lang=de&type=show_document) | 2012     | DE           |
| 7       | CHE-1024 | [BGer 4C.168/2006](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F11-09-2006-4C-168-2006&lang=de&type=show_document) | 2006     | DE           |
| 8       | CHE-1025 | [BGE 123 III 35](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F123-III-35%3Ade&lang=de&type=show_document)   | 1996     | DE           |
| 9       | CHE-1026 | [BGer 4A 394/2009](https://www.bger.ch/ext/eurospider/live/fr/php/aza/http/index.php?highlight_docid=aza://04-12-2009-4A_394-2009&lang=de&type=show_document) | 2009     | FR          |
| 10      | CHE-1027 | [BGE 128 III 201](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F128-III-201%3Ade&lang=de&type=show_document)            | 2002     | DE           |
| 11      | CHE-1028 | [BGE 132 III 285](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F132-III-285%3Afr&lang=fr&type=show_document)            | 2005     | DE           |
| 12      | CHE-1030 | [BGE 119 II 173](https://www.bger.ch/ext/eurospider/live/fr/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F119-II-173%3Afr&lang=fr&type=show_document) | 1993     | DE           |
| 13      | CHE-1033 | [BGE 130 III 620](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F130-III-620%3Ade&lang=de&type=show_document)            | 2004     | DE           |
| 14      | CHE-1034 | [BGE 136 III 392](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F136-III-392%3Ade&lang=de&type=show_document)            | 2010     | FR          |
| 15      | CHE-1035 | [BGer 4C.54/2000](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F19-01-2001-4C-54-2000&lang=de&type=show_document) | 2001     | FR          |
| 16      | CHE-1037 | [BGer 5C.68/2002](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F25-04-2002-5C-68-2002&lang=de&type=show_document) | 2002     | DE           |
| 17      | CHE-1038 | [BGE 111 II 175](http://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F111-II-175%3Ade&lang=de&type=show_document)             | 1985     | DE           |
| 18      | CHE-1039 | [BGE 111 IA 12](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F111-IA-12%3Ade&lang=de&zoom=&type=show_document) | 1985     | DE           |
| 19      | CHE-1040 | [BGer 4C.32/2001](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F07-05-2001-4C-32-2001&lang=de&type=show_document) | 2001     | DE           |
| 20      | CHE-1042 | [BGE 102 II 143](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F102-II-143%3Ade&lang=it&type=show_document)  | 1976     | DE           |
| 21      | CHE-1043 | [BGE 119 II 264](http://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F119-II-264%3Ade&lang=de&type=show_document)             | 1993     | DE           |
| 22      | CHE-1044 | [BGE 117 II 494](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F117-II-494%3Ade&lang=de&type=show_document)  | 1991     | DE           |
| 23      | CHE-1045 | [BGer 4A 227/2009](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F28-07-2009-4A_227-2009&lang=de&type=show_document) | 2009     | FR          |
| 24      | CHE-1050 | [BGE 80 II 179](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F80-II-179%3Ade&lang=de&zoom=&type=show_document)  | 1954     | FR          |
| 25      | CHE-1051 | [BGE 91 II 44](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F91-II-44%3Ade&lang=de&zoom=&type=show_document)   | 1965     | DE           |
| 26      | CHE-1314 | [BGE 133 III 90](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F133-III-90%3Afr&lang=fr&type=show_document)            | 2006     | DE           |
| 27      | CHE-1319 | [BGer 4A 15/2024](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=aza%3A%2F%2F18-04-2024-4A_15-2024&lang=de&type=show_document) | 2024     | DE           |
| 28      | CHE-1320 | [BGer 4A 120/2022](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza://26-10-2021-4A_133-2021&lang=de&zoom=&type=show_document) | 2022     | FR          |
| 29      | CHE-1327 | [BGer 4A 133/2021; BGer 4A 135/2021](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza://26-10-2021-4A_133-2021&lang=de&zoom=&type=show_document) | 2021     | FR          |
| 30      | CHE-1328 | [BGer 4A 543/2018](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2Faza://28-05-2019-4A_543-2018&lang=de&zoom=&type=show_document) | 2019     | DE           |
| 31      | CHE-1331 | [BGer 4A 559/2022](https://www.bger.ch/ext/eurospider/live/fr/php/aza/http/index.php?highlight_docid=aza://03-08-2023-4A_559-2022&lang=fr&zoom=&type=show_document) | 2023     | DE           |
| 32      | CHE-1332 | [BGer 4C.458/2004](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?lang=de&type=show_document&highlight_docid=aza://17-05-2005-4C-458-2004) | 2005     | IT           |
| 33      | CHE-1333 | [BGE 140 III 473](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F140-III-473%3Ade&lang=de&type=show_document)            | 2014     | DE           |
