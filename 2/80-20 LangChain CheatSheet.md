# LangChain Core Artifacts — TLDR Cheat Sheet
**Author**: Iqbal Yusuf | **Date**: February 2026 | **Status**: Draft | **Version**: v1
**Purpose**: Quick reference for the 20% of LangChain that does 80% of real work

---

## 1. ChatPromptTemplate

**Description**: Composes a structured list of typed messages (System, Human, AI) to send to a chat model. The primary prompt assembly artifact for all modern LLM work. Handles `{variable}` substitution across all message slots.

**Use Case**: Any task requiring a system instruction + user input pattern — resume matching, document analysis, classification. If you're talking to Claude, you need this.

**Example Code 1** — Load from string:
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a resume screening expert for AEC firms."),
    ("human", "Match this resume to the job description.\n\nJD:\n{jd}\n\nResume:\n{resume}")
])
```

**Example Code 2** — Load system prompt from file:
```python
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

system_text = Path("system_prompt.md").read_text()
seed_text = Path("prompt-00.md").read_text()

prompt = ChatPromptTemplate.from_messages([
    ("system", system_text),
    ("human", seed_text)
])
```

---

## 2. SystemMessagePromptTemplate

**Description**: A single-slot template that produces a `SystemMessage`. Used when you need to construct the system message independently before composing it into a `ChatPromptTemplate`. Supports `{variable}` substitution.

**Use Case**: When your system prompt itself contains dynamic content — e.g., injecting the role name or company name into the system instruction at runtime.

**Example Code 1** — Basic:
```python
from langchain_core.prompts import SystemMessagePromptTemplate

sys_template = SystemMessagePromptTemplate.from_template(
    "You are a resume screener for {company}. Role: {role}."
)
```

**Example Code 2** — Compose into ChatPromptTemplate:
```python
from langchain_core.prompts import (
    ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)

sys_msg = SystemMessagePromptTemplate.from_template("You screen resumes for {company}.")
human_msg = HumanMessagePromptTemplate.from_template("Evaluate:\n{resume}")

prompt = ChatPromptTemplate.from_messages([sys_msg, human_msg])
```

---

## 3. HumanMessagePromptTemplate

**Description**: A single-slot template that produces a `HumanMessage`. The user turn. Handles `{variable}` substitution for dynamic input content.

**Use Case**: When you need to inject structured resume or document content into the human turn at runtime, with explicit control over formatting.

**Example Code 1** — Basic:
```python
from langchain_core.prompts import HumanMessagePromptTemplate

human_msg = HumanMessagePromptTemplate.from_template(
    "Job Description:\n{jd}\n\nResume:\n{resume}\n\nProvide match score and rationale."
)
```

**Example Code 2** — With multiline template string:
```python
template = """
Candidate: {candidate_name}
Resume Text:
{resume}

Score against JD criteria. Return JSON.
"""
human_msg = HumanMessagePromptTemplate.from_template(template)
```

---

## 4. ChatAnthropic

**Description**: LangChain's connector to Anthropic's Claude models. Sends the compiled message list to Claude and returns a response object. Configured with model name, temperature, and max tokens.

**Use Case**: Every pipeline that calls Claude. The model layer in every chain you build this sprint.

**Example Code 1** — Basic instantiation:
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0,
    max_tokens=1024
)
```

**Example Code 2** — Via OpenRouter (your current setup):
```python
from langchain_openai import ChatOpenAI  # OpenRouter uses OpenAI-compatible API

llm = ChatOpenAI(
    model="anthropic/claude-sonnet-4-6",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0
)
```

---

## 5. StrOutputParser

**Description**: Extracts the plain string content from a model response object. Converts `AIMessage(content="...")` into a raw Python string. The simplest output parser — use it until you need structure.

**Use Case**: Any chain where the output is free-form text — match narratives, summaries, rationale explanations. Default choice for Days 1–3.

**Example Code 1** — Standalone:
```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
result = parser.invoke(ai_message)  # returns plain string
```

**Example Code 2** — In a chain:
```python
chain = prompt | llm | StrOutputParser()
output = chain.invoke({"jd": jd_text, "resume": resume_text})
print(output)  # plain string, no AIMessage wrapper
```

---

## 6. JsonOutputParser

**Description**: Parses model output as JSON. Instructs the model (via prompt injection) to return valid JSON, then deserializes it into a Python dict. More reliable when combined with `PydanticOutputParser`.

