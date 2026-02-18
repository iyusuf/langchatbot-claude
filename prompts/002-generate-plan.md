# Generate Execution Plan from spec-001

Read `specs/spec-001.md` thoroughly. Read `.claude/CLAUDE.md` for project conventions.

Do NOT write any application code. Your only output is `plans/plan-001.md`.

## What to produce

Create `plans/plan-001.md` containing:

1. **Phase list** — Break spec-001 into sequential implementation phases. Each phase adds exactly one functional capability. Target 5-8 phases.

2. **Per phase, include**:
   - Phase number and title
   - Objective (one sentence)
   - Which spec requirements it satisfies (reference FR-N, NFR-N numbers)
   - Files to create or modify
   - Verification step (a concrete command or action to confirm it works)
   - Status: `[ ] Not started`

3. **Phase 1 must be minimal**: A working Streamlit app that sends one hardcoded message to OpenRouter via `llm_factory.py` and displays the response. No tools, no sessions, no file context. Just proof that the Streamlit ↔ LangChain ↔ OpenRouter pipeline works end to end.

4. **Dependencies between phases** — If Phase N depends on Phase M, state it explicitly.

## Constraints

- Do not create any directories or code files.
- Do not install any packages.
- Only output: `plans/plan-001.md`
- After writing the plan, summarize the phase titles so I can review before we proceed.