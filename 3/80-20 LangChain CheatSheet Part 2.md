# LangChain Core Artifacts — Expansion Sections 16–22
**Author**: Iqbal Yusuf | **Date**: February 2026 | **Status**: Draft | **Version**: v1
**Purpose**: Extend the 80-20 cheatsheet to cover manual-workflow-to-LangChain transfer — prompt persistence, session journaling, /compact automation, report generation, batch execution, deterministic pipeline steps, and cost tracking.

**Placement**: Insert after Section 15 (FewShotPromptTemplate), before Quick Composition Reference.

---

## 16. RunnableLambda / RunnablePassthrough

**Description**: `RunnableLambda` wraps any Python function as a chain-compatible step — it receives the previous step's output and returns input for the next step. `RunnablePassthrough` forwards its input unchanged, optionally running side-effects or parallel branches via `.assign()`. Together, these are how you insert deterministic logic (regex extraction, SQL queries, file I/O, validation) between LLM calls without breaking the LCEL pipe.

**Use Case**: Your deterministic-first principle requires that Ingest, Structure, and Deliver stages often use zero LLM calls. `RunnableLambda` makes a regex parser or a CSV writer a first-class chain step, composable with `|` just like a prompt or model. `RunnablePassthrough.assign()` lets you enrich a dict with computed fields mid-chain without losing existing keys.

**Example Code 1** — Deterministic extraction step:
```python
from langchain_core.runnables import RunnableLambda
import re

def extract_email(text: str) -> dict:
    """Deterministic step: no LLM, just regex."""
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
    return {"email": match.group(0) if match else "NOT_FOUND", "raw_text": text}

extract_step = RunnableLambda(extract_email)
chain = ingest_chain | extract_step | evaluate_chain
```

**Example Code 2** — Passthrough with field enrichment:
```python
from langchain_core.runnables import RunnablePassthrough

# Adds "token_count" to the dict without losing "jd" and "resume"
chain = RunnablePassthrough.assign(
    token_count=lambda x: len(x["resume"].split())
) | prompt | llm | StrOutputParser()

result = chain.invoke({"jd": jd_text, "resume": resume_text})
# prompt template can now reference {token_count} alongside {jd} and {resume}
```

---

## 17. chain.batch() / Parallel Execution

**Description**: Every LCEL chain exposes `.batch(inputs)` which runs the chain against a list of inputs. Processes multiple documents through the same pipeline in a single call. Supports `max_concurrency` to control parallelism and API rate limits. Returns a list of outputs in input order.

**Use Case**: Processing 10+ resumes, N RFX documents, or any batch where the same prompt runs against multiple inputs. Replaces manual for-loops with a built-in mechanism that handles concurrency and error collection. Essential for producing `baseline_scores.csv` across all resumes in one shot.

**Example Code 1** — Batch resume evaluation:
```python
chain = prompt | llm | PydanticOutputParser(pydantic_object=ResumeMatch)

inputs = [
    {"jd": jd_text, "resume": resume_texts[i]}
    for i in range(len(resume_texts))
]

results = chain.batch(inputs, config={"max_concurrency": 3})
# results: list[ResumeMatch], one per resume, preserves input order
```

**Example Code 2** — Batch with error handling:
```python
from langchain_core.runnables import RunnableConfig

results = chain.batch(
    inputs,
    config=RunnableConfig(max_concurrency=2),
    return_exceptions=True  # failed items return Exception instead of crashing
)

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Resume {i} failed: {result}")
    else:
        print(f"Resume {i}: score={result.overall_score}")
```

---

## 18. Prompt Persistence & File-Based Registry

**Description**: LangChain supports serializing prompt templates to YAML/JSON via `prompt.save()` and `load_prompt()`. Combined with your existing `<type>_<purpose>_v<N>.<ext>` naming convention and `Path`-based file loading, this creates a file-based prompt registry — versioned, diffable, and decoupled from code. System prompts and human templates live as separate files, loaded at chain construction time.

**Use Case**: Transferring your manual prompt-saving workflow into a structured registry. Every prompt you currently copy-paste into Claude.ai becomes a versioned file that a chain loads at runtime. Prompt changes are git-diffable. Rolling back to a previous version means changing a file path, not editing code.

**Example Code 1** — Save and load a ChatPromptTemplate:
```python
from langchain_core.prompts import ChatPromptTemplate, load_prompt

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a resume screening expert for AEC firms."),
    ("human", "Match this resume to the JD.\n\nJD:\n{jd}\n\nResume:\n{resume}")
])

# Save to YAML (git-trackable, diffable)
prompt.save("prompts/prompt_resume_match_v1.yaml")

# Load in another script or chain version
loaded_prompt = load_prompt("prompts/prompt_resume_match_v1.yaml")
chain = loaded_prompt | llm | StrOutputParser()
```

