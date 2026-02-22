from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a resume screening expert for AEC firms."),
    ("human", "Match this resume to the job description.\n\nJD:\n{jd}\n\nResume:\n{resume}")
])


# Smoke Test

print(prompt.messages)
print(prompt.input_variables)