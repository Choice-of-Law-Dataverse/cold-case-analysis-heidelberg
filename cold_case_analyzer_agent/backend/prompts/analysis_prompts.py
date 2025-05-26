# ===== ABSTRACT =====
ABSTRACT_PROMPT = """
Your task is to extract the abstract from a court decision. Your response consists of the abstract only, no explanations or other additional information. The official abstract stated in the case is usually right at the beginning, sometimes called "Regeste". If the abstract is not in english, translate it to english. If there is no dedicated abstract to be found, and only then, you have to return a general description of the information in the file. It has to be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less. If there are any legal provisions mentioned, use their English name/abbreviation.\n\nCourt Decision Text:\n{text}\n\nThe abstract is:\n
"""

# ===== RELEVANT FACTS =====
FACTS_PROMPT = """
Your task is to extract and summarise the relevant facts from a court decision. Your response consists of the relevant facts only, no explanations or other additional information. You return a structured paragraph meaningful for private international law practitioners. The relevant facts summed up from the case must provide a concise account of the factual background that is essential to understanding the legal dispute, avoiding extraneous details. Relevant information includes who are the parties, what happened, what is the dispute about and what are the different stages of court proceedings. Your response prioritizes information on choice of law and can only contain accurate information. Under no circumstance can you add assumptions that are not stated in the case. If there are any legal provisions mentioned, use their English name/abbreviation.\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe relevant facts are:\n
"""

# ===== PIL PROVISIONS =====
PIL_PROVISIONS_PROMPT = """
Your task is to extract private international law provisions from a court decision that is related to choice of law. Your response is a list object of the provisions sorted by the impact of the rules for the choice of law issue present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant private international law provision usually stems from the most prominent legislation dealing with private international law in the respective jurisdiction. In Switzerland, for instance, it is usually the PILA. If there is no provision from such a prominent legislation found, double-check whether there is any other legal provision or another court decision, cited as a precedent, used in regards to the choice of law context in this court decision. The output adheres to this format: ["provision_1", "provision_2", ...]. If you do not find private international law provisions in the court decision or you are not sure, return [\\"NA\\"]. If any language other than English is used to describe a provision, use their English name/abbreviation.\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe private international law provisions are:\n
"""

# ===== CHOICE OF LAW ISSUE =====
COL_ISSUE_PROMPT = """
Your task is to identify the main Private International Law issue from a court decision. Your response will be a concise yes or no question. The issue you extract will have to do with Choice of Law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case, but rather the overall choice of law issue behind the case. If there are any legal provisions mentioned, use their English name/abbreviation.\n\nThe issue in this case is related to this theme/these themes: {classification_definitions}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe issue is:\n
"""

# ===== COURT'S POSITION =====
COURTS_POSITION_PROMPT = """
Summarize the court's position on the choice of law issue within a court decision. Your response is phrased in a general way, generalizing the issue so that it could be applied to other private international law cases. If there are any legal provisions mentioned, use their English name/abbreviation.
Your output is a direct answer to the issue laid out here:\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s): {classification}\n\nThe court's position is:\n
"""

