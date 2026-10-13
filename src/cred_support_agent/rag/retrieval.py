from __future__ import annotations

from typing import Any, Dict, List

from src.cred_support_agent.rag.embeddings import get_embedding_service


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    if not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_top_k(collection, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    service = get_embedding_service()
    query_embedding = service.embed([query])[0]
    raw = collection.query(query_embedding=query_embedding, n_results=top_k)
    docs = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    results = []
    for doc, meta in zip(docs, metadatas):
        item = {"text": doc, "metadata": meta or {}}
        results.append(item)
    return results
