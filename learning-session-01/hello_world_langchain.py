# hello_world_langchain.py — Teaching Example

from langchain_core.prompts import ChatPromptTemplate
from llm_connect import get_llm

# 1. Get the model — connection details live in llm_connect.py
llm = get_llm()

# 2. Prompt template — unchanged, this layer doesn't care about infrastructure
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{user_input}")
])

# 3. LCEL chain — same pipe composition
chain = prompt | llm

# 4. Invoke
response = chain.invoke({"user_input": "What is LangChain?"})
print(response.content)
