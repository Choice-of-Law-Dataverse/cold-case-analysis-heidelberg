# ===== ABSTRACT =====
ABSTRACT_PROMPT = """
Your task is to extract the abstract from a court decision. Your response only consists of the abstract, with no explanations or additional information. The official abstract in the case is right at the beginning, often referred to with a specific term such as “Headnote”. If there is no dedicated abstract to be found, and only then, you must return a general description of the information in the file. It must be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less.\n\nCourt Decision Text:\n{text}\n\nThe abstract is:\n
"""

# ===== RELEVANT FACTS =====
FACTS_PROMPT = """
Your task is to extract and summarise the relevant facts from a court decision. Your response consists of the relevant facts only, no explanations or other additional information. You return a structured paragraph meaningful to private international law practitioners. The relevant facts summed up from the case must provide a concise account of the factual background that is essential to understanding the legal dispute, avoiding extraneous details. Relevant information includes who the parties are, what happened, what the dispute is about, and what the different stages of court proceedings are. Your response prioritizes information on choice of law and can only contain accurate information. Under no circumstances can you add assumptions that are not stated in the case. If any legal provisions are mentioned, use their English abbreviation.\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe relevant facts are:\n
"""

# ===== PIL PROVISIONS =====
PIL_PROVISIONS_PROMPT = """
Your task is to extract rules related to choice of law cited in a court decision. Your response is a list of provisions sorted by the impact of the rules for the choice of law issue(s) present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant provision usually comes from the citation of previous case law (precedents) from the same or from a foreign jurisdiction. It is also possible that principles or legislations are used. The output adheres to this format: ["provision_1", "provision_2", ...]. If you do not find PIL provisions in the court decision or if you are not sure, return ["NA"].\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe private international law provisions are:\n
"""

# ===== CHOICE OF LAW ISSUE =====
COL_ISSUE_PROMPT = """
Your task is to identify the main Private International Law issue from a court decision. Your response will be a concise question (usually a yes or no question). The issue you extract will have to do with Choice of Law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case, but rather the overall choice of law issue behind the case.\n\nThe issue in this case is related to this theme/these themes:\n{classification_definitions}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe issue is:\n
"""

# ===== COURT'S POSITION =====
COURTS_POSITION_PROMPT = """
Summarize the court's position on the choice-of-law issue(s) within the decision. Your response is phrased in a general way, generalizing the issue(s) so that your generalization could be applied to other private international law cases. The summary of the court’s position must be structured by (1) Majority Decisions, (2) Minority Decisions, and (3) Dissenting Opinions if the court decision contains any of them.\n\nYour output is a direct answer to the issue laid out here:\n{col_issue}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s):\n{classification}\n\nThe court's position is:\n
"""
