# Execution Plan for spec-001

**Spec**: `specs/spec-001.md` — Streamlit + LangChain/LangGraph + OpenRouter Chatbot
**Date created**: 2026-02-16

---

## Phase 1: Minimal Streamlit-to-OpenRouter Pipeline

**Objective**: Prove the Streamlit → LangChain → OpenRouter pipeline works end-to-end with one hardcoded message.

**Requirements satisfied**: FR-1 (minimal), NFR-2 (secrets via .env)

**Files to create**:
- `src/__init__.py` — package marker
- `src/config_loader.py` — load `config.yaml` + environment variables
- `src/llm_factory.py` — single LLM instantiation point using OpenRouter
- `src/app.py` — Streamlit entry point; single text input, sends to LLM, displays response
- `config.yaml` — default model name, model list, basic settings
- `.env.example` — template with `OPENROUTER_API_KEY`
- `requirements.txt` — pinned dependencies (streamlit, langchain, langchain-openai, python-dotenv, pyyaml)

**Verification**: Run `streamlit run src/app.py`, type a message, confirm a response from OpenRouter appears on screen.

**Dependencies**: None (first phase).

**Status**: `[ ] Not started`

---

## Phase 2: Conversational Chat UI with Streaming and Model Switching

**Objective**: Build a full chat interface with message history, streamed responses, and a sidebar model selector.

**Requirements satisfied**: FR-1 (full chat UI, sidebar, streaming), FR-6 (model switching)

**Files to modify**:
- `src/app.py` — replace single-shot UI with `st.chat_message` / `st.chat_input` loop; add sidebar with model dropdown; implement streaming via `st.write_stream`

**Files to modify (if needed)**:
- `src/llm_factory.py` — ensure model parameter is dynamic (accept model name from sidebar)
- `src/config_loader.py` — expose model list for sidebar dropdown

**Verification**: Run `streamlit run src/app.py`. Have a multi-turn conversation. Switch model mid-conversation via sidebar. Confirm streamed token-by-token output appears correctly.

**Dependencies**: Phase 1 (pipeline must work).

**Status**: `[ ] Not started`

---

## Phase 3: LangGraph Agent Orchestration

**Objective**: Replace the direct LLM call with a LangGraph `StateGraph` so all conversation flows through the agent graph, separating agent state from UI state.

**Requirements satisfied**: Architecture Constraint 3 (StateGraph, not AgentExecutor), Architecture Constraint 7 (explicit state passing)

**Files to create**:
- `src/agent_graph.py` — define `StateGraph` with a chat node that invokes the LLM; compile the graph; expose a function to run a user message through the graph and return the response

**Files to modify**:
- `src/app.py` — replace direct `llm.invoke()` calls with graph invocation; keep `st.session_state` for UI display only, agent state lives in the graph
- `requirements.txt` — add `langgraph` if not already present

**Verification**: Run `streamlit run src/app.py`. Multi-turn conversation should behave identically to Phase 2, but now routed through the LangGraph agent. Log every graph node transition to the terminal. The log must show: START → chat_node → END for every message. This log proves the graph is running and provides the foundation for verifying tool routing in Phase 5 (where it becomes START → chat_node → tool_node → chat_node → END).

**Dependencies**: Phase 2 (conversational UI must work).

**Status**: `[ ] Not started`

---

## Phase 4: Project Instruction and File Context Injection

**Objective**: Inject `project_instruction.md` as a system message and all `FILES/` contents as context, behind a clean abstraction layer.

**Requirements satisfied**: FR-2 (project instruction injection, hot-reload), FR-3 (file context ingestion, token budget, abstraction)

**Files to create**:
- `src/file_context.py` — abstraction layer exposing `get_context(query: str | None) -> str`; reads all supported files from `FILES/`, concatenates them; respects configurable token budget; warns on truncation
- `project_instruction.md` — sample project instruction for testing
- `FILES/` — add 1-2 sample files (e.g., a `.md` and a `.txt`) for testing

**Files to modify**:
- `src/agent_graph.py` — prepend system message (project instruction + file context) to the message list on each turn; re-read `project_instruction.md` on each turn for hot-reload
- `src/app.py` — show ingested files with token counts in sidebar expandable section; show truncation warning if token budget exceeded
- `config.yaml` — add `token_budget` setting

**Verification**: Run `streamlit run src/app.py`. Ask the LLM a question about the content in `FILES/`. Confirm it answers using that context. Edit `project_instruction.md` mid-session and confirm the change is reflected on the next turn. Check sidebar shows file list and token counts.

**Dependencies**: Phase 3 (agent graph must be in place so context is injected into graph state, not ad-hoc).

**Status**: `[ ] Not started`

---

## Phase 5: Tool Registration and Invocation

**Objective**: Auto-discover tools from `TOOLS/`, register them with the LangGraph agent, and allow the LLM to invoke them during conversation.

**Requirements satisfied**: FR-4 (tool registration, auto-discovery, invocation, UI display)

