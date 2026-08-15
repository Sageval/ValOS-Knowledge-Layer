# Parametric vs. Retrieved Knowledge

## Overview

Large Language Models draw on two very different kinds of knowledge, and understanding the difference is the whole reason RAG exists.

### Parametric Knowledge

- Learned during training and compressed into the model's weights
- Static — it doesn't change unless the model itself is retrained
- Broad but generic: an LLM knows a huge amount about the world in general, and nothing about anything created or changed after its training cutoff, and nothing at all about private information it was never shown

### Retrieved Knowledge

- Fetched at query time, from an external source (documents, a database, an API)
- Dynamic — update the source and the next query immediately reflects it, with no retraining
- Narrow but current and specific: it only knows what's actually in the source, but that source can be exactly the information the model needs

---

## Why this matters in practice

An LLM's parametric knowledge alone can't answer questions about information it was never trained on — most obviously, information that's private, personal, or simply too recent to have been in its training data.

Concretely, in this project: `phi3:mini` on its own has no idea who the profile in `sample_data/sample_profile.txt` belongs to, what they do, or any other detail in that file — that information was never part of its training. Asked directly, it will either say it doesn't know, or worse, guess and hallucinate an answer that sounds plausible but is wrong.

Retrieval is what closes that gap. The chunk containing the relevant detail is fetched from ChromaDB and inserted directly into the prompt (see `docs/concepts/retrieval-pipeline.md`), so the model isn't relying on what it memorized during training — it's reading the answer directly out of the context it was just handed and reasoning over that instead.

This is the core trade-off RAG is built around: parametric knowledge gives an LLM broad general reasoning ability; retrieval gives it access to information — private, current, or otherwise — that reasoning ability alone could never supply.

---

## Related Concepts

- [`embeddings.md`](embeddings.md) — how retrieved text is converted into a searchable form
- [`retrieval-pipeline.md`](retrieval-pipeline.md) — the full sequence from question to grounded answer
- [ADR-001: Ollama](../decisions/ADR-001-ollama.md) — the local runtime both kinds of knowledge pass through in this project
