# Update CLAUDE.md — Plans Directory Structure

Read `.claude/CLAUDE.md`. Make the following changes:

## Change 1: Workflow section
Replace all references to `PLAN.md` in the Workflow section with `plans/plan-001.md`. Update the workflow to read:

1. Read `specs/spec-001.md` thoroughly before implementation.
2. Create `plans/plan-001.md` breaking the spec into testable phases. Phase 1 = minimal Streamlit app that sends one message to OpenRouter and displays the response. Each subsequent phase adds one functional requirement.
3. Execute one phase at a time. After each phase, verify with `streamlit run src/app.py`, then update `plans/plan-001.md` to mark the phase complete before proceeding.
4. Do NOT build everything at once.

## Change 2: Project Structure section
Replace the `PLAN.md` line with a `plans/` directory. The updated structure should show:

```
langchatbot-claude/
├── .claude/CLAUDE.md
├── specs/                   # What to build (specifications)
│   └── spec-001.md
├── plans/                   # Generated execution plans (one per spec)
│   └── plan-001.md
├── prompts/                 # Sequential prompts for Claude Code
│   └── 001-generate-plan.md
├── src/
│   ├── app.py
│   ├── llm_factory.py
│   ├── agent_graph.py
│   ├── tool_registry.py
│   ├── file_context.py
│   ├── session_manager.py
│   └── config_loader.py
├── TOOLS/
├── FILES/
├── SESSIONS/
├── tests/
├── config.yaml
├── .env.example
├── requirements.txt
└── README.md
```

## Change 3: Add naming convention note
After the Project Structure section, add:

```
## Naming Convention

specs/spec-NNN.md → plans/plan-NNN.md → prompts/NNN-*.md

One spec produces one plan. One plan is executed by many prompts.
Plan numbers match their source spec number.
```

## Constraints
- Do not change any other sections of CLAUDE.md.
- Do not create any new files beyond updating `.claude/CLAUDE.md`.
- Show me the diff when done.