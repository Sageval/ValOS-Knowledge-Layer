import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import ollama
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

load_dotenv()  # Reads .env into the environment, if one exists

app = FastAPI()  # Create the FastAPI application

# Ollama's local address - override with an env var for non-default setups
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Connect to the same ChromaDB collection you built in Step 2
client = chromadb.PersistentClient(path="./chroma_db")

ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url=OLLAMA_URL,
)

collection = client.get_or_create_collection(
    name="personal_profile",
    embedding_function=ef,
)


@app.get("/ask")  # This creates a GET endpoint at /ask
def ask(question: str):  # FastAPI automatically reads "question" from the URL query string
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Step 1: RETRIEVE - search ChromaDB for the 2 most relevant chunks
        results = collection.query(
            query_texts=[question],  # ChromaDB converts this to a vector and finds similar chunks
            n_results=2,  # Return the top 2 matches; kept small since profile.txt chunks are short
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Vector search failed: {e}")

    documents = results.get("documents", [[]])[0]
    if not documents:
        raise HTTPException(status_code=404, detail="No relevant context found in the knowledge base.")

    # Combine the matching chunks into a single string
    context = "\n\n".join(documents)

    # Step 2: AUGMENT - build a prompt that includes the retrieved context
    augmented_prompt = f"""Use the following context to answer the question.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {question}"""

    # Step 3: GENERATE - send the augmented prompt to the local LLM
    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[{"role": "user", "content": augmented_prompt}],
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Local LLM unavailable - is Ollama running? ({e})",
        )

    # Return the answer along with the context so users can verify the source
    return {
        "question": question,
        "answer": response["message"]["content"],
        "context_used": documents,
    }
