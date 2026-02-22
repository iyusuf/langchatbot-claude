from langchain_core.prompts import (HumanMessagePromptTemplate)

template = """
Candidate: {candidate_name}
Resume Text:
{resume}

Score against JD criteria. Return JSON.
"""

human_message_prompt = HumanMessagePromptTemplate.from_template(template)