**Example Code 2** — File-based registry with your naming convention:
```python
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

PROMPT_DIR = Path("prompts/")

def load_prompt_pair(purpose: str, version: int) -> ChatPromptTemplate:
    """Load system + human prompt files following artifact naming convention."""
    sys_file = PROMPT_DIR / f"system_{purpose}_v{version}.md"
    human_file = PROMPT_DIR / f"human_{purpose}_v{version}.md"
    return ChatPromptTemplate.from_messages([
        ("system", sys_file.read_text()),
        ("human", human_file.read_text())
    ])

# Usage: swap versions by changing the integer, not the code
chain_v1 = load_prompt_pair("resume_match", 1) | llm | StrOutputParser()
chain_v2 = load_prompt_pair("resume_match", 2) | llm | StrOutputParser()
```

---

## 19. Callbacks & Session Logging

**Description**: LangChain's callback system fires events at every stage of chain execution — on chain start/end, LLM start/end, tool start/end, errors. `FileCallbackHandler` writes events to a log file. Custom callbacks (subclass `BaseCallbackHandler`) let you capture exactly the fields you need: timestamps, token counts, inputs/outputs, latencies. This is your automated work journal.

**Use Case**: Replacing manual session journaling. Every chain invocation writes a structured log entry: what prompt was used, what input was sent, what output was returned, how many tokens were consumed, how long it took. Reviewable after the fact. Audit-safe.

**Example Code 1** — FileCallbackHandler (quick setup):
```python
from langchain_community.callbacks import FileCallbackHandler

handler = FileCallbackHandler("logs/session_2026-02-22.log")
chain = prompt | llm | StrOutputParser()

result = chain.invoke(
    {"jd": jd_text, "resume": resume_text},
    config={"callbacks": [handler]}
)
# logs/session_2026-02-22.log now contains full chain execution trace
```

**Example Code 2** — Custom callback for structured journaling:
```python
from langchain_core.callbacks import BaseCallbackHandler
from datetime import datetime
import json

class SessionJournal(BaseCallbackHandler):
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.entries = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.entries.append({
            "event": "llm_start",
            "timestamp": datetime.now().isoformat(),
            "model": serialized.get("kwargs", {}).get("model", "unknown"),
            "prompt_preview": prompts[0][:200] if prompts else ""
        })

    def on_llm_end(self, response, **kwargs):
        gen = response.generations[0][0]
        self.entries.append({
            "event": "llm_end",
            "timestamp": datetime.now().isoformat(),
            "output_preview": gen.text[:200],
            "token_usage": response.llm_output.get("usage", {}) if response.llm_output else {}
        })

    def flush(self):
        with open(self.log_path, "w") as f:
            json.dump(self.entries, f, indent=2)

journal = SessionJournal("logs/journal_2026-02-22.json")
result = chain.invoke({"jd": jd_text, "resume": resume_text}, config={"callbacks": [journal]})
journal.flush()
```

---

## 20. On-Demand /compact Chain (Pattern)

**Description**: Not a LangChain artifact — a composable pattern. A dedicated summarization chain that takes a conversation transcript or accumulated outputs and produces a carry-forward context block in your format. Unlike `ConversationSummaryMemory` (which summarizes automatically and opaquely after every turn), this chain runs only when you invoke it deliberately. You control what goes in, what gets preserved, and what gets discarded.

**Use Case**: Transferring your manual `/compact` command into an invocable chain. After processing N resumes or completing a work session, you run the compact chain to extract high-signal tokens — candidate scores, key differentiators, unresolved questions — into a structured block that seeds the next session. The output format matches your carry-forward context block conventions.

**Example Code 1** — Basic /compact chain:
```python
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

compact_system = """You are a context compression specialist. 
Given a transcript of AI-assisted work, extract ONLY:
1. Decisions made (with rationale)
2. Scores and rankings (with evidence references)
3. Open questions or unresolved items
4. Artifacts produced (name, version, status)

Discard: full reasoning for obvious conclusions, repeated context, 
formatting boilerplate, greetings, meta-discussion.

Output as a structured carry-forward block."""

compact_prompt = ChatPromptTemplate.from_messages([
    ("system", compact_system),
    ("human", "Transcript to compact:\n\n{transcript}")
])

compact_chain = compact_prompt | llm | StrOutputParser()

# After a batch run, compact the accumulated outputs
transcript = "\n---\n".join(all_assessment_outputs)
carry_forward = compact_chain.invoke({"transcript": transcript})
Path("context/carry_forward_2026-02-22.md").write_text(carry_forward)
```

