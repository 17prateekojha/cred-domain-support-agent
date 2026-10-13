from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

from src.cred_support_agent.rag.retrieval import retrieve_top_k


def document_level_metrics(retrieved_chunks: Sequence[Dict[str, Any]], relevant_docs: Iterable[str]) -> Dict[str, Any]:
    retrieved_docs: List[str] = []
    for chunk in retrieved_chunks:
        metadata = chunk.get("metadata") or {}
        doc_id = metadata.get("doc_id") or chunk.get("doc_id") or metadata.get("document_id")
        if doc_id and doc_id not in retrieved_docs:
            retrieved_docs.append(doc_id)
    truth_set = set(relevant_docs)
    retrieved_set = set(retrieved_docs)
    true_positives = len(retrieved_set & truth_set)
    precision = (true_positives / len(retrieved_set)) if retrieved_set else 0.0
    recall = (true_positives / len(truth_set)) if truth_set else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "retrieved_documents": retrieved_docs,
        "relevant_documents": sorted(truth_set),
        "true_positives": true_positives,
    }


def evaluate_strategy(collection, query_to_docs: Mapping[str, Sequence[str]], top_k: int = 5) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for query, relevant_docs in query_to_docs.items():
        retrieved = retrieve_top_k(collection, query, top_k=top_k)
        metrics = document_level_metrics(retrieved, relevant_docs)
        rows.append({
            "query": query,
            "relevant_docs": sorted(set(relevant_docs)),
            "retrieved_docs": metrics["retrieved_documents"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
        })
    return rows


def summarize_strategy_metrics(rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    if not rows:
        return {"avg_precision": 0.0, "avg_recall": 0.0, "avg_f1": 0.0}
    avg_precision = sum(item["precision"] for item in rows) / len(rows)
    avg_recall = sum(item["recall"] for item in rows) / len(rows)
    avg_f1 = sum(item["f1"] for item in rows) / len(rows)
    return {
        "avg_precision": round(avg_precision, 4),
        "avg_recall": round(avg_recall, 4),
        "avg_f1": round(avg_f1, 4),
    }


def compare_chunking_strategies(fixed_collection, sentence_collection, query_to_docs: Mapping[str, Sequence[str]], top_k: int = 5) -> Dict[str, Any]:
    fixed_rows = evaluate_strategy(fixed_collection, query_to_docs, top_k=top_k)
    sentence_rows = evaluate_strategy(sentence_collection, query_to_docs, top_k=top_k)
    return {
        "fixed_size_overlap": {
            "rows": fixed_rows,
            "summary": summarize_strategy_metrics(fixed_rows),
        },
        "sentence_based": {
            "rows": sentence_rows,
            "summary": summarize_strategy_metrics(sentence_rows),
        },
    }


QUERY_DOCUMENT_MAP: Dict[str, Sequence[str]] = {
    "What are the general eligibility requirements for a home loan?": ["loan_eligibility.md"],
    "How is the EMI on a large loan typically computed?": ["emi_calculation.md"],
    "Which KYC documents are required for verification?": ["kyc_requirements.md"],
    "What steps are taken during a fraud dispute resolution?": ["fraud_disputes.md"],
    "How do interest-rate slabs differ by risk profile?": ["interest_rate_slabs.md"],
    "Are prepayment penalties common in this sample policy?": ["prepayment_rules.md"],
    "What are the usual minimum-balance expectations?": ["minimum_balance.md"],
    "Which factors can impact a credit score in this sample policy?": ["credit_score_factors.md"],
    "How does the account closure process begin?": ["account_closure.md"],
    "What are the general rules for joint accounts?": ["joint_account_rules.md"],
    "Who is usually eligible for an NRI account in this project?": ["nri_account_eligibility.md"],
    "Explain the relationship between loan amount and repayment tenor.": ["loan_eligibility.md", "emi_calculation.md"],
    "What is the weather in Mumbai today?": [],
    "Can you tell me whether I should be approved for a bank loan without any policy context?": [],
}
