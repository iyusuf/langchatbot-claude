# LangChatbot-Claude — Session 00: Hello World

## What I Did Today

### 1. Verified environment setup
Created `debug_env.py` to confirm the `.env` file loads correctly and the `OPENROUTER_API_KEY` is accessible. Quick sanity check before touching any LangChain code.

### 2. Built a hello-world LangChain script
`hello_world_langchain.py` — a minimal script that sends a single hardcoded prompt ("What is LangChain?") to Claude via OpenRouter using LangChain's LCEL chain (`ChatPromptTemplate | ChatOpenAI`). Proved the full path works: `.env` key -> `ChatOpenAI` -> OpenRouter -> Claude -> printed response.

### 3. Extracted a reusable LLM connection module
`llm_connect.py` — pulled all OpenRouter/LLM wiring into a single `get_llm()` factory function. Any script can now get a ready-to-use LangChain chat model with one import. Accepts optional `model` and `temperature` overrides.

### 4. Moved the model name into config
`config.yaml` — created a YAML config file so the default model (`anthropic/claude-sonnet-4.6`) isn't hardcoded in Python. `llm_connect.py` reads from this file at import time. Changing models is now a one-line YAML edit.

### 5. Built an interactive console chatbot
`console_user_input.py` — a loop that reads user input from the terminal, sends it to the LLM, and prints the response. Started as a single-shot script, then upgraded to a `while True` loop so it keeps the conversation going until the user types "quit".

## File Map

```
hello_world_langchain.py   # One-shot LLM call (teaching example)
console_user_input.py      # Interactive console chat loop
llm_connect.py             # Reusable LLM factory (get_llm())
config.yaml                # Model configuration
debug_env.py               # Env var sanity check (temporary)
requirements.txt           # Python dependencies
.env                       # API key (not committed)
```

## What's Next

The natural progression from here, based on the pattern so far (get something working, then extract and generalize):

- **Conversation memory** — right now each prompt is independent. Add LangChain message history so the LLM remembers earlier turns in the same session.
- **System prompt from config** — move the "You are a helpful assistant." system message out of code and into `config.yaml` or a separate prompt file, the same way the model name was extracted.
- **Streamlit UI** — swap the console `input()` loop for a Streamlit chat interface (`st.chat_input` / `st.chat_message`), turning this into a real web app.
- **LangGraph agent** — replace the simple LCEL chain with a `StateGraph` to enable tool use, branching logic, and proper agent orchestration.
- **File context and tools** — give the agent the ability to read files from `FILES/` and invoke tools from `TOOLS/`, following the full spec in `specs/spec-001.md`.
