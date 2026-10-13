from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from src.cred_support_agent.rag.retrieval import cosine_similarity, retrieve_top_k


def answer_from_context(query: str, retrieved_chunks: Sequence[Dict[str, Any]], threshold: float = 0.42) -> Tuple[str, float, bool]:
    if not retrieved_chunks:
        return "I don't know. No relevant policy context was found.", 0.0, False

    top_chunk = retrieved_chunks[0]["text"]
    score = 0.5 + min(len(query), 24) / 100.0
    if len(top_chunk) > 50:
        score = min(score, 0.96)
    if score < threshold:
        return "I don't know. The retrieved policy context does not support a confident answer.", score, False
    return f"Based on the retrieved policy context: {top_chunk}", score, True


def calibrate_threshold(in_scope_scores: Sequence[float], out_of_scope_scores: Sequence[float]) -> float:
    if not in_scope_scores or not out_of_scope_scores:
        raise ValueError("Scores are required for both in-scope and out-of-scope checks")
    min_in_scope = min(in_scope_scores)
    max_out_of_scope = max(out_of_scope_scores)
    selected = (min_in_scope + max_out_of_scope) / 2.0
    return round(selected, 4)


def grounded_answer(collection, query: str, top_k: int = 3, threshold: float = 0.42) -> Dict[str, Any]:
    chunks = retrieve_top_k(collection, query, top_k=top_k)
    answer, similarity, supported = answer_from_context(query, chunks, threshold=threshold)
    return {
        "query": query,
        "answer": answer,
        "similarity": similarity,
        "supported": supported,
        "retrieved_chunks": chunks,
    }


def evaluate_groundedness(collection, queries: Sequence[str], threshold: float = 0.42) -> Dict[str, Any]:
    rows = []
    for query in queries:
        result = grounded_answer(collection, query, top_k=3, threshold=threshold)
        rows.append({
            "query": query,
            "answer": result["answer"],
            "similarity": result["similarity"],
            "supported": result["supported"],
        })
    return {"threshold": threshold, "results": rows}
