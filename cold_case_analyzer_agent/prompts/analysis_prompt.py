ANALYSIS_PROMPT = """
You are a jurist and a private international law expert. Analyze the following court decision.\nSummarize the key points in a concise paragraph, focusing on the Choice of Law section and the classified theme.\n\nCourt Decision Text:\n{text}\n\nExtracted Choice of Law Section:\n{col_section}\n\nClassified Theme(s): {classification}\n\nYour analysis:\n
"""