# Chunking metrics

This summary reflects the project's own retrieval evaluation and is intentionally deterministic under `MOCK_LLM`.

## Recommendation

The fixed-size-with-overlap strategy is preferred for this project because its average F1 score is 0.5000 versus 0.3889 for the sentence-based strategy. The fixed strategy also preserves a stable recall pattern across the selected evaluation queries, which is important for policy-grounded answers in the Cred domain.

## Fixed-size-overlap

{
  "rows": [
    {
      "query": "What are the general eligibility requirements for a home loan?",
      "relevant_docs": [
        "loan_eligibility.md"
      ],
      "retrieved_docs": [
        "emi_calculation.md",
        "loan_eligibility.md",
        "fraud_disputes.md"
      ],
      "precision": 0.3333,
      "recall": 1.0,
      "f1": 0.5
    },
    {
      "query": "How is the EMI on a large loan typically computed?",
      "relevant_docs": [
        "emi_calculation.md"
      ],
      "retrieved_docs": [
        "emi_calculation.md",
        "loan_eligibility.md",
        "fraud_disputes.md"
      ],
      "precision": 0.3333,
      "recall": 1.0,
      "f1": 0.5
    },
    {
      "query": "What steps are taken during a fraud dispute resolution?",
      "relevant_docs": [
        "fraud_disputes.md"
      ],
      "retrieved_docs": [
        "loan_eligibility.md",
        "fraud_disputes.md",
        "emi_calculation.md"
      ],
      "precision": 0.3333,
      "recall": 1.0,
      "f1": 0.5
    }
  ],
  "summary": {
    "avg_precision": 0.3333,
    "avg_recall": 1.0,
    "avg_f1": 0.5
  }
}

## Sentence-based

{
  "rows": [
    {
      "query": "What are the general eligibility requirements for a home loan?",
      "relevant_docs": [
        "loan_eligibility.md"
      ],
      "retrieved_docs": [
        "loan_eligibility.md",
        "emi_calculation.md",
        "fraud_disputes.md"
      ],
      "precision": 0.3333,
      "recall": 1.0,
      "f1": 0.5
    },
    {
      "query": "How is the EMI on a large loan typically computed?",
      "relevant_docs": [
        "emi_calculation.md"
      ],
      "retrieved_docs": [
        "fraud_disputes.md",
        "loan_eligibility.md"
      ],
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0
    },
    {
      "query": "What steps are taken during a fraud dispute resolution?",
      "relevant_docs": [
        "fraud_disputes.md"
      ],
      "retrieved_docs": [
        "loan_eligibility.md",
        "fraud_disputes.md"
      ],
      "precision": 0.5,
      "recall": 1.0,
      "f1": 0.6667
    }
  ],
  "summary": {
    "avg_precision": 0.2778,
    "avg_recall": 0.6667,
    "avg_f1": 0.3889
  }
}
