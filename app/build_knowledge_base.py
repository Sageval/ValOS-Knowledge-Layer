import os
import sys

from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

load_dotenv()  # Reads .env into the environment, if one exists

# Ollama's local address - override with an env var for non-default setups
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Path to the source document - override with an env var, or pass as a CLI arg.
# Defaults to the sanitized sample profile shipped in this repo.
PROFILE_PATH = (
    sys.argv[1] if len(sys.argv) > 1
    else os.getenv("PROFILE_PATH", "sample_data/sample_profile.txt")
)

if not os.path.exists(PROFILE_PATH):
    print(f"Error: could not find '{PROFILE_PATH}'.")
    print("Pass a path as an argument (python app/build_knowledge_base.py path/to/file.txt),")
    print("set the PROFILE_PATH environment variable, or add a profile.txt in the project root.")
    sys.exit(1)

# Load the profile document
with open(PROFILE_PATH, "r") as f:
    text = f.read()

# Split into chunks by paragraph - each blank line becomes a split point
# strip() removes extra whitespace, and the if-check skips empty chunks
chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

if not chunks:
    print(f"Error: '{PROFILE_PATH}' produced no usable chunks. Is the file empty?")
    sys.exit(1)

print(f"Loaded {len(chunks)} chunks from {PROFILE_PATH}")

# Initialize ChromaDB - PersistentClient saves data to disk so it survives restarts
client = chromadb.PersistentClient(path="./chroma_db")

# Connect to Ollama's embedding model to convert text into vectors
ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url=OLLAMA_URL,
)

# Drop any existing collection first so re-running this script doesn't collide
# with previously indexed chunks or leave stale data behind
client.delete_collection(name="personal_profile")

# Create (or reuse) a collection - like a table in a database
collection = client.get_or_create_collection(
    name="personal_profile",
    embedding_function=ef,  # Tells ChromaDB how to convert text to vectors
)

try:
    # Add chunks to the collection - ChromaDB automatically generates embeddings
    collection.add(
        ids=[f"chunk{i}" for i in range(len(chunks))],  # Unique ID for each chunk
        documents=chunks,  # The actual text content
        metadatas=[{"source": "profile", "chunk_index": i} for i in range(len(chunks))],
    )
except Exception as e:
    print(f"Error: failed to build embeddings - is Ollama running? ({e})")
    sys.exit(1)

print(f"Added {len(chunks)} chunks to the 'personal_profile' collection.")
print("Knowledge base built successfully!")
