from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


system_message_text_file = Path("system_message.txt").read_text()
system_message_prompt_template = SystemMessagePromptTemplate.from_template(system_message_text_file)

human_template_text_file = Path("human_template.txt").read_text()
human_message_prompt_template = HumanMessagePromptTemplate.from_template(human_template_text_file)


prompt = ChatPromptTemplate.from_messages([
   system_message_prompt_template,
   human_message_prompt_template
])

llm_model = ChatAnthropic(
    model="claude-sonnet-4-6", 
    temperature=0.0, 
    max_tokens=1024
)

chain = prompt | llm_model | StrOutputParser()

# Smoke Test
print(prompt.messages)
print(prompt.input_variables)
response = chain.invoke({
    "candidate_name1": "John Doe",
    "resume": "John has 5 years of experience in software development, specializing in Python and JavaScript. He has worked on various projects, including web applications and data analysis tools."
})
print(response)

