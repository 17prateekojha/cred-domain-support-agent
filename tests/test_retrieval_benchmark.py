from src.cred_support_agent.rag.benchmarking import QUERY_DOCUMENT_MAP, document_level_metrics, evaluate_strategy
from src.cred_support_agent.rag.chunking import build_document_chunks
from src.cred_support_agent.rag.indexing import build_collection


def _sample_collection():
    docs = [
        {"doc_id": "loan_eligibility.md", "text": "Home loan eligibility requires stable income, credit profile, and debt-to-income checks. These are project policy examples only."},
        {"doc_id": "emi_calculation.md", "text": "EMI is computed from principal, interest rate, and tenure using standard amortization math. This sample policy explains the formula."},
        {"doc_id": "fraud_disputes.md", "text": "Fraud reviews require evidence and a documented dispute path. The policy never guarantees approval during an investigation."},
    ]
    fixed_chunks = build_document_chunks(docs, strategy="fixed")
    sentence_chunks = build_document_chunks(docs, strategy="sentence")
    fixed_collection = build_collection("test_fixed_benchmark", fixed_chunks)
    sentence_collection = build_collection("test_sentence_benchmark", sentence_chunks)
    return fixed_collection, sentence_collection


def test_document_level_metrics_reward_relevant_hits():
    retrieved = [
        {"metadata": {"doc_id": "loan_eligibility.md"}, "text": "eligibility"},
        {"metadata": {"doc_id": "emi_calculation.md"}, "text": "emi"},
    ]
    metrics = document_level_metrics(retrieved, ["loan_eligibility.md"])
    assert metrics["precision"] >= 0.5
    assert metrics["recall"] == 1.0


def test_evaluate_strategy_runs_for_queries():
    fixed_collection, sentence_collection = _sample_collection()
    rows = evaluate_strategy(fixed_collection, {"What are the general eligibility requirements for a home loan?": ["loan_eligibility.md"]}, top_k=3)
    assert rows[0]["query"].startswith("What are the general eligibility")
    assert len(rows) == 1
    assert rows[0]["precision"] >= 0.0
    assert rows[0]["recall"] >= 0.0
    assert sentence_collection is not None
    assert "loan_eligibility.md" in QUERY_DOCUMENT_MAP["What are the general eligibility requirements for a home loan?"]