**Files to create**:
- `src/tool_registry.py` — scan `TOOLS/` directory, import modules, collect `@tool`-decorated functions, return list of tools
- `TOOLS/__init__.py` — package marker
- `TOOLS/read_file.py` — read a file from `FILES/` and return contents
- `TOOLS/list_files.py` — list files in `FILES/` directory
- `TOOLS/run_python.py` — execute a Python snippet in a sandboxed subprocess and return output

**Files to modify**:
- `src/agent_graph.py` — add `ToolNode` to the graph; add conditional edge: if LLM response contains tool calls, route to `ToolNode`, then back to LLM; bind tools to the LLM via `.bind_tools()`
- `src/app.py` — display tool invocations and results in expandable sections in the chat; show registered tools in sidebar

**Verification**: Run `streamlit run src/app.py`. Ask the LLM to list files in the project. Confirm it invokes the `list_files` tool and incorporates the result. Ask it to run a simple Python calculation. Confirm `run_python` executes and returns the result. Check sidebar shows all registered tools.

**Dependencies**: Phase 3 (StateGraph must exist to add ToolNode). Phase 4 (helpful but not strictly required; tools like `read_file` read from `FILES/` which should exist).

**Status**: `[ ] Not started`

---

## Phase 6: Session Persistence

**Objective**: Persist every chat session to disk as JSONL and allow resuming prior sessions from the sidebar.

**Requirements satisfied**: FR-5 (session ID, JSONL persistence, resume, sidebar management)

**Files to create**:
- `src/session_manager.py` — generate session IDs (`session_<ISO-timestamp>`), append exchanges to `SESSIONS/session_<id>.jsonl`, list available sessions, load a session's history
- `SESSIONS/` — directory for session files (created at runtime if missing)

**Files to modify**:
- `src/app.py` — add "New Session" button and session resume dropdown in sidebar; on each turn, call `session_manager` to persist the exchange; on resume, replay history into both LangGraph state and Streamlit chat display
- `src/agent_graph.py` — support initializing graph state from a loaded session history (for resume)

**Verification**: Run `streamlit run src/app.py`. Have a conversation. Close the browser tab. Reopen `streamlit run src/app.py`. Select the prior session from the sidebar dropdown. Confirm full chat history is restored and the conversation can continue. Check that `SESSIONS/` contains a `.jsonl` file with all exchanges.

**Dependencies**: Phase 3 (agent graph state must be separate from UI state for clean serialization). Phase 2 (sidebar UI must exist).

**Status**: `[ ] Not started`

---

## Phase 7: LangSmith Observability and Final Polish

**Objective**: Integrate LangSmith tracing for all LLM calls, tool invocations, and agent transitions; apply final error-handling and code-quality polish.

**Requirements satisfied**: FR-7 (LangSmith tracing, project name, run metadata, disable via config), NFR-1 (graceful error handling), NFR-3 (type hints), NFR-4 (docstrings and comments)

**Files to modify**:
- `src/config_loader.py` — load LangSmith settings (API key, project name, enabled flag) from `.env` and `config.yaml`
- `src/agent_graph.py` — attach LangSmith tracing callbacks; include metadata (session ID, model, project root) in each trace
- `src/app.py` — wrap all LLM/agent calls in try/except; display errors as `st.error()` / `st.warning()` banners; never show raw stack traces
- `.env.example` — add `LANGSMITH_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT`
- `config.yaml` — add `langsmith.enabled` flag

**Files to create**:
- `tests/test_tool_registry.py` — unit tests for tool auto-discovery
- `tests/test_session_manager.py` — unit tests for session save/load/list
- `tests/test_file_context.py` — unit tests for file context ingestion and token budget

**Verification**: Run `streamlit run src/app.py` with LangSmith enabled. Have a conversation that includes tool calls. Open the LangSmith dashboard and confirm traces appear with correct metadata. Set `langsmith.enabled: false` in config, restart, confirm no traces are sent. Run `pytest tests/` and confirm all tests pass. Intentionally trigger errors (e.g., invalid API key, malformed tool) and confirm friendly error banners appear.

**Dependencies**: All prior phases (this is the integration and polish pass).

**Status**: `[ ] Not started`

---

## Dependency Summary

```
Phase 1  (Pipeline)
  └─► Phase 2  (Chat UI + Streaming + Model Switching)
        └─► Phase 3  (LangGraph Agent)
              ├─► Phase 4  (Project Instruction + File Context)
              ├─► Phase 5  (Tool Registration + Invocation)
              └─► Phase 6  (Session Persistence)
                    └─► Phase 7  (LangSmith + Tests + Polish)
```

Phases 4, 5, and 6 can be developed in any order after Phase 3, but the plan sequences them as listed because:
- Phase 4 (file context) creates the `FILES/` directory and content that Phase 5's tools operate on.
- Phase 6 (sessions) benefits from a more complete agent (with tools and context) for meaningful session replay.
- Phase 7 is always last as the integration/polish pass.