**Example Code 2** — Domain-aware /compact with preservation rules:
```python
compact_prompt = ChatPromptTemplate.from_messages([
    ("system", Path("prompts/system_compact_v1.md").read_text()),
    ("human", """Session context:
- Domain: {domain}
- Task: {task}
- Artifacts produced this session: {artifacts}

Transcript:
{transcript}

Preservation rules:
- ALWAYS preserve: {preserve_rules}
- ALWAYS discard: {discard_rules}

Generate carry-forward context block.""")
])

compact_chain = compact_prompt | llm | StrOutputParser()

carry_forward = compact_chain.invoke({
    "domain": "resume_matching",
    "task": "batch evaluation of 10 resumes against JD",
    "artifacts": "baseline_scores.csv (Draft), evaluation_rubric_v1.md (Frozen)",
    "transcript": transcript,
    "preserve_rules": "all scores, ranking order, key skill gaps, flagged candidates",
    "discard_rules": "full resume text, JD boilerplate, formatting instructions"
})
```

---

## 21. Report Generation Pipeline (Pattern)

**Description**: A multi-stage LCEL pipeline that follows the Ingest → Structure → Evaluate → Narrate → Deliver pattern for producing documents. Each stage is a separate chain or `RunnableLambda`. Deterministic stages (outline assembly, template rendering, file writing) use `RunnableLambda`. Generative stages (analysis, narrative synthesis) use LLM chains. The pipeline takes raw data in and produces a formatted report artifact out.

**Use Case**: Transferring your manual LLM report creation into a reproducible pipeline. Instead of copy-pasting data into Claude.ai, crafting a prompt, revising the output, and manually formatting — the pipeline runs end-to-end. Swap the prompts to generate different report types (sprint summaries, evaluation reports, compliance matrices) using the same orchestration skeleton.

**Example Code 1** — Three-stage report pipeline:
```python
from langchain_core.runnables import RunnableLambda
from pathlib import Path
import json

# Stage 1: INGEST — deterministic, no LLM
def gather_report_data(inputs: dict) -> dict:
    """Collect scores, rankings, and metadata from CSV/JSON files."""
    scores = Path(inputs["scores_path"]).read_text()
    rubric = Path(inputs["rubric_path"]).read_text()
    return {**inputs, "scores_data": scores, "rubric": rubric}

# Stage 2: NARRATE — generative, needs LLM
narrate_prompt = ChatPromptTemplate.from_messages([
    ("system", Path("prompts/system_report_narrator_v1.md").read_text()),
    ("human", "Scores:\n{scores_data}\n\nRubric:\n{rubric}\n\nGenerate executive summary and per-candidate narratives.")
])
narrate_chain = narrate_prompt | llm | StrOutputParser()

# Stage 3: DELIVER — deterministic, no LLM
def write_report(narrative: str) -> str:
    """Write final report to file with artifact header."""
    report = f"# Sprint Evaluation Report\n**Date**: 2026-02-22 | **Status**: Draft\n\n{narrative}"
    out_path = Path("reports/sprint_eval_report_v1.md")
    out_path.write_text(report)
    return f"Report written to {out_path}"

# Compose
pipeline = RunnableLambda(gather_report_data) | narrate_chain | RunnableLambda(write_report)
result = pipeline.invoke({"scores_path": "baseline_scores.csv", "rubric_path": "evaluation_rubric_v1.md"})
```

**Example Code 2** — Parameterized report template (swap domain, keep skeleton):
```python
def build_report_pipeline(domain: str, version: int):
    """Factory: same orchestration skeleton, different domain prompts."""
    sys_prompt = Path(f"prompts/system_report_{domain}_v{version}.md").read_text()
    human_prompt = Path(f"prompts/human_report_{domain}_v{version}.md").read_text()

    narrate = ChatPromptTemplate.from_messages([
        ("system", sys_prompt),
        ("human", human_prompt)
    ]) | llm | StrOutputParser()

    return RunnableLambda(gather_report_data) | narrate | RunnableLambda(write_report)

# Same skeleton, different domains
resume_report = build_report_pipeline("resume_match", 1)
rfx_report = build_report_pipeline("rfx_scoring", 1)
```

---

## 22. Token Tracking & Cost Accounting

