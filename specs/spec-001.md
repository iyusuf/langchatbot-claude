# prompt_console_chatbot_spec_v2.md
# Status: Draft
# Date: 2026-02-16
# Purpose: Specification prompt for Claude Code to build a Streamlit-based LangChain/LangGraph chatbot
#          replicating the "Project" paradigm from Claude.ai/ChatGPT
# Changes from v1: Streamlit replaces console UI; OpenRouter integration confirmed with concrete
#          pattern; maturity level recalibrated to "learning project (Hello World +++)"

---

## Objective

Build a **Streamlit-based chatbot application** that replicates the Claude.ai/ChatGPT **Project** paradigm — project-scoped instructions, file-based knowledge context, invocable tools, and persistent session history — running locally. The application must be built on LangChain, LangGraph, and LangSmith, using OpenRouter as the unified LLM gateway.

**Primary purpose**: This is a **learning project** for understanding LangChain, LangGraph, and LangSmith through hands-on implementation. Maturity target is "Hello World +++" — functional, well-structured, clearly commented, but not production-hardened. Favor clarity and learnability over optimization.

**Phase 1 (this spec)**: Core chatbot with project structure, tool invocation, and session persistence.
**Phase 2 (future)**: RAG framework integration for scalable document retrieval over the FILES knowledge base.

---

## Context

This is a greenfield Python project. The chatbot operates through a Streamlit web interface served locally. It models the following concepts drawn from Claude.ai and ChatGPT "Projects":

| Concept | Local Equivalent | Description |
|---|---|---|
| Project Instruction | `project_instruction.md` | A markdown file injected as system-level context for every conversation turn. |
| Project Files (Knowledge) | `FILES/` directory | Local files ingested and provided as context to the LLM. Phase 1: full-text injection. Phase 2: RAG-based retrieval. |
| Project Tools | `TOOLS/` directory | Python modules exposing LangChain-compatible tools the LLM agent can invoke during conversation. |
| Session History | `SESSIONS/` directory | Each chat session serialized to disk for persistence, replay, and continuity across restarts. |

---

## Architecture Constraints

1. **Python 3.11+** — single language.
2. **LangChain** — for LLM abstraction, tool definitions, prompt templates, and chain composition.
3. **LangGraph** — for agent orchestration, state management, and control flow (tool-calling loops, conditional routing). Use `StateGraph`, not legacy `AgentExecutor`.
4. **LangSmith** — for tracing, debugging, and observability of all LLM calls and agent steps.
5. **OpenRouter** — sole LLM provider gateway (see Integration Pattern below).
6. **Streamlit** — sole UI framework. No console/terminal interface.
7. **Stateless services, explicit state passing** — no hidden global state. Session state managed through LangGraph's state graph + Streamlit's `st.session_state` for UI layer only.
8. **Learning-first structure** — every module should have a docstring explaining *what it does and why*. Inline comments on non-obvious LangChain/LangGraph patterns.

---

## OpenRouter + LangChain Integration Pattern

Confirmed from OpenRouter documentation. Two approaches are supported; **use `init_chat_model` as primary, `ChatOpenAI` direct as fallback**.

### Approach A — `init_chat_model` (preferred)
```python
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="openai/<model_name>",  # or "anthropic/<model_name>"
    model_provider="openai",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)
```

### Approach B — `ChatOpenAI` direct (fallback)
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="<model_name>",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>",   # optional, for OpenRouter rankings
        "X-Title": "<YOUR_APP_NAME>",         # optional
    },
)
```

### Key notes for the coding agent:
- OpenRouter uses the OpenAI-compatible API interface for all models, including Anthropic Claude.
- Model strings follow OpenRouter format: `anthropic/claude-sonnet-4-20250514`, `openai/gpt-4o`, etc.
- The `model_provider` in `init_chat_model` should always be `"openai"` since OpenRouter exposes an OpenAI-compatible endpoint, regardless of which underlying model is selected.
- Reference implementation: [github.com/alexanderatallah/openrouter-streamlit](https://github.com/alexanderatallah/openrouter-streamlit) — a Streamlit + OpenRouter + LangChain example app.

---

## Project Directory Structure

```
app_langchain_chatbot_v1/
├── app.py                        # Streamlit entry point
├── config.yaml                   # Default model, LangSmith project, token limits, tool flags
├── project_instruction.md        # System prompt injected into every turn
├── requirements.txt              # Pinned dependencies
├── .env.example                  # Template for OPENROUTER_API_KEY, LANGSMITH_API_KEY
├── FILES/
│   └── (user-provided knowledge files)
├── TOOLS/
│   ├── __init__.py
│   ├── read_file.py              # Read a file and return contents
│   ├── list_files.py             # List files in FILES/ directory
│   └── run_python.py             # Execute Python snippet in subprocess
├── SESSIONS/
│   └── session_<id>.jsonl
├── src/
│   ├── __init__.py
│   ├── llm_factory.py            # OpenRouter LLM instantiation (abstraction point)
│   ├── agent_graph.py            # LangGraph StateGraph definition
│   ├── tool_registry.py          # Auto-discover and register tools from TOOLS/
│   ├── file_context.py           # Read FILES/ and build context (SWAP POINT for Phase 2 RAG)
│   ├── session_manager.py        # Session save/load/list operations
│   └── config_loader.py          # Load config.yaml + env vars
└── tests/
    ├── test_tool_registry.py
    ├── test_session_manager.py
    └── test_file_context.py
