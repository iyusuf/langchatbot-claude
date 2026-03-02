from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

system_message = Path("system_message.txt").read_text()
seed_message = Path("seed_message.txt").read_text()


prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", seed_message)
])

# Smoke Test
print(prompt.messages)
print(prompt.input_variables)
    