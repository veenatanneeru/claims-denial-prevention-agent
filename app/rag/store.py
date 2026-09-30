"""In-memory vector store over the policy documents (rebuilt on startup, so it stays stateless)."""
from functools import lru_cache
from pathlib import Path

import chromadb

POLICY_DIR = Path(__file__).resolve().parents[2] / "data" / "policies"


@lru_cache(maxsize=1)
def _collection():
    client = chromadb.EphemeralClient()
    collection = client.get_or_create_collection("policies")
    files = sorted(POLICY_DIR.glob("*.md"))
    collection.add(
        ids=[f.stem for f in files],
        documents=[f.read_text() for f in files],
        metadatas=[{"source": f.name} for f in files],
    )
    return collection


def search(query: str, k: int = 3) -> list[dict]:
    result = _collection().query(query_texts=[query], n_results=k)
    return [
        {"source": meta["source"], "text": doc}
        for doc, meta in zip(result["documents"][0], result["metadatas"][0])
    ]