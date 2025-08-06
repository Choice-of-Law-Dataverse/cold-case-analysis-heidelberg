# ===== RELEVANT FACTS =====
FACTS_PROMPT = """
TASK: Extract and synthesize factual elements essential for understanding the choice of law analysis into a single, coherent paragraph.
INSTRUCTIONS:
1.	Output Requirement: 
Provide exactly ONE paragraph containing all relevant facts in narrative form.
2.	Content Priority:
Elaborate on facts including, but not limited to the following, as long as they are relevant for the private international law (PIL) and choice of law discussion in the decision: 
-	Party characteristics (nationality, domicile, place of business/incorporation)
-	Nature and geography of the underlying transaction/relationship
-	Express or implied choice of law indicators
-	Specific circumstances that created the choice of law issue
3.	Writing Guidelines: 
-	Use flowing, connected sentences rather than listing facts in points
-	Employ transitional phrases to link different factual elements
-	Maintain chronological or logical progression 
-	Keep sentences concise but substantive
4.	Inclusion Standards: 
-	Include: Connecting factors, transactional geography, choice of law clauses, foreign law invocations, conflict triggers
-	Exclude: Specific amounts, exact dates, individual names, procedural details, unrelated contract terms
5.	OUTPUT FORMAT:
**FACTS:**
[Single paragraph containing all essential facts in narrative form, explaining the international elements and circumstances that necessitated choice of law analysis.]
6.	CONSTRAINT:
Base the factual narrative solely on the provided judgment text, synthesizing information from both the full text and extracted choice of law section.
\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe facts are:\n
"""

# ===== PIL PROVISIONS =====
PIL_PROVISIONS_PROMPT = """
Your task is to extract rules related to choice of law cited in a court decision. Your response is a list of provisions sorted by the impact of the rules for the choice of law issue(s) present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant provision usually stems from the most prominent legislation dealing with private international law in the respective jurisdiction. In Switzerland, for instance, it is usually the PILA. If no legislative provision is found, double-check whether there is any other court decision cited as a choice of law precedent. The output adheres to this format: ["provision_1", "provision_2", ...]. If you do not find PIL provisions in the court decision or if you are not sure, return ["NA"]. If any language other than English is used to cite a provision, use their English abbreviation.\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe private international law provisions are:\n
"""

# ===== CHOICE OF LAW ISSUE =====
COL_ISSUE_PROMPT = """
Your task is to identify the main private international law issue from a court decision. Your response will be a concise yes-no question. The issue you extract will have to do with choice of law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case but rather the overall choice-of-law issue behind the case. If any legal provisions are mentioned, use their English abbreviation.\n\nThe issue in this case is related to this theme/these themes:\n{classification_definitions}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe issue is:\n
"""

# ===== COURT'S POSITION =====
COURTS_POSITION_PROMPT = """
Summarize the court's position on the choice-of-law issue(s) within the decision. Your response is phrased in a general way, generalizing the issue(s) so that your generalization could be applied to other private international law cases. If any legal provisions are mentioned, use their English abbreviation. Your output is a direct answer to the issue laid out here:\n{col_issue}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s):\n{classification}\n\nThe court's position is:\n
"""

# ===== ABSTRACT =====
ABSTRACT_PROMPT = """
Your task is to extract the abstract from a court decision. Your response only consists of the abstract, with no explanations or additional information. The official abstract in the case is right at the beginning, usually called "Regeste". Please translate this section into English. If there is no dedicated abstract to be found, and only then, you have to return a general description of the information in the file. It has to be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less. If any legal provisions are mentioned, use their English abbreviation.\n\nCourt Decision Text:\n{text}\n\nThe abstract is:\n
"""