**Description**: `get_openai_callback` is a context manager that captures token counts and estimated cost for all LLM calls within its scope. Works with OpenAI-compatible APIs (including OpenRouter). For direct Anthropic API, use the `usage` field from the response metadata. Combine with the Session Journal callback (Section 19) for per-invocation cost tracking.

**Use Case**: Understanding what your automated workflows cost vs. manual Claude.ai usage. When running batch evaluations across 10+ resumes, you need to know: total tokens consumed, cost per resume, cost per chain version. Feeds directly into ROI analysis — does the automation save enough time to justify the API spend?

**Example Code 1** — OpenRouter / OpenAI-compatible tracking:
```python
from langchain_community.callbacks import get_openai_callback

chain = prompt | llm | StrOutputParser()

with get_openai_callback() as cb:
    results = chain.batch(inputs, config={"max_concurrency": 3})

print(f"Total tokens: {cb.total_tokens}")
print(f"Prompt tokens: {cb.prompt_tokens}")
print(f"Completion tokens: {cb.completion_tokens}")
print(f"Total cost (USD): ${cb.total_cost:.4f}")
print(f"Per-resume avg: ${cb.total_cost / len(inputs):.4f}")
```

**Example Code 2** — Direct Anthropic response metadata:
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0, max_tokens=1024)

# invoke returns AIMessage with usage metadata
response = llm.invoke(messages)
usage = response.usage_metadata  # dict with input_tokens, output_tokens
print(f"Input: {usage['input_tokens']}, Output: {usage['output_tokens']}")

# Accumulate across a batch manually
total_input = 0
total_output = 0
for inp in inputs:
    resp = (prompt | llm).invoke(inp)
    total_input += resp.usage_metadata["input_tokens"]
    total_output += resp.usage_metadata["output_tokens"]
```

---

## Expanded Composition Reference

```
# --- Sprint-Scoped Patterns (Sections 1–15) ---

# Minimal viable chain (Days 1–2)
chain = ChatPromptTemplate | ChatAnthropic | StrOutputParser

# Structured output chain (Day 2+)
chain = ChatPromptTemplate | ChatAnthropic | PydanticOutputParser

# Few-shot chain (Day 3)
chain = FewShotPromptTemplate | ChatAnthropic | StrOutputParser

# RAG chain (Day 4)
chain = RetrievalQA(retriever=Chroma.as_retriever(), llm=ChatAnthropic)

# Memory chain (Day 5)
chain = ConversationChain(llm=ChatAnthropic, memory=ConversationSummaryMemory)

# Staged pipeline (Day 6)
pipeline = ingest_chain | structure_chain | evaluate_chain | narrate_chain

# --- Workflow Transfer Patterns (Sections 16–22) ---

# Deterministic step in pipeline (Section 16)
chain = RunnableLambda(parse_pdf) | prompt | llm | RunnableLambda(write_csv)

# Batch processing (Section 17)
results = chain.batch(inputs, config={"max_concurrency": 3})

# Versioned prompt loading (Section 18)
chain = load_prompt_pair("resume_match", 2) | llm | parser

# Logged chain execution (Section 19)
result = chain.invoke(inputs, config={"callbacks": [journal, handler]})

# On-demand /compact (Section 20)
carry_forward = compact_chain.invoke({"transcript": session_transcript})

# Report generation (Section 21)
report = RunnableLambda(gather) | narrate_chain | RunnableLambda(write)

# Cost-tracked batch (Section 22)
with get_openai_callback() as cb:
    results = chain.batch(inputs)
```

---

## Manual → LangChain Transfer Map

| What You Do Manually | LangChain Equivalent | Section |
|---------------------|---------------------|---------|
| Save prompts as files with naming convention | `prompt.save()` + file-based registry | 18 |
| Keep work journals in chat sessions | `FileCallbackHandler` + `SessionJournal` callback | 19 |
| Run `/compact` to summarize and carry forward | On-demand compact chain | 20 |
| Create reports via LLM conversation | Report generation pipeline | 21 |
| Copy-paste same prompt for multiple docs | `chain.batch()` | 17 |
| Insert manual steps between LLM calls | `RunnableLambda` / `RunnablePassthrough` | 16 |
| Estimate cost of AI-assisted work | `get_openai_callback` + `usage_metadata` | 22 |
| Score outputs against rubric | `PydanticOutputParser` + rubric chain | 7 + 21 |
| Carry context between chat sessions | File-based carry-forward + compact chain | 18 + 20 |

---

*Artifact*: `langchain_cheatsheet_expansion_v1.md` | *Status*: Draft | *Next*: Merge into `langchain_core_cheatsheet_v2.md` after review