# Implementation Plan: Cred Domain Support Agent (CrewAI)

This document converts the architecture into a practical, phase-by-phase build plan for the capstone project. It is organized so work can proceed in stable, testable increments without losing traceability to the PRD and architecture requirements.

## 1. Implementation Approach

The project will be built in a layered, incremental sequence:

1. Establish deterministic data and knowledge-base foundation.
2. Build local retrieval and indexing with ChromaDB and SentenceTransformers.
3. Create the loan-lookup tool and crew orchestration layer.
4. Add safety, governance, and review controls.
5. Expose the system through FastAPI and WebSocket APIs.
6. Run evaluation, logging, and final documentation.

Each phase produces evidence artifacts such as tests, transcripts, metrics, and logs that map directly to PRD acceptance criteria.

## 2. Phase-by-Phase Plan

### Phase 1: Data Foundation and Dataset Validation

Objective:
Build the synthetic dataset generator and validate that it satisfies all deterministic and statistical requirements.

Tasks:
- Create `dataset.py`.
- Define a fixed random seed and document it in README.
- Choose and document category weights, status weights, and loan amount range.
- Generate at least 40 records.
- Ensure all required categories and statuses are included.
- Ensure each required category has at least 3 records and each required status has at least 1 record.
- Ensure `flagged_for_fraud_review` percentage falls between 10% and 30% using seed/weight tuning.
- Print category counts, status counts, and fraud-review percentage.
- Add validation assertions/test coverage for structure and constraints.

Files to create/update:
- `dataset.py`
- `tests/test_dataset.py`
- `README.md`

Evidence to produce:
- Dataset generation output showing counts and percentages.
- Validation test results.
- Documentation of dataset rationale and design choices.

Definition of done:
- Dataset is deterministic, valid, and reproducible.
- All acceptance criteria for Task 1 are satisfied.

---

### Phase 2: Knowledge Base Authoring and Document Coverage

Objective:
Create the project-authored knowledge base covering all required topics and keep policy content clearly illustrative.

Tasks:
- Create 12 separate knowledge-base documents.
- Each document should contain 2–5 sentences.
- Cover all required topics from the PRD.
- Explicitly label content as illustrative project policy, not official Cred policy.
- Keep wording internally consistent and original.

Files to create:
- `knowledge_base/loan_eligibility.md`
- `knowledge_base/emi_calculation.md`
- `knowledge_base/credit_card_fees.md`
- `knowledge_base/kyc_requirements.md`
- `knowledge_base/fraud_disputes.md`
- `knowledge_base/account_closure.md`
- `knowledge_base/interest_rate_slabs.md`
- `knowledge_base/prepayment_rules.md`
- `knowledge_base/minimum_balance.md`
- `knowledge_base/credit_score_factors.md`
- `knowledge_base/joint_account_rules.md`
- `knowledge_base/nri_account_eligibility.md`

Evidence to produce:
- Coverage check showing each required topic is present.
- README note that content is illustrative and not official policy.

Definition of done:
- At least 12 authored KB docs exist and cover every required topic.

---

### Phase 3: Retrieval Indexing and Chunking Comparison

Objective:
Implement two retrieval strategies, embed them locally, and index them in ChromaDB collections.

Tasks:
- Implement fixed-size chunking with overlap.
- Implement sentence-based chunking.
- Create a local SentenceTransformers embedding pipeline.
- Create two separate ChromaDB collections.
- Use `collection.upsert()` to index chunks.
- Preserve chunk-to-parent-document metadata.
- Validate retrieval behavior on a sample set of queries.
- Compare strategy-level retrieval quality on the same evaluation set.

Files to create/update:
- `src/cred_support_agent/rag/chunking.py`
- `src/cred_support_agent/rag/embeddings.py`
- `src/cred_support_agent/rag/indexing.py`
- `src/cred_support_agent/rag/retrieval.py`
- `tests/test_rag.py`

Evidence to produce:
- Retrieval outputs for sample queries.
- Per-query precision/recall arithmetic.
- Recommendation for preferred strategy based on results.

Definition of done:
- Both collections run locally and return relevant results.
- Reproducible retrieval evaluation is captured.

