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
TASK: Extract only the legal authorities that the court actually used to support its choice of law reasoning and decision.
INSTRUCTIONS:
1.	Inclusion Standard: Include authorities only where the court: 
-	Applied the authority's principle to reach its conclusion
-	Adopted the authority's reasoning as part of its analysis
-	Used the authority to interpret or clarify legal principles
-	Distinguished or followed the authority's approach
-	If no textbooks/academic sources, and/or statutory provisions have been cited, then do not output these headings.
2.	Authority Categories: 
-	Judicial Decisions: Indian and foreign cases the court followed, distinguished, or applied
-	Textbooks/Treatises: Academic sources (Dicey, Cheshire, etc.) the court cited for legal principles
-	Statutory Provisions: Specific legislative rules the court applied
-	Legal Principles: Established doctrines or tests the court referenced.
3.	Usage Description Requirements: 
-	For Cases: List case name only. Include citations only if provided in the judgment. (no usage explanation needed)
-	For Textbooks/Academic Sources: List names. Provide one-line explanation of how used for each.
-	For Statutory Provisions: List provision only (no usage explanation needed)
4.	Exclusions: 
-	Authorities cited by parties/counsel unless court adopted their reasoning
-	Cases mentioned for historical context without direct application
-	Authorities cited but not used in the court's actual reasoning
-	General legal background citations not supporting the specific decision
5.	OUTPUT FORMAT:
**LEGAL AUTHORITIES RELIED UPON:**

**Judicial Precedents:**
-	[Case name 1]
-	[Case name 2]
**Textbooks/Academic Sources:**
-	[Source]: [Brief explanation of how court used it]
**Statutory Provisions:**
-	[Provision name/section]
6.	CONSTRAINT: Extract only from the court's own reasoning in the provided judgment text, focusing on authorities that directly supported the choice of law analysis and conclusion.
\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe authorities are:\n
"""

# ===== CHOICE OF LAW ISSUE =====
COL_ISSUE_PROMPT = """
TASK: Identify the specific choice of law questions that the court actually decided in this private international law (PIL) case. 
INSTRUCTIONS:
1.	Issue Identification Criteria: 
Extract only questions about applicable law that the court explicitly or implicitly resolved to reach its decision. Focus on what the court needed to determine, not what parties argued or preliminary questions considered but not decided. There may be one or more issues. If there is only one issue, then return only one question.
2.	Question Formulation: 
Frame each issue as a precise legal question using "Whether..." format. Examples: 
-	"Whether parties can validly choose the law of a country with no connection to their contract?"
-	"Whether implied choice of law can be inferred from forum selection clauses?"
-	"Whether the closest connection test applies when parties made no express choice of law?"
-	"Whether Indian courts should apply foreign law to determine contractual validity?"
3.	Scope Guidelines: 
-	Include: Questions about validity of express choices, methods for determining implied choices, default rules in absence of choice, scope of chosen law, renvoi issues
-	Include: Issues about connecting factors, party autonomy limitations, public policy exceptions
-	Exclude: Pure jurisdictional questions, procedural law issues, enforcement matters unrelated to choice of law
4.	Output Requirements: 
-	List each issue as a separate numbered question
-	Use precise, legally accurate terminology
-	Ensure each question reflects a choice of law determination actually made by the court
-	Order issues from primary to secondary based on their importance to the court's reasoning
5.	Quality Check: Each identified issue should be answerable by pointing to specific court reasoning in the choice of law analysis.
6.	OUTPUT FORMAT:
**LEGAL ISSUES:**
1. Whether [specific choice of law question court resolved]
2. Whether [additional issue if present]
7.   CONSTRAINT: Base issue identification solely on the court's actual analysis and resolution, drawing from both the full judgment text and extracted choice of law section.
\nThe issue in this case is related to this theme/these themes:\n{classification_definitions}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nThe issue is:\n
"""

# ===== COURT'S POSITION =====
COURTS_POSITION_PROMPT = """
TASK: Extract the binding legal principle(s) that the court established as essential to its choice of law decision.
INSTRUCTIONS:
1.	Ratio Identification Method: 
-	Identify each legal proposition the court stated regarding choice of law
-	Apply the inversion test mentally: Would reversing this proposition change the court's conclusion?
-	Include only propositions where the answer is "no" - these are ratio decidendi
2.	Content Requirements: 
-	Extract the court's binding legal rule(s), not factual findings or case-specific applications
-	State each principle as a clear, precedential rule applicable to future cases
-	Focus on private international law (PIL) methodology, not the specific contractual or factual outcome
-	Use the court's own formulation where possible, condensed into the form of a principle.
3.	Output Specifications: 
-	State each ratio as a complete legal principle in 1-2 sentences maximum
-	If multiple ratios exist on different choice of law points, number them separately
-	Ensure each principle directly addresses the legal issue(s) previously identified
-	Avoid factual details, policy reasoning, or persuasive commentary
4.	Quality Standards: 
-	Each ratio should be actionable as precedent in future PIL cases
-	Principles should be neither too narrow (case-specific) nor too broad (unhelpful generalization)
-	Focus on what the court held must be done, not what it suggested or considered
5.	OUTPUT FORMAT:
**COURT’S POSITION**
[Legal principle 1 - complete rule in 1-2 sentences]
[Legal principle 2 - if applicable]
6.	CONSTRAINT: Extract principles solely from the court's binding determinations in the provided judgment text, ensuring each principle was necessary for the court's choice of law conclusion.
\nYour output is a direct answer to the issue laid out here:\n{col_issue}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s):\n{classification}\n\nThe court's position is:\n
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
\nYour output is a direct answer to the issue laid out here:\n{col_issue}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s):\n{classification}\n\nThe obiter dicta is:\n
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
\nYour output is a direct answer to the issue laid out here:\n{col_issue}\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s):\n{classification}\n\nThe dissenting opinions are:\n
"""

# ===== ABSTRACT =====
ABSTRACT_PROMPT = """
Your task is to extract the abstract from a court decision. Your response only consists of the abstract, with no explanations or additional information. The official abstract in the case is right at the beginning, often referred to with a specific term such as “Headnote” or “Case Note”. At times it might just be printed in bold at the start of the judgment without any specific title.  If there is no dedicated abstract to be found, and only then, you must return a general description of the information in the file. It must be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less.\nCourt Decision Text:\n{text}\n\nThe abstract is:\n
"""