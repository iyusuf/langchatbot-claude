from langchain_core.prompts import (
    ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)

sys_msg = SystemMessagePromptTemplate.from_template("You screen resumes for {company}.")
human_msg = HumanMessagePromptTemplate.from_template("Evaluate:\n{resume}")

prompt = ChatPromptTemplate.from_messages([sys_msg, human_msg])


# Smoke Test
print(prompt.input_variables)  # should show ['company', 'resume']

result = prompt.invoke({"company": "AECOM", "resume": "10yr GIS developer, ESRI certified"})


for msg in result.messages:
    print(f"[{msg.type}]\n{msg.content}\n")
