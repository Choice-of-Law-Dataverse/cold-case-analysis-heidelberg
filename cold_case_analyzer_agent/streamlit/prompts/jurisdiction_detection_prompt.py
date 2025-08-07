JURISDICTION_DETECTION_PROMPT = """
You are a legal expert. Your task is to classify the following text as coming from a "Civil-law jurisdiction", a "Common-law jurisdiction", or as "No court decision".

- If the text is a court decision from a civil law country (e.g., Germany, France, Italy, Spain, Switzerland, Austria, etc.), respond with exactly: Civil-law jurisdiction
- If the text is a court decision from a common law country (e.g., United States, England, Australia, Canada, etc.), respond with exactly: Common-law jurisdiction
- If the text is not a court decision, or you cannot tell, respond with exactly: No court decision

Return only one of these three options, and nothing else.

Text:
{text}
"""
