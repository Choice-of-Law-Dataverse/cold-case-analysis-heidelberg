# ===== ABSTRACT =====
ABSTRACT_PROMPT = """
Your task is to extract the abstract from a court decision. Your response only consists of the abstract, with no explanations or additional information. The official abstract in the case is right at the beginning, often referred to with a specific term such as “Headnote” or “Case Note”. At times it might just be printed in bold at the start of the judgment without any specific title.  If there is no dedicated abstract to be found, and only then, you must return a general description of the information in the file. It must be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less.\nCourt Decision Text:\n{text}\n\nThe abstract is:\n
"""

# ===== RELEVANT FACTS =====
FACTS_PROMPT = """
Your task is to extract and summarise the relevant facts from a court decision. Your response consists of the relevant facts only, no explanations or other additional information. You return a structured paragraph meaningful to private international law practitioners. The relevant facts summed up from the case must provide a concise account of the factual background that is essential to understanding the legal dispute, avoiding extraneous details. Relevant information includes who the parties are, what happened, what the dispute is about, and what the different stages of court proceedings are. Your response prioritizes information on choice of law and can only contain accurate information. Under no circumstances can you add assumptions that are not stated in the case. If any legal provisions are mentioned, use their English abbreviation.\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe relevant facts are:\n
"""

# ===== PIL PROVISIONS =====
PIL_PROVISIONS_PROMPT = """
Your task is to extract rules related to choice of law cited in a court decision. Your response is a list of provisions sorted by the impact of the rules for the choice of law issue(s) present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant provision usually comes from the citation of previous case law (precedents) from the same or from a foreign jurisdiction. It always has to be related to the choice of law issue. It is also possible that principles or legislations are used. The output adheres to this format: ["provision_1", "provision_2", ...]. If you do not find PIL provisions in the court decision or if you are not sure, return ["NA"].\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe private international law provisions are:\n
"""

# ===== CHOICE OF LAW ISSUE =====
COL_ISSUE_PROMPT = """
Your task is to identify the main Private International Law issue  from a court decision. Your response will be a concise question (usually a yes or no question). The issue you extract will have to do with Choice of Law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case, but rather the overall choice of law issue behind the case.\nThe issue in this case is related to this theme/these themes:\n{classification_definitions}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe issue is:\n
"""

# ===== COURT'S POSITION =====
COURTS_POSITION_RATIO_DECIDENDI_PROMPT = """
Summarize the court's position on the choice-of-law issue(s) within the decision. Your response is phrased in a general way, generalizing the issue(s) so that your generalization could be applied to other private international law cases. The summary of the court’s position must be structured by (1) Majority Decisions, (2) Minority Decisions, and (3) Dissenting Opinions  if the court decision contains any of them.\nYour output is a direct answer to the issue laid out here:\n{col_issue}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s):\n{classification}\n\nThe court's position is:\n
"""

COURTS_POSITION_OBITER_DICTA_PROMPT = """
TASK: Extract judicial observations about choice of law that are not essential to the court's decision but provide persuasive legal commentary.
INSTRUCTIONS:
1.	Obiter Identification Method: 
-	Apply the inversion test: Could the court have reached the same decision if this statement were omitted or reversed?
-	If yes, the statement is obiter dicta
-	Focus on legal propositions, principles, or methodological observations, not factual findings
2.	PIL-Relevant Obiter Categories: 
-	Alternative choice of law approaches the court considered but didn't apply
-	Comparative observations about foreign private international law (PIL) systems or practices
-	Commentary on the development or future direction of Indian PIL
-	Hypothetical scenarios or broader applications beyond the case facts
-	Judicial observations about PIL methodology or theoretical frameworks
-	Commentary on party autonomy principles not directly applied
3.	Content Requirements: 
-	Include only substantive legal observations, not casual remarks or procedural comments
-	Extract statements that could influence future PIL reasoning, even if not binding
-	Focus on the court's legal analysis, not factual characterizations or case-specific applications
-	Exclude pure policy discussions unless they contain legal principles
4.	Output Specifications: 
-	Present each obiter observation clearly and concisely
-	Use the court's language where possible, but may paraphrase for clarity
-	If no relevant obiter exists, state: "No obiter dicta on choice of law issues identified"
-	Organize multiple obiter statements logically (by topic or sequence in judgment)
5.	OUTPUT FORMAT:
**OBITER DICTA:**
[Legal observation 1 - court's non-essential commentary on PIL/choice of law]

[Legal observation 2 - if applicable]
6.	CONSTRAINT: Extract only judicial commentary from the provided judgment text that relates to PIL methodology or choice of law principles but was not necessary for the court's actual decision.
"""

COURTS_POSITION_DISSENTING_OPINIONS_PROMPT = """
TASK: Identify and summarize any dissenting or minority judicial opinions specifically related to choice of law analysis.
INSTRUCTIONS:
1.	Scope of Analysis: 
-	Focus only on disagreements about private international law (PIL) methodology, choice of law principles, or applicable law determination
-	Exclude dissents on unrelated procedural, jurisdictional, or substantive law matters
-	Include concurring opinions that reach the same result through different PIL reasoning
2.	Content Extraction: 
-	Judge's name/designation (if provided)
-	Core PIL disagreement with the majority approach
-	Alternative choice of law methodology or principle proposed
-	Different conclusion about applicable law (if any)
3.	Analysis Requirements: 
-	Distinguish between methodological disagreements (how to determine applicable law) and application disagreements (which law applies)
-	Focus on legal reasoning differences and methodological disagreements, not factual disputes
-	Capture the essence of alternative PIL approaches suggested
4.	Output Standards: 
-	Provide concise but complete summary of each dissenting PIL position
-	If multiple dissents exist, address each separately
-	If partial agreement exists, specify areas of PIL agreement vs. disagreement
5.	OUTPUT FORMAT:
**DISSENTING/MINORITY OPINIONS:**
[Judge name (if provided)]: [Summary of PIL disagreement and alternative approach]
OR
"No dissenting opinion or minority opinion on the choice of law issue."
6.	CONSTRAINT: Extract only from the provided judgment text, focusing exclusively on choice of law disagreements while ignoring dissents on other legal issues.
"""