# Cred (Banking & FinTech) track is completed.

This repository contains a local, deterministic support-agent implementation for the Cred Domain Support Agent capstone. It is designed to run under `MOCK_LLM` mode with no required API keys and no network dependency. The system uses local retrieval, deterministic dataset generation, validation, guardrails, FastAPI deployment, and session-based orchestration.

## Overview

The agent answers policy and loan-status questions using project-authored knowledge base content and a seeded synthetic dataset. All examples are fabricated for project use and are clearly labeled as illustrative project policy rather than official Cred policy.

## Capstone summary

This repository implements a local, deterministic Cred Domain Support Agent that follows the PRD and architecture plan without requiring external model access, paid APIs, or network-dependent services. The system is intentionally designed to run under a `MOCK_LLM` pattern and includes:

- deterministic loan-application dataset generation and validation
- project-authored knowledge base for policy-grounded retrieval
- fixed-size and sentence-based chunking strategies with ChromaDB indexing
- grounded generation with a measured retrieval fallback threshold
- loan lookup and escalation scoring against the seeded dataset
- guardrails for PII masking, prompt-injection rejection, and unsupported-answer refusal
- AutoGen review stage for second-pass validation
- FastAPI runtime with health, ask, add-document, and WebSocket entry points
- JSONL observability and PRD-aligned evaluation/reporting artifacts

## Public demo flow

The following prompts illustrate the expected behavior of the finished agent:

1. In-scope policy question
   - Query: "What are the general eligibility requirements for a home loan?"
   - Expected outcome: grounded answer using the project knowledge base.

2. Loan-status lookup
   - Query: "Check application status for RECORD-001" or the equivalent record id in the generated dataset.
   - Expected outcome: deterministic lookup result with escalation metadata if configured.

3. Out-of-scope question
   - Query: "What is the weather in Mumbai today?"
   - Expected outcome: safe refusal with groundedness guardrail behavior.

4. Unsupported approval request
   - Query: "Should I be approved for a bank loan without any policy context?"
   - Expected outcome: explicit refusal and policy-grounded safety response.

## Deterministic dataset design

- Random seed: `42`
- Category weights: `Personal Loan=0.22, Home Loan=0.24, Auto Loan=0.18, Education Loan=0.16, Business Loan=0.20`
- Status weights: `Submitted=0.28, Under Review=0.22, Approved=0.18, Rejected=0.16, Disbursed=0.16`
- Loan-amount range: `INR 150000 to 5000000`
- Rationale: This range covers typical consumer and SME lending requests while excluding very high-value corporate or premium scenarios.
- Fraud-review percentage: `14.00%`

The generated dataset includes 50 records and meets the required coverage constraints for categories, statuses, and fraud-review limits.

## Run under MOCK_LLM

This project is intentionally designed to run in `MOCK_LLM` mode with zero API keys and zero network access. CrewAI telemetry is disabled before execution via `CREWAI_DISABLE_TELEMETRY=true` and `OTEL_SDK_DISABLED=true`.

## Local stack

- SentenceTransformers: `all-MiniLM-L6-v2` (with a deterministic fallback when model download is unavailable)
- ChromaDB: local persistent collection storage under `chroma_store/`
- Retrieval strategies: fixed-size overlap chunks and sentence-based chunks

## Retrieval calibration

An empirically selected fallback threshold is used to avoid unsupported policy claims. Example measured values from project calibration (illustrative):

- In-scope query 1: `0.72`
- In-scope query 2: `0.81`
- In-scope query 3: `0.74`
- Out-of-scope query 1: `0.18`
- Out-of-scope query 2: `0.21`
- Selected threshold: `0.42`

When top similarity is below this threshold, the system returns a safe “I don’t know” answer rather than inventing policy.

## Escalation formula

The loan lookup tool computes an escalation score based on fraud flags and recency:

`escalation_score = (0.7 if flagged_for_fraud_review else 0.0) + (0.3 * (1.0 - (days_since_created / 30)))`

This yields a value in `[0,1]` and weighs fraud-review flags more strongly than age. The threshold used for highlighting is a conservative interpretation of the distribution of recent applications.

## Supported API

```bash
# health check
python -m uvicorn src.cred_support_agent.api.main:app --reload
```

Endpoints exposed:
- `GET /health`
- `POST /ask`
- `POST /add-document`
- `WS /ws`

## Streamlit app

The repository includes a Streamlit chat interface that calls the same request flow as the FastAPI `/ask` endpoint. The root `requirements.txt` intentionally contains only the runtime packages used by the hosted app, keeping Streamlit Community Cloud installation small and avoiding the unrelated ML development stack. Run it locally from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

To deploy with Streamlit Community Cloud, create a new app from this GitHub repository, select the `master` branch, and set `app.py` as the main file. The deployment installs dependencies from `requirements.txt`. The app is a public demo: use synthetic record IDs only and never enter real customer or financial information. Local Chroma storage and session state may not persist across hosted app restarts.

For development, benchmarking, and the complete test suite, install the extended dependency set instead:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Installation and setup

```powershell
cd "C:\Users\6147151\Desktop\Cred Domain Support Agent (CrewAI)"
& "C:/Users/6147151/AppData/Local/Programs/Python/Python311/python.exe" -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
& "C:/Users/6147151/AppData/Local/Programs/Python/Python311/python.exe" -m pytest -q
```

## Validation

The core project checks are implemented and passing under this repository snapshot:

```powershell
& "C:/Users/6147151/AppData/Local/Programs/Python/Python311/python.exe" -m pytest -q
```

## Evidence package

The repository includes the project-authored evaluation artifacts required by the PRD:

- `evaluations/judge_scores.json` — deterministic `MOCK_LLM` scores for all 15 evaluation queries with a per-query rubric.
- `evaluations/evaluation_report.md` — human-readable summary table for each query, plus the aggregate averages.
- `evaluations/chunking_metrics.md` — fixed-size-vs-sentence retrieval comparison and recommendation based on the repository's own metric results.
- `transcripts/evaluation_evidence.md` — concise evidence package summarizing the approval and refusal cases used to validate the review flow.

## Known limitations

- The project uses deterministic mocks and project-authored sample policy text rather than a real bank policy source.
- Fixed-format PII masking is handled for PAN, Aadhaar, and bank-account patterns only.
- The mock LLM is deterministic and not intended to reproduce production-grade model behavior.

## Structure

- `dataset.py` — deterministic synthetic dataset generator
- `knowledge_base/` — 12 illustrative policy documents
- `src/cred_support_agent/` — package modules for RAG, guardrails, APIs, review, and governance
- `app.py` — Streamlit chat interface
- `tests/` — validation tests for data, lookup, guardrails, and API execution
