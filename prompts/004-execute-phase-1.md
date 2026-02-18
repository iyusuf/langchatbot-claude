# Execute Phase 1: Minimal Streamlit-to-OpenRouter Pipeline

Read `plans/plan-001.md` Phase 1. Read `.claude/CLAUDE.md` for project conventions.

## What to build

Create the minimal pipeline proving Streamlit → LangChain → OpenRouter works:

1. `src/__init__.py` — package marker
2. `src/config_loader.py` — load `config.yaml` and `.env` environment variables
3. `src/llm_factory.py` — single function that returns a `ChatOpenAI` instance configured for OpenRouter. This is the ONLY place LLM instantiation happens in the entire project.
4. `src/app.py` — Streamlit app with `st.chat_input` and `st.chat_message`. User types a message, it goes to OpenRouter via `llm_factory`, response displays on screen. Include basic message history in `st.session_state` so the chat UI shows prior messages within the same browser session.
5. `config.yaml` — default model (`anthropic/claude-sonnet-4-20250514`), list of available models, any other settings `config_loader` needs
6. `.env.example` — template with `OPENROUTER_API_KEY=`
7. `requirements.txt` — pinned dependencies: streamlit, langchain, langchain-openai, python-dotenv, pyyaml

## Constraints

- No LangGraph yet. Direct `llm.invoke()` is correct for this phase.
- No tools, no file context, no sessions, no streaming.
- No sidebar beyond a simple title/header.
- Keep it minimal. This phase proves the pipeline, nothing more.

## Verification

After building, run `streamlit run src/app.py` and confirm:
1. The app launches without errors
2. You can type a message and receive a response from OpenRouter
3. The chat shows message history within the session

## After verification

Update `plans/plan-001.md` Phase 1 status from `[ ] Not started` to `[x] Complete` with today's date.