**Use Case**: When you need structured scores — resume match scores, rubric ratings, ranked candidate lists. Essential for `baseline_scores.csv` generation.

**Example Code 1** — Basic:
```python
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()
chain = prompt | llm | parser
result = chain.invoke({"resume": resume_text, "jd": jd_text})
# result is a dict: {"score": 4, "rationale": "..."}
```

**Example Code 2** — With format instructions injected into prompt:
```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

parser = JsonOutputParser()
prompt = PromptTemplate(
    template="Evaluate the resume.\n{format_instructions}\nResume: {resume}",
    input_variables=["resume"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
```

---

## 7. PydanticOutputParser

**Description**: Parses model output into a typed Pydantic model. Enforces schema at runtime — if the model returns malformed JSON, it raises a validation error. The production-grade alternative to `JsonOutputParser`.

**Use Case**: When output schema must be enforced — e.g., every resume must return `score: int`, `strengths: list[str]`, `gaps: list[str]`. Prevents silent schema drift across 10+ resume runs.

**Example Code 1** — Define schema:
```python
from pydantic import BaseModel
from typing import List
from langchain_core.output_parsers import PydanticOutputParser

class ResumeMatch(BaseModel):
    candidate_name: str
    overall_score: int  # 1-5
    strengths: List[str]
    gaps: List[str]
    recommendation: str

parser = PydanticOutputParser(pydantic_object=ResumeMatch)
```

**Example Code 2** — In chain with format instructions:
```python
chain = prompt.partial(
    format_instructions=parser.get_format_instructions()
) | llm | parser

result = chain.invoke({"resume": resume_text, "jd": jd_text})
print(result.overall_score)  # typed int, not string
```

---

## 8. LCEL Pipe Operator ( | )

**Description**: LangChain Expression Language composition operator. Chains runnables left-to-right: output of left becomes input of right. Replaces `SequentialChain` and `LLMChain` for most use cases. Everything in LangChain that implements `Runnable` can be piped.

**Use Case**: Composing prompt → model → parser into a single invocable unit. The primary assembly mechanism for every chain in this sprint.

**Example Code 1** — Basic three-stage chain:
```python
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"jd": jd_text, "resume": resume_text})
```

**Example Code 2** — Multi-stage pipeline (Day 6 pattern):
```python
ingest_chain = ingest_prompt | llm | StrOutputParser()
evaluate_chain = eval_prompt | llm | PydanticOutputParser(pydantic_object=ResumeMatch)
narrate_chain = narrate_prompt | llm | StrOutputParser()

# Sequential: output of each stage feeds next
full_pipeline = ingest_chain | evaluate_chain | narrate_chain
```

---

## 9. RecursiveCharacterTextSplitter

**Description**: Splits long documents into chunks using a hierarchy of separators (paragraphs → sentences → words → characters). The default splitter for most text — respects natural document structure better than fixed-size splitting.

**Use Case**: Chunking resumes and JDs before indexing into a vector store. Critical for Day 4 retrieval pipeline — wrong chunk size kills retrieval quality.

**Example Code 1** — Basic:
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_text(resume_text)
```

**Example Code 2** — On Document objects:
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
doc_chunks = splitter.split_documents(documents)  # preserves metadata
```

---

## 10. Chroma (Vector Store)

**Description**: In-process vector database. Stores document embeddings and enables similarity search. Persists to disk. Your existing ChromaDB setup is compatible — this is the LangChain wrapper around it.

**Use Case**: Day 4 retrieval pipeline. Index supplementary context (role criteria, skill taxonomies, past hire profiles) and retrieve relevant chunks per resume at query time.

**Example Code 1** — Create and persist:
```python
from langchain_community.vectorstores import Chroma
from langchain_anthropic import AnthropicEmbeddings

vectorstore = Chroma.from_documents(
    documents=doc_chunks,
    embedding=AnthropicEmbeddings(),
    persist_directory="./chroma_db"
)
```

**Example Code 2** — Load existing and query:
```python
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=AnthropicEmbeddings()
)
results = vectorstore.similarity_search("Python GIS experience", k=3)
```

---

## 11. RetrievalQA

**Description**: Combines a retriever (vector store query) with an LLM chain into a single callable. Retrieves relevant chunks, injects them into the prompt, and generates a grounded response. The primary RAG chain abstraction.

**Use Case**: Day 4 — augmenting resume matching with retrieved supplementary context (role criteria, department docs, skill taxonomies) without manually managing chunk injection.

**Example Code 1** — Basic setup:
```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    chain_type="stuff"  # "stuff" = inject all chunks into single prompt
)
result = qa_chain.invoke({"query": "Does this candidate have GIS experience?"})
```

**Example Code 2** — With custom prompt:
```python
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": custom_prompt}
)
```

---

## 12. ConversationBufferMemory

**Description**: Stores the full conversation history in memory and injects it into every subsequent prompt. Simple — no summarization, no truncation. Grows linearly with conversation length.

**Use Case**: Day 5 multi-turn resume matching — when you want the model to have full recall of all previous resume assessments while processing the current one. Watch token budget carefully.

**Example Code 1** — Basic:
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
memory.save_context(
    {"input": "Evaluate resume_01"},
    {"output": "Score: 4/5. Strong GIS background..."}
)
```

**Example Code 2** — In a chain:
```python
from langchain.chains import ConversationChain

conversation = ConversationChain(llm=llm, memory=memory)
result = conversation.predict(input="Now evaluate resume_02 relative to resume_01.")
```

---

## 13. ConversationSummaryMemory

**Description**: Maintains a running LLM-generated summary of the conversation instead of full history. Bounded token cost — summary grows slowly regardless of conversation length. Uses an LLM call to summarize after each turn.

**Use Case**: Day 5 — processing 10+ resumes sequentially where full history would exhaust the context window. Mirrors your manual `/compact` command but automated.

**Example Code 1** — Basic:
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(llm=llm, return_messages=True)
# After each resume, memory summarizes instead of appending full text
```

**Example Code 2** — Check current summary:
```python
memory.save_context(
    {"input": "Evaluate resume_03"},
    {"output": "Score: 2/5. Missing required certifications..."}
)
print(memory.load_memory_variables({})["history"])
# Returns condensed summary of all prior assessments, not full transcripts
```

---

## 14. TextLoader / PyPDFLoader / DirectoryLoader

**Description**: Document loaders that read files from disk into LangChain `Document` objects (text content + metadata). `TextLoader` for .txt/.md, `PyPDFLoader` for PDFs, `DirectoryLoader` for bulk-loading a folder.

**Use Case**: Day 1 — ingesting `sprint_data/resumes/` folder into the pipeline. The entry point for all document processing.

**Example Code 1** — Single PDF:
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("sprint_data/resumes/resume_01.pdf")
documents = loader.load()  # list of Document objects, one per page
```

**Example Code 2** — Full directory:
```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

loader = DirectoryLoader(
    "sprint_data/resumes/",
    glob="*.pdf",
    loader_cls=PyPDFLoader
)
all_resumes = loader.load()  # all PDFs in folder as Document list
```

---

## 15. FewShotPromptTemplate

**Description**: Extends `PromptTemplate` with a curated list of input/output examples injected before the actual query. Teaches format, tone, and reasoning pattern simultaneously. Works with an `ExampleSelector` for dynamic selection.

**Use Case**: Day 3 — injecting 2–3 high-quality resume match examples before the actual resume to anchor output quality and format consistency.

**Example Code 1** — Static examples:
```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

examples = [
    {"resume": "10yr GIS dev, ESRI cert...", "assessment": "Score: 5/5. Strong match..."},
    {"resume": "2yr admin, no tech skills...", "assessment": "Score: 1/5. Weak match..."},
]

example_prompt = PromptTemplate(
    input_variables=["resume", "assessment"],
    template="Resume: {resume}\nAssessment: {assessment}"
)

few_shot = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="You are a resume screener. Examples below:",
    suffix="Resume: {input}\nAssessment:",
    input_variables=["input"]
)
```

**Example Code 2** — With SemanticSimilarityExampleSelector:
```python
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma

selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    AnthropicEmbeddings(),
    Chroma,
    k=2  # select 2 most similar examples to current resume
)

few_shot = FewShotPromptTemplate(
    example_selector=selector,
    example_prompt=example_prompt,
    prefix="You are a resume screener:",
    suffix="Resume: {input}\nAssessment:",
    input_variables=["input"]
)
```

---

## Quick Composition Reference

```
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
```

---

*Artifact*: `langchain_core_cheatsheet_v1.md` | *Status*: Draft | *Next*: Promote to Conclusive after Day 7 sprint validation