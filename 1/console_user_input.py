# console_user_input.py — Interactive console chat with LLM via LangChain

from langchain_core.prompts import ChatPromptTemplate
from llm_connect import get_llm

# 1. Get the model
llm = get_llm()

# 2. Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{user_input}")
])

# 3. LCEL chain
chain = prompt | llm

# 4. Chat loop — type "quit" or press Ctrl+C to exit
print('Chat started. Type "quit" to exit.\n')
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit"):
        print("Goodbye!")
        break
    if not user_input:
        continue

    response = chain.invoke({"user_input": user_input})
    print(f"\nAssistant: {response.content}\n")
