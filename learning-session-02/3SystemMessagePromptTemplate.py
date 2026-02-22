from langchain_core.prompts import (SystemMessagePromptTemplate)

sys_template = SystemMessagePromptTemplate.from_template("You are resume screener for {company}. Role: {role}")
                                                         
# Smoke Test
print(sys_template.input_variables)  # should show ['company', 'role']''