---

### Phase 4: Grounded Generation and Similarity Threshold Calibration

Objective:
Generate answers using only retrieved context and calibrate the fallback threshold based on measured in-scope and out-of-scope similarity values.

Tasks:
- Implement grounded generation using top-k chunk retrieval.
- Measure top-1 cosine similarity for at least 3 in-scope queries.
- Measure top-1 cosine similarity for at least 2 out-of-scope queries.
- Select threshold between observed clusters rather than using a preset value.
- Show at least 5 in-scope queries and 1 out-of-scope fallback example.
- Document results in README and evaluation artifacts.

Files to create/update:
- `src/cred_support_agent/rag/grounded_generation.py`
- `evaluations/retrieval_calibration.json`
- `README.md`
- `transcripts/rag_demo.md`

Evidence to produce:
- Similarity values table.
- Fallback demo transcript with “I don’t know”.
- Threshold rationale based on measured data.

Definition of done:
- Grounding threshold is empirically selected and documented.
- Unsupported questions refuse to answer rather than hallucinate.

---

### Phase 5: Loan Status Lookup and Escalation Scoring

Objective:
Implement the lookup tool and its structured risk/escalation logic.

Tasks:
- Create `check_loan_application_status(record_id: str) -> dict`.
- Read from the generated dataset.
- Return application status, `loan_amount_inr`, and `escalation_score` in `[0,1]`.
- Combine `flagged_for_fraud_review` and normalized recency based on `days_since_created`.
- Document exact formula and threshold rationale.
- Justify threshold using dataset distribution and percentiles where relevant.
- Write tests for valid IDs, unknown IDs, and boundary conditions.

Files to create/update:
- `src/cred_support_agent/tools/loan_lookup.py`
- `tests/test_lookup.py`
- `README.md`

Evidence to produce:
- Escalation formula explanation.
- Test results for known/unknown IDs and boundary values.
- Documentation of threshold and distribution logic.

Definition of done:
- Tool returns proper record data and designed escalation scoring.

---

### Phase 6: CrewAI Orchestration, Tools, and Memory

Objective:
Build a three-agent CrewAI flow and ensure multi-turn memory works correctly.

Tasks:
- Create a custom `MOCK_LLM` implementation by extending `BaseLLM`.
- Configure telemetry disablement before `crew.kickoff()`.
- Create Retrieval Agent, Lookup Agent, and Response Composer.
- Keep tool permissions explicit and minimal.
- Ensure the RAG tool and loan lookup tool are used on different sample queries.
- Add `RunnableWithMessageHistory` based session memory.
- Demonstrate a multi-turn conversation and a fresh conversation reset.
- Run the crew through `.kickoff()`.

Files to create/update:
- `src/cred_support_agent/mock_llm.py`
- `src/cred_support_agent/crew/agents.py`
- `src/cred_support_agent/crew/tasks.py`
- `src/cred_support_agent/crew/orchestration.py`
- `src/cred_support_agent/memory/sessions.py`
- `tests/test_memory.py`
- `transcripts/crew_tool_calls.md`
- `transcripts/memory_demo.md`

Evidence to produce:
- Crew execution transcript.
- Evidence of tool usage on separate sample calls.
- Fresh-vs-existing conversation demonstration.

Definition of done:
- Crew orchestrates successfully under `MOCK_LLM`.
- Memory and tool boundaries work as specified.

---

### Phase 7: Structured Output and Guardrails

Objective:
Validate all responses and add safety controls before final generation.

Tasks:
- Define Pydantic response schema for crew output.
- Validate all crew responses against the schema.
- Implement input-side PII masking for PAN, Aadhaar, and bank account numbers.
- Implement prompt-injection detection.
- Implement output-groundedness checks.
- Demonstrate deliberate test cases for each guardrail.
- Apply masking consistently to both prompt text and log text.

Files to create/update:
- `src/cred_support_agent/schemas/responses.py`
- `src/cred_support_agent/guardrails/input_guardrails.py`
- `src/cred_support_agent/guardrails/output_guardrails.py`
- `tests/test_guardrails.py`
- `transcripts/guardrail_demo.md`

Evidence to produce:
- Guardrail tests for mask, injection refusal, and unsupported answer refusal.
- Logs showing masked request content.

Definition of done:
- Every generated answer is schema validated and guarded against misuse.

---

### Phase 8: AutoGen Review Stage and Structured Verdicts

Objective:
Add an independent review stage after the draft answer is created.

Tasks:
- Create `Policy-Compliance-Reviewer` and `Final-Editor` agents.
- Use `RoundRobinGroupChat` with `max_turns=2`.
- Build a verdict model with `approved`, `final_answer`, and `reason`.
- Register `StructuredMessage[YourVerdictModel]` with `custom_message_types`.
- Demonstrate one approval case and one revision case.
- Validate final output before returning to the caller.

Files to create/update:
- `src/cred_support_agent/review/verdict.py`
- `src/cred_support_agent/review/autogen_review.py`
- `tests/test_review.py`
- `transcripts/autogen_review_demo.md`

Evidence to produce:
- Review transcript with one unchanged approval and one revised output.
- Structured verdict examples.

Definition of done:
- Draft response is independently reviewed and either accepted or revised.

---

### Phase 9: FastAPI Deployment and WebSocket Support

Objective:
Expose the system through networked interfaces while preserving safety and structured validation.

Tasks:
- Create FastAPI app with `POST /ask` and `POST /add-document`.
- Add WebSocket endpoint for multi-turn chat.
- Validate Pydantic request/response models.
- Handle `WebSocketDisconnect` gracefully.
- Add reproducible testing instructions for HTTP and WebSocket flows.

Files to create/update:
- `src/cred_support_agent/api/main.py`
- `tests/test_api.py`
- `README.md`

Evidence to produce:
- Endpoint tests.
- WebSocket disconnect handling verification.
- Example curl or client instructions.

Definition of done:
- The core system is deployable and testable via API endpoints.

---

### Phase 10: Logging, Metrics, and Observability

Objective:
Emit privacy-safe structured logs and capture end-to-end execution metadata.

Tasks:
- Implement JSONL logging for every request.
- Include trace ID, timing, request metadata, and outcome.
- Capture tool invocation and retrieval metrics.
- Include cache and guardrail outcomes.
- Ensure no raw PAN/Aadhaar/bank-account values are written to logs.
- Add test to inspect generated logs for unmasked values.

Files to create/update:
- `src/cred_support_agent/observability/jsonl_logging.py`
- `tests/test_api.py` or dedicated log test
- `logs/.gitkeep` and generated log files

Evidence to produce:
- JSONL entries for sample requests.
- Test verifying sanitization of fixed-format PII.

Definition of done:
- Every request creates a structured log record without privacy violations.

---

### Phase 11: Evaluation Harness and Score Reporting

Objective:
Run a 15-query evaluation set under `MOCK_LLM` and report all required metrics.

Tasks:
- Build evaluation query set covering all required KB topics.
- Include at least two deliberately out-of-scope or edge-case queries.
- Run system answers for all 15 queries.
- Score each query on Accuracy, Grounding, Completeness, and Safety.
- Use an LLM-as-judge prompt under `MOCK_LLM`.
- Record how the mock judge scores and its limitations.
- Report all 15 query scores and average scores for each metric.

Files to create/update:
- `data/evaluation_queries.json`
- `evaluations/judge_scores.json`
- `evaluations/evaluation_report.md`
- `README.md`

Evidence to produce:
- Full 15-query detailed score table.
- Averages for all four metrics.
- Documentation of scoring limitations.

Definition of done:
- All evaluation requirements are captured and reproducible.

---

### Phase 12: Governance Controls, Budget, and Cache

Objective:
Implement the final governance controls required by the PRD.

Tasks:
- Add least-autonomy enforcement so only the Lookup Agent can call the loan lookup tool.
- Classify system risk as Low, Medium, or High and justify it.
- Enforce per-request budget caps.
- Demonstrate a deliberately oversized request being rejected.
- Implement in-memory response cache keyed on normalized query text.
- Demonstrate cache hit behavior and show redundant call avoidance.

Files to create/update:
- `src/cred_support_agent/governance/permissions.py`
- `src/cred_support_agent/governance/budget.py`
- `src/cred_support_agent/cache/response_cache.py`
- `tests/test_governance.py`
- `tests/test_cache.py`
- `transcripts/governance_demo.md`
- `transcripts/cache_demo.md`

Evidence to produce:
- Least-autonomy demonstration.
- Oversized request rejection proof.
- Before/after cache evidence.

Definition of done:
- Governance and runtime controls are implemented and demonstrated.

---

### Phase 13: Final Documentation and Repo Readiness

Objective:
Prepare the repository for public submission by aligning documentation, setup, and evidence.

Tasks:
- Ensure README begins with the required track-completion statement.
- Document dataset design choices.
- Document retrieval calibration and similarity threshold.
- Document escalation score formula and threshold logic.
- Document FastAPI endpoints, WebSocket usage, and logging format.
- Document results from evaluation, review, governance, and cache demos.
- Provide installation, setup, and test commands for PowerShell or equivalent shell.
- Document known limitations and deterministic `MOCK_LLM` constraints.
- Verify all repository artifacts exist in the expected structure.

Files to create/update:
- `README.md`
- `PRD.md` (or repository copy if used)
- `.env.example`
- `requirements.txt`

Evidence to produce:
- Final documentation package.
- End-to-end reproduction instructions.

Definition of done:
- README and package metadata are complete and ready for repository submission.

---

## 3. Cross-Cutting Execution Strategy

### Development sequencing
Work should be executed in the following order:

1. Dataset and knowledge base
2. Retrieval and indexing
3. Lookup and crew orchestration
4. Guardrails and validation
5. Review and API exposure
6. Evaluation and governance
7. Documentation and final verification

This order minimizes dependency risk and makes validation possible at every milestone.

### Testing discipline
Each phase should include:
- focused unit tests
- one or more end-to-end validation calls
- artifact capture in transcripts or evaluation files

### Evidence capture
Each phase should leave behind proof of completion in either:
- tests
- transcript markdown files
- JSON evaluation outputs
- logs
- README documentation

This is critical because the project is graded on reproducible evidence rather than only code completeness.

## 4. Milestone Checklist

### Milestone A — Data and RAG foundation
- [ ] Deterministic dataset generated
- [ ] Required categories and statuses present
- [ ] Knowledge base documents authored
- [ ] Local chunking and indexing working

### Milestone B — Crew and lookup functionality
- [ ] Loan lookup tool works
- [ ] CrewAI flow runs under `MOCK_LLM`
- [ ] Session memory works
- [ ] Structured responses validate correctly

### Milestone C — Safety and review
- [ ] PII masking works
- [ ] Prompt injection is detected
- [ ] Groundedness guardrail blocks unsupported answers
- [ ] AutoGen review accepts or revises drafts

### Milestone D — Deployment and evaluation
- [ ] FastAPI and WebSocket are working
- [ ] JSONL logging is implemented
- [ ] 15-query evaluation completed
- [ ] Final metrics are documented

### Milestone E — Governance and release
- [ ] Least autonomy enforced
- [ ] Budget rejection works
- [ ] Response cache works
- [ ] README and final artifacts are complete

## 5. Risk Handling

### Risk: dependency-related delays
Mitigation: keep each phase independent and testable; do not block later phases on perfect optimization.

### Risk: invalid or unsafe outputs
Mitigation: require schema validation, groundedness checks, and review before final responses are returned.

### Risk: hidden privacy leakage
Mitigation: apply masking before prompt generation and before writing logs; explicitly test the log output.

### Risk: environment problems with local ML tooling
Mitigation: constrain all model and retrieval dependencies to local Python libraries that can run without paid services or network access.

## 6. Final Implementation Goal

The capstone should end with a single public repository that clearly demonstrates all required components, proof artifacts, and compliance with the PRD’s deterministic, local-only `MOCK_LLM` execution model.

The final repository should not simply contain a prototype. It should include verifiable evidence for every requirement: dataset generation, retrieval behavior, tool usage, memory handling, safety checks, review, API deployment, logs, evaluation scores, and governance enforcement.
