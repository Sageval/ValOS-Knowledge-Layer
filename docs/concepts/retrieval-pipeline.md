# Retrieval Pipeline

## Overview

A retrieval pipeline is the sequence of operations that retrieves relevant information before invoking a language model.

Its purpose is to provide the model with accurate, relevant, and up-to-date context.

Without retrieval, a language model relies solely on its parametric knowledge.

With retrieval, the model reasons over external information supplied by the application.

---

## Generic Pipeline

User Query

↓

Embedding Generation

↓

Vector Search

↓

Relevant Documents

↓

Prompt Construction

↓

Language Model

↓

Grounded Response

---

## Responsibilities

### Query Processing

Accept and normalize the user's request.

### Retrieval

Search the knowledge base for semantically similar documents.

### Context Assembly

Combine retrieved information into a prompt.

### Generation

Use the language model to produce a grounded response.

---

## Key Insight

Retrieval does not replace the language model.

Retrieval supplies evidence.

The language model performs reasoning.