# Architecture Plan: Cred Domain Support Agent (CrewAI)

This document translates the PRD into an implementation-ready architecture for the Cred Domain Support Agent. It focuses on the required deliverables, constraints, and evidence needed for a deterministic, local-only, MOCK_LLM-based capstone project.

## 1. Purpose and Design Goals

The solution is a domain support assistant for banking and lending operations. It must:

- Answer policy questions using only project-authored knowledge-base evidence.
- Check a fabricated loan application record by ID and return status plus a computed escalation score.
- Maintain conversation context within a single process run.
- Mask fixed-format PII before inference and logging.
- Refuse unsupported or unsafe responses.
- Validate outputs with Pydantic schemas.
- Submit drafts to an independent AutoGen review stage before finalizing.
- Run under `MOCK_LLM` with zero API keys and zero network access.

The core architectural principle is deterministic evidence-based operation: every answer must be grounded in retrieved context, validated against a schema, and limited by governance rules.

## 2. Non-Functional and Operational Constraints

The architecture must satisfy the following constraints from the PRD:

- Single public repository deliverable.
- README must state that the Cred (Banking & FinTech) track is completed.
- All graded flows run under `MOCK_LLM` without real APIs.
- CrewAI telemetry must be disabled before `crew.kickoff()`.
- Local SentenceTransformers embeddings and local ChromaDB must be used.
- Real data, production integrations, and network-dependent LLM access are out of scope.
- All invented policy content must be clearly labeled as illustrative and not official Cred policy.
- Fixed-format PII masking applies to PAN, Aadhaar, and bank account numbers only.
- Model input and logs must not contain raw masked values.

## 3. High-Level System Architecture

### 3.1 Layered architecture

The system is organized into six layers:

1. Data Layer
   - Synthetic loan dataset generator
   - Knowledge-base markdown documents
   - Evaluation and transcript artifacts

2. Retrieval and Indexing Layer
   - Chunking engines
   - SentenceTransformers embeddings
   - ChromaDB collections
   - Retrieval calibration and grounding logic

3. Agent Orchestration Layer
   - CrewAI agents
   - Tool definitions
   - Session memory
   - Structured response validation

4. Governance and Safety Layer
   - PII masking
   - Prompt-injection detection
   - Output-groundedness checks
   - Least-autonomy permissions
   - Budget enforcement and response caching

5. Review and Evaluation Layer
   - AutoGen review team
   - Deterministic evaluation harness
   - Metrics computation and reporting

6. Delivery Layer
   - FastAPI HTTP endpoints
   - WebSocket chat support
   - JSONL observability logging

## 4. Detailed Component Breakdown

### 4.1 Data layer

#### dataset.py

Responsibilities:
- Generate deterministic synthetic loan records.
- Ensure at least 40 records.
- Cover all categories and statuses.
- Apply a realistic loan-amount range with documented rationale.
- Track `days_since_created` (0–30), `flagged_for_fraud_review`, and status/category distribution.

Key design choices:
- Fixed seed for reproducibility.
- Category weights and status weights documented in README.
- Fraud-review percentage constrained to 10–30% via seed/weight selection.
- Validation assertions ensuring all required categories/statuses appear and all constraints hold.

#### Knowledge base

Responsibilities:
- Provide at least 12 project-authored documents, each 2–5 sentences.
- Cover all required topics:
  - Loan eligibility criteria by loan type
  - EMI calculation rules
  - Credit-card fee structure
  - KYC document requirements
  - Fraud-dispute resolution process
  - Account-closure process
  - Interest-rate slabs
  - Prepayment-penalty rules
  - Minimum-balance requirements
  - Credit-score impact factors
  - Joint-account rules
  - NRI-account eligibility
- Clearly label content as illustrative sample policy and not official Cred policy.

### 4.2 Retrieval and indexing layer

#### Chunking strategies

Two strategies are implemented and compared:

1. Fixed-size chunks with overlap
2. Sentence-based chunks

Each strategy is embedded locally with SentenceTransformers and stored in a separate ChromaDB collection using `collection.upsert()`.

#### RAG core responsibilities

- Chunk source documents.
- Generate embeddings.
- Store chunks with metadata that links each chunk back to the parent document.
- Retrieve top-k matching chunks for a query.
- Support grounded generation where answers are generated only from retrieved context.
- Evaluate retrieval using document-level precision/recall after deduplicating parent documents.

#### Grounded generation logic

- Query retrieval uses top-k chunk results from the selected collection.
- A fallback threshold is calibrated using measured similarity values.
- At least 3 in-scope queries and 2 out-of-scope queries are used to select a threshold between the observed clusters.
- If similarity is below threshold, the system returns a safe “I don’t know” response.

### 4.3 Agent orchestration layer

#### CrewAI crew structure

The orchestration layer includes at least three agents:

1. Retrieval Agent
   - Invokes the RAG retrieval tool.
   - Finds relevant chunks for a user query.

2. Lookup Agent
   - Calls `check_loan_application_status(record_id: str) -> dict`.
   - Only this agent has permission to access the loan-application lookup tool.

3. Response Composer
   - Merges retrieval evidence and application lookup data.
   - Creates a draft answer in a validated structured-output schema.

#### Tools

- `rag_lookup(query: str, top_k: int, collection_name: str) -> ...`
- `check_loan_application_status(record_id: str) -> dict`

The tool boundary is explicit and least-privileged. No other agent is allowed to call the lookup tool.

#### Session memory

- Use LangChain `InMemoryChatMessageHistory` with `RunnableWithMessageHistory`.
- Maintain context across turns within the same process.
- Demonstrate both a multi-turn session and a fresh reset conversation.

#### Structured outputs

- Define a Pydantic `BaseModel` for final crew responses.
- Validate every output before returning it to the caller.
- Fail safely on invalid or schema-breaking output.

## 5. Governance and Safety Architecture

### 5.1 Input guardrails

Input-side checks occur before inference or prompt assembly:

- Mask PAN numbers, Aadhaar numbers, and bank account numbers.
- Detect prompt injection attempts and refuse or neutralize malicious instructions.
- Apply masking to both model input and logged request text.

The implementation must not rely on unstructured string matching for sensitive values beyond the fixed-format patterns required by the PRD. It should use deterministic regex-based masking for the supported field types.

### 5.2 Output guardrails

Output-side checks enforce evidence-based answering:

- Determine whether retrieved context supports the response.
- Refuse to answer when evidence is insufficient.
- Use the calibrated retrieval threshold and groundedness signals to block unsupported claims.

### 5.3 Least autonomy and governance controls

The project applies a four-layer governance model:

- Application layer: only Lookup Agent can access loan status data.
- Risk classification: medium risk due to financial-policy and loan-record handling, with limitations preventing lending decisions.
- Runtime layer: request budget enforcement with capped token/cost approximations.
- Response layer: caching, structured validation, evidence checking, and review.

### 5.4 Budget and cache

- Per-request budget cap enforced before tool or model execution.
- Oversized requests rejected before silent budget overrun.
- In-memory response cache normalized on query text.
- Repeated identical queries return a cache hit and skip redundant LLM/tool work.

## 6. Review and Evaluation Architecture

### 6.1 AutoGen review stage

After CrewAI produces a draft answer, the system sends the draft and retrieved context to an AutoGen two-agent review team:

- `Policy-Compliance-Reviewer`
- `Final-Editor`

Requirements:
- Use `RoundRobinGroupChat` with `max_turns=2` or equivalent configured termination.
- `Final-Editor` uses structured output via a Pydantic verdict model.
- Register `StructuredMessage[YourVerdictModel]` with `custom_message_types`.
- Reviewer can approve unchanged or revise the draft.

### 6.2 Evaluation harness

A 15-query evaluation set covers all required knowledge-base topics and includes at least two out-of-scope or edge-case queries.

For each query, the system records:
- Accuracy
- Grounding
- Completeness
- Safety

The evaluation uses an LLM-as-judge prompt under `MOCK_LLM` and documents the scoring limitations.

### 6.3 Logging and observability

One JSONL log record is produced per request. Each log includes:
- Trace ID
- timestamps/timing
- request metadata
- outcome and status
- tool invocation metadata
- retrieval metrics
- cache hit/miss
- guardrail outcomes
- review verdicts

Raw fixed-format PII must never be written to disk.

## 7. API and Runtime Deployment

### 7.1 FastAPI

The system exposes at least:
- `POST /ask`
- `POST /add-document`
- WebSocket endpoint for multi-turn chat

Responsibilities:
- Validate request/response models using Pydantic.
- Route user prompts into the CrewAI flow.
- Run multi-turn chat through WebSocket with graceful disconnect handling.
- Catch `WebSocketDisconnect` so client disconnects do not crash the server.

### 7.2 Request flow

1. Client sends HTTP or WebSocket input.
2. Request enters input guardrails.
3. Prompt is sanitized and masked before model/tool processing.
4. Retrieval tool searches the selected Chroma collection.
5. Loan lookup tool is invoked only by the Lookup Agent.
6. Composer builds structured response draft.
7. Response is validated against Pydantic schema.
8. Groundedness checks ensure evidence supports the answer.
9. AutoGen review team approves or revises.
10. Response is logged to JSONL with masked data only.
11. Client receives final response.

## 8. Data Flow and Component Interaction

### End-to-end flow

```
User input
  -> Input guardrails (PII masking + prompt injection detection)
  -> CrewAI retrieval/lookup orchestration
      -> RAG retrieval from selected Chroma collection
      -> Loan status lookup via check_loan_application_status
      -> Response Composer validates schema
  -> Groundedness and budget checks
  -> AutoGen review stage
  -> Final answer + log emission
```

### Critical dependencies

- `dataset.py` seeds the loan dataset used by lookup logic.
- Knowledge-base corpus drives the retrieval layer and prompts the grounded-generation path.
- Chosen collection selection is fixed as the recommended strategy from Part 1.
- Output validation ensures model output compatibility with the Pydantic schema.
- Review and governance stages add a second layer of enforceable constraints before the answer is returned.

## 9. Suggested Repository Structure

```text
cred-domain-support-agent/
├── README.md
├── PRD.md
├── requirements.txt
├── .env.example
├── dataset.py
├── data/
│   ├── generated_applications.json
│   └── evaluation_queries.json
├── knowledge_base/
│   ├── loan_eligibility.md
│   ├── emi_calculation.md
│   ├── credit_card_fees.md
│   ├── kyc_requirements.md
│   ├── fraud_disputes.md
│   ├── account_closure.md
│   ├── interest_rate_slabs.md
│   ├── prepayment_rules.md
│   ├── minimum_balance.md
│   ├── credit_score_factors.md
│   ├── joint_account_rules.md
│   └── nri_account_eligibility.md
├── src/
│   └── cred_support_agent/
│       ├── config.py
│       ├── mock_llm.py
│       ├── dataset_validation.py
│       ├── rag/
│       │   ├── chunking.py
│       │   ├── embeddings.py
│       │   ├── indexing.py
│       │   ├── retrieval.py
│       │   └── grounded_generation.py
│       ├── tools/
│       │   └── loan_lookup.py
│       ├── crew/
│       │   ├── agents.py
│       │   ├── tasks.py
│       │   └── orchestration.py
│       ├── memory/
│       │   └── sessions.py
│       ├── guardrails/
│       │   ├── input_guardrails.py
│       │   └── output_guardrails.py
│       ├── schemas/
│       │   └── responses.py
│       ├── review/
│       │   ├── verdict.py
│       │   └── autogen_review.py
│       ├── governance/
│       │   ├── permissions.py
│       │   └── budget.py
│       ├── cache/
│       │   └── response_cache.py
│       ├── observability/
│       │   └── jsonl_logging.py
│       └── api/
│           └── main.py
├── tests/
│   ├── test_dataset.py
│   ├── test_rag.py
│   ├── test_lookup.py
│   ├── test_memory.py
│   ├── test_guardrails.py
│   ├── test_api.py
│   ├── test_governance.py
│   ├── test_review.py
│   └── test_cache.py
├── evaluations/
│   ├── retrieval_calibration.json
│   ├── chunking_metrics.md
│   ├── judge_scores.json
│   └── evaluation_report.md
├── transcripts/
│   ├── rag_demo.md
│   ├── crew_tool_calls.md
│   ├── memory_demo.md
│   ├── guardrail_demo.md
│   ├── autogen_review_demo.md
│   ├── governance_demo.md
│   └── cache_demo.md
└── logs/
    └── .gitkeep
```

## 10. Planned Implementation Phases

### Phase 1: Data and retrieval foundation
- Build deterministic dataset generator.
- Author knowledge-base documents.
- Implement both chunkers.
- Embed and index in ChromaDB collections.
- Measure retrieval performance and calibrate fallback threshold.

### Phase 2: Agent orchestration and memory
- Implement loan lookup tool with escalation scoring.
- Build CrewAI multi-agent flow.
- Add LangChain session memory.
- Implement Pydantic response schemas.

### Phase 3: Guardrails and review
- Add PII masking and prompt-injection detection.
- Add groundedness guardrail.
- Add AutoGen review stage with structured verdicts.

### Phase 4: Deployment, observability, and evaluation
- Expose FastAPI endpoints and WebSocket.
- Emit JSONL logs with privacy-safe content.
- Execute a 15-query evaluation set.
- Report scores and averages for accuracy, grounding, completeness, and safety.

### Phase 5: Governance and release readiness
- Enforce request budgets and least-autonomy controls.
- Add response cache and benchmark hit rate.
- Finalize README and reproducibility notes.
- Confirm all acceptance criteria and required transcripts are present.

## 11. Key Architectural Decisions

### Deterministic execution
All major flows must be deterministic under `MOCK_LLM`. That includes dataset generation, retrieval calibration, review, evaluation, and logs.

### Local-only AI stack
SentenceTransformers and ChromaDB run locally. No paid API or external model is required for graded evidence.

### Evidence-first generation
The system never invents policy. It must answer only from retrieved context and guard against unsupported claims.

### Governance by construction
Safety, least autonomy, budget caps, and review are built into the system design instead of being bolted on afterward.

### Privacy by default
Masked input and masked logs prevent raw fixed-format PII from reaching inference or disk storage.

## 12. Risks and Mitigations

### Risk: silent model failure in CrewAI
Mitigation: use a custom `BaseLLM` mock implementation and avoid brittle prompt parsing tricks that can misread template text as tool output.

### Risk: unsupported answers
Mitigation: enforce retrieval similarity threshold and groundedness guardrail before returning an answer.

### Risk: unsafe or unvalidated output
Mitigation: require Pydantic validation and AutoGen review for the final answer.

### Risk: privacy leak
Mitigation: enforce regex-based masking before prompt construction and before writing logs.

### Risk: non-reproducible evaluation
Mitigation: pin model, dataset, and query sets; record all metrics under deterministic `MOCK_LLM` mode.

## 13. Definition of Done Alignment

The architecture is complete when the implementation satisfies every mandatory acceptance criterion in the PRD, including:

- deterministic dataset generation
- twelve+ knowledge-base documents
- local retrieval with two Chroma collections
- grounded generation with threshold calibration
- CrewAI three-agent orchestration with memory and schema validation
- PII masking, prompt-injection detection, and groundedness refusal
- FastAPI + WebSocket deployment
- JSONL observability logging
- 15-query evaluation with all score categories and averages
- AutoGen review stage
- least-autonomy controls, budgets, and response caching

This architecture provides the structural foundation for a compliant implementation of the Cred Domain Support Agent and supports the required proof artifacts for final repository submission.