```

---

## Functional Requirements

### FR-1: Streamlit Chat Interface
- Standard Streamlit chat UI using `st.chat_message` and `st.chat_input`.
- **Sidebar** contains:
  - Model selector dropdown (populated from config, e.g., `anthropic/claude-sonnet-4-20250514`, `openai/gpt-4o`).
  - Session management: "New Session" button, dropdown to resume prior sessions.
  - Expandable section showing: registered tools, ingested files with token counts.
- Streamed LLM responses via Streamlit's `st.write_stream` or equivalent.

### FR-2: Project Instruction Injection
- `project_instruction.md` read at session start, injected as the system message.
- Changes to the file picked up on next user turn (hot-reload).

### FR-3: File Context Ingestion (Phase 1 — Full-Text)
- All files in `FILES/` parsed and concatenated into a context block injected alongside the system message.
- Supported formats (Phase 1): `.md`, `.txt`, `.csv`, `.py`, `.json`, `.yaml`.
- Token budget awareness: if total context exceeds configurable threshold, warn in sidebar and truncate with indicator.
- **CRITICAL**: This layer must sit behind an abstraction (`file_context.py`) so Phase 2 can swap in RAG retrieval without touching agent logic.

### FR-4: Tool Registration and Invocation
- Each Python file in `TOOLS/` exposes LangChain-compatible tools via `@tool` decorator or `StructuredTool`.
- Auto-discovered and registered at app start.
- LangGraph agent decides when to invoke tools.
- Tool invocations and results displayed in the Streamlit UI (expandable sections or status indicators).
- **Starter tools to implement**: `read_file`, `list_files`, `run_python` (sandboxed subprocess).

### FR-5: Session Persistence
- Each session: unique ID (`session_<ISO-timestamp>`).
- Every exchange (user input, assistant response, tool calls, tool results) appended to `SESSIONS/session_<id>.jsonl`.
- Session resume replays history into LangGraph state + Streamlit chat display.
- Stored in `st.session_state` during active session; serialized to disk on each turn.

### FR-6: Model Switching
- Sidebar dropdown allows switching model mid-session.
- Model change takes effect on next user message.
- Current model displayed in sidebar.

### FR-7: LangSmith Observability
- All LLM calls, tool invocations, and agent state transitions traced to LangSmith.
- Project name and run metadata (session ID, model, project root) attached to every trace.
- LangSmith can be disabled via config for offline use.

---

## Non-Functional Requirements

- **NFR-1**: Graceful error handling — API failures, malformed tools, missing files — shown as Streamlit error/warning banners, never raw stack traces.
- **NFR-2**: All secrets via environment variables (`.env`), never in config files.
- **NFR-3**: Type hints throughout. No `Any` types in public interfaces.
- **NFR-4**: Every module has a docstring. Non-obvious LangChain/LangGraph patterns get inline comments explaining the *why*.

---

## Phase 2 Preview (Not in Scope — Architectural Constraint Only)

Phase 2 replaces full-text file injection with a RAG pipeline:

- Local vector store (FAISS or ChromaDB) for document embeddings.
- Chunking strategy for `FILES/` (including PDF, DOCX support added here).
- Retrieval chain integrated into LangGraph agent.
- Hybrid retrieval: keyword + semantic. Re-ranking before injection.

**Phase 1 hard constraint**: `file_context.py` must expose a clean interface (e.g., `get_context(query: str | None) -> str`) that Phase 2 replaces with retrieval logic. Agent graph must not directly access file system.

---

## Success Criteria

1. User can launch `streamlit run app.py`, see a chat interface, and converse with an LLM via OpenRouter that has awareness of project instructions and files.
2. LLM can autonomously invoke tools from `TOOLS/` and incorporate results into responses.
3. Sessions persist across browser refreshes and app restarts, and can be resumed.
4. Model switching between Claude and GPT models works mid-session via sidebar.
5. All interactions traced and visible in LangSmith (when enabled).
6. File ingestion is behind `file_context.py` abstraction that Phase 2 can replace without touching `agent_graph.py`.
7. A developer learning LangChain can read the code and understand the patterns through docstrings and comments.

---

## Deliverables

1. **Working Streamlit application** — `streamlit run app.py` from project root.
2. **README.md** — setup instructions (env vars, config, dependencies), architecture overview, usage walkthrough.
3. **Example project** — sample `project_instruction.md`, sample files in `FILES/`, starter tools in `TOOLS/`.
4. **Tests** — unit tests for tool registration, session serialization, file context ingestion.
5. **`.env.example`** — template for required environment variables.

---

## Reference Resources

- OpenRouter + LangChain docs: https://openrouter.ai/docs/guides/community/langchain
- OpenRouter + Streamlit reference app: https://github.com/alexanderatallah/openrouter-streamlit
- LangGraph StateGraph docs: https://langchain-ai.github.io/langgraph/
- LangSmith docs: https://docs.smith.langchain.com/

---

## Notes for Coding Agent (Claude Code)

- Use `langchain-openai` with OpenRouter base URL override for LLM instantiation. Wrap in `llm_factory.py` so model/provider details are in one place.
- Use `langgraph` `StateGraph` for the agent loop, **not** legacy `AgentExecutor`.
- Prefer `langgraph`'s built-in `ToolNode` for tool execution.
- Session serialization: evaluate LangGraph checkpointer vs custom JSONL writer — comment the decision in code.
- Streamlit state management: use `st.session_state` only for UI state (messages display, current model). Agent state lives in LangGraph.
- For streaming: LangGraph supports `.astream_events()` — use this to feed tokens to Streamlit's streaming display.
- This is a learning project. When choosing between "clever" and "readable", always choose readable. Comment the LangChain/LangGraph patterns for someone who hasn't used them before.