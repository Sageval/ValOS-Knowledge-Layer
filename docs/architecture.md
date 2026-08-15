# ValOS Knowledge Layer — Architecture

This document covers system-level design decisions specific to this project. For a general explanation of what a retrieval pipeline is, see [`concepts/retrieval-pipeline.md`](concepts/retrieval-pipeline.md).

---

## Why two entry points instead of one

The project is split into two standalone scripts rather than a single application:

- **`build_knowledge_base.py`** — an offline, one-time (or occasional) indexing step. Reads a source document, chunks it, embeds it, and writes it to ChromaDB.
- **`main.py`** — the always-on API server that only ever *reads* from ChromaDB.

Keeping these separate mirrors how RAG systems are typically deployed: indexing is a batch job that runs when the knowledge base changes, while serving is a long-running process that should stay lightweight and fast. Combining them into one script would mean re-embedding the entire knowledge base on every server restart — wasteful, and it couples two operations that change at different frequencies.

---

## How the three services connect

```text
┌──────────────────┐
│   FastAPI (app)   │  ← main.py
└─────────┬─────────┘
          │ query_texts
          ▼
┌──────────────────┐        ┌───────────────────┐
│     ChromaDB       │◄─────►│ Ollama (embeddings) │  nomic-embed-text
│  (./chroma_db/)    │        └───────────────────┘
└─────────┬─────────┘
          │ retrieved context
          ▼
┌──────────────────┐
│ Ollama (generation) │  phi3:mini
└──────────────────┘
```

ChromaDB doesn't call Ollama directly — it's configured with an `OllamaEmbeddingFunction`, so every time `.query()` or `.add()` runs, ChromaDB internally makes an HTTP call to Ollama's embedding model to convert text to vectors. This is why Ollama must be running *before* either script executes; there's no local fallback.

Generation is a separate, independent Ollama call made directly from `main.py` after context has already been retrieved — ChromaDB has no involvement in that step. This split is what `docs/concepts/embeddings.md` describes as "two models, two responsibilities": the embedding model never sees the final prompt, and the generation model never performs vector search.

---

## Configuration boundary

`OLLAMA_URL` and `PROFILE_PATH` are read from environment variables (via `.env`, see `.env.example`) rather than hardcoded, so the same code runs unmodified whether Ollama is on `localhost` or another host on the network, and whether the knowledge base is built from the sample profile or a different document entirely.

---

## What changes for multi-user (planned)

The current single `personal_profile` collection assumes one user. The planned multi-user direction (see the README roadmap) would require:

- A collection-per-user or metadata-filtered single collection (`{"user_id": "..."}` on each chunk)
- `/ask` accepting a user/profile identifier alongside the question
- `build_knowledge_base.py` accepting a user identifier so ingestion is scoped, not global

No code changes exist for this yet — noted here so the reasoning is documented before implementation starts.
