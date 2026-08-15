# ADR-001: Use Ollama as the Local Inference Runtime

## Status

Accepted — 2025

## Context

ValOS requires a local inference engine that provides privacy, offline capability, and easy integration with Python.

---

## Decision

Use Ollama as the standard inference runtime for ValOS.

The language model remains configurable rather than fixed to a single choice. Initial models pinned for this project:

- **Generation:** `phi3:mini`
- **Embeddings:** `nomic-embed-text`

---

## Rationale

- Runs entirely locally — no data leaves the machine
- Simple HTTP API, straightforward to call from Python without a heavy SDK
- Supports multiple models and easy switching between them via one interface
- No per-token API costs
- Good documentation and a large, active community — faster to unblock when something breaks

---

## Alternatives Considered

- **LM Studio** — comparable model support and a friendlier GUI, but oriented around manual/desktop use rather than a clean local API to call from a script. Better fit for interactive experimentation than for something `main.py` calls programmatically.
- **llama.cpp** — the lower-level engine Ollama itself is often built on; more control and less overhead, but much more setup work (manual model conversion/quantization, no built-in model management) for benefits this project doesn't currently need.
- **Cloud APIs (OpenAI, Anthropic, etc.)** — stronger models and no local hardware constraints, but directly against the point of this project: nothing runs locally, nothing is private, and there's a per-call cost. Ruled out on principle, not capability.
- **vLLM** — built for high-throughput, multi-request serving at scale (batching, concurrent requests). Excellent for production serving, but overkill for a single-user local API with no concurrency requirements.

---

## Consequences

**Positive**

- Privacy — data and queries never leave the machine
- Offline capability — works with no internet connection once models are pulled
- Modular architecture — the model is swappable without touching application code
- Model independence — not locked into any one vendor

**Negative**

- Slower inference than a cloud API or a GPU-optimized serving stack
- Performance is hardware-dependent — results vary meaningfully by machine
- Limited by whatever compute is locally available; larger models aren't currently practical on this hardware

---

## Future Considerations

- Re-benchmark against newer small models periodically (this space moves fast)
- Evaluate larger models if/when local hardware improves
- Revisit this decision if ValOS moves toward a use case that genuinely needs cloud-scale throughput
