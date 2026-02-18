# LangChatbot — Streamlit + LangChain/LangGraph + OpenRouter

## Project Overview

Learning project ("Hello World +++") building a Streamlit chatbot that replicates the Claude.ai/ChatGPT "Project" paradigm — project instructions, file context, tool invocation, session persistence — using LangChain, LangGraph, LangSmith, and OpenRouter.

Full specification: `specs/spec-001.md` — read this before writing any code.

## Workflow

1. Read `specs/spec-001.md` thoroughly before implementation.
2. Create `plans/plan-001.md` breaking the spec into testable phases. Phase 1 = minimal Streamlit app that sends one message to OpenRouter and displays the response. Each subsequent phase adds one functional requirement.
3. Execute one phase at a time. After each phase, verify with `streamlit run src/app.py`, then update `plans/plan-001.md` to mark the phase complete before proceeding.
4. Do NOT build everything at once.

## Architecture Rules

- **LangGraph `StateGraph`** for agent orchestration. Never use legacy `AgentExecutor`.
- **`ToolNode`** from LangGraph for tool execution.
- **`st.session_state`** for UI state only. Agent state lives in LangGraph.
- **`src/file_context.py`** must be a clean abstraction layer. Agent graph must never directly access the file system. Phase 2 will swap this for RAG — design for that now.
- **`src/llm_factory.py`** is the single place for OpenRouter/LLM instantiation. No LLM construction anywhere else.

## OpenRouter Integration

Use `ChatOpenAI` from `langchain-openai` with OpenRouter base URL:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="<model_name>",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=OPENROUTER_API_KEY,
)
```
`model_provider` is always `"openai"` regardless of underlying model (Claude, GPT, etc.).

## Project Structure

All application code goes in `src/`. Specs live in `specs/`. Prompts in `prompts/`.
```
langchatbot-claude/
├── .claude/CLAUDE.md
├── specs/                   # What to build (specifications)
│   └── spec-001.md
├── plans/                   # Generated execution plans (one per spec)
│   └── plan-001.md
├── prompts/                 # Sequential prompts for Claude Code
│   └── 001_generate_plan.md
├── src/
│   ├── app.py              # Streamlit entry point
│   ├── llm_factory.py
│   ├── agent_graph.py
│   ├── tool_registry.py
│   ├── file_context.py
│   ├── session_manager.py
│   └── config_loader.py
├── TOOLS/                   # LangChain @tool modules (auto-discovered)
├── FILES/                   # Knowledge files (ingested as context)
├── SESSIONS/                # Persisted chat sessions
├── tests/
├── config.yaml
├── .env.example
├── requirements.txt
└── README.md
```

## Naming Convention

specs/spec-NNN.md → plans/plan-NNN.md → prompts/NNN-*.md

One spec produces one plan. One plan is executed by many prompts.
Plan numbers match their source spec number.

## Commands

- `streamlit run src/app.py` — launch the app
- `pytest tests/` — run tests
- `pip install -r requirements.txt` — install dependencies

## Code Standards

- Python 3.11+
- Type hints on all public interfaces. No `Any` types.
- Docstring on every module and class explaining what it does and why.
- Inline comments on non-obvious LangChain/LangGraph patterns — this is a learning project.
- When choosing between clever and readable, choose readable.
- Secrets via `.env` only, never in config files.
- Errors shown as Streamlit warning/error banners, never raw stack traces to the user.

## What NOT to Do

- Do not skip phases or implement features out of order.
- Do not hardcode model names — they come from `config.yaml`.
- Do not put LLM instantiation logic outside `llm_factory.py`.
- Do not access `FILES/` directory directly from `agent_graph.py` — always go through `file_context.py`.
- Do not use `AgentExecutor`. Use `StateGraph`.