# PRD — Final Capstone: Cred Domain Support Agent (CrewAI)

**Track:** Banking & FinTech (Cred)  
**Estimated duration:** 14 days  
**Total marks:** 100  
**Primary deliverable:** One public GitHub repository containing the complete project  
**Required execution mode for graded evidence:** `MOCK_LLM`, with zero API keys and zero network access

---

## 1. Product Overview

### 1.1 Background

Cred's lending-operations team needs an agent that helps support staff respond to member queries quickly and consistently. The agent must answer loan-policy questions from a knowledge base created for this project and look up the status of a specific loan application using a fabricated, validated dataset.

The capstone combines the building blocks used in production-minded support agents:

- Dataset design and validation
- Local embeddings and vector retrieval
- Grounded generation
- Conversation/session memory
- Tool-calling agents
- Multi-agent orchestration
- Structured outputs
- Input and output guardrails
- Independent answer review
- End-to-end evaluation and observability
- AI governance and cost control
- FastAPI deployment

The implementation must be more than a happy-path demo: it must provide reproducible evidence that the acceptance criteria and governance controls work.

### 1.2 Product objective

Build one working domain-support agent that can:

1. Answer loan-policy questions using only retrieved knowledge-base evidence.
2. Look up a fabricated loan application's status and escalation score.
3. Preserve conversation context within a session during one process run.
4. Detect prompt injection and mask fixed-format PII before model processing and logging.
5. Validate every response against a Pydantic schema.
6. Submit draft answers to an independent AutoGen review stage before returning them.
7. Enforce least autonomy, per-request budget limits, and response caching.
8. Expose the system through HTTP and WebSocket APIs.
9. Produce repeatable end-to-end evaluation results under `MOCK_LLM`.

### 1.3 Scope

**In scope**
- A seeded synthetic loan-application dataset.
- A project-authored knowledge base covering all required topics.
- Two chunking approaches, local SentenceTransformers embeddings, and separate ChromaDB collections.
- Grounded RAG, CrewAI orchestration, LangChain session memory, guardrails, Pydantic output validation, AutoGen review, structured JSONL logging, evaluation, governance, caching, and FastAPI.
- Tests, transcripts, metrics, and documentation inside one repository.

**Out of scope**
- Real customer data or production banking-system integration.
- Actual loan approval, rejection, underwriting, or credit decisions.
- Use of real PAN, Aadhaar, bank-account, applicant-name, or income data.
- Reliance on a paid API or a network-connected LLM for graded acceptance evidence.
- Image, screenshot, diagram, PDF, slide deck, presentation, video, or audio deliverables.

---

## 2. Submission and Operating Requirements

1. Submit exactly **one public GitHub repository link** for the complete project. There are no separate per-part submissions.
2. The first section of `README.md` must state that the **Cred (Banking & FinTech) track is completed**.
3. The README must document the exact deterministic dataset-design choices from Part 1, Task 1:
   - Random seed
   - Category weights
   - Status weights
   - Loan-amount range
   - One-sentence rationale for the amount range
4. Include `dataset.py`, all knowledge-base documents, RAG and indexing code, CrewAI code, AutoGen review code, governance controls, deployment code, tests, evaluation outputs, and transcripts.
5. The graded transcripts and acceptance tests must run under deterministic `MOCK_LLM` mode with zero API keys and zero network access.
6. SentenceTransformers embeddings and ChromaDB must run locally and without a paid account or credit card.
7. A real LLM provider may be supported optionally behind an environment-variable flag, but it must not be required for any acceptance criterion.
8. Set `CREWAI_DISABLE_TELEMETRY=true` or `OTEL_SDK_DISABLED=true` **before the CrewAI crew runs**. Confirm this in `README.md`.
9. Use only fabricated examples and original project-specific dataset, knowledge-base content, code, and analysis.
10. Submit the repository link before the end of the 14-day capstone window.

### 2.1 MOCK_LLM implementation constraints

For CrewAI, implement the mock model by extending CrewAI's documented extension point, `crewai.llms.base_llm.BaseLLM`. Do not rely on intercepting model calls externally.

Avoid these known silent-failure cases:

- **ReAct observation parsing:** CrewAI's built-in ReAct system-prompt template includes the example text `Observation: the result of the action`. A parser that searches the combined conversation for `Observation:` can match the template before a tool has run and incorrectly return placeholder text. Parse the model's generated response, not the system-prompt template.
- **Tool argument dispatch:** Do not identify tool behavior by searching for substrings in tool names. A tool named `rag_lookup` could be misclassified. Dispatch using the tool's declared argument schema.
- **Telemetry/network access:** Disable CrewAI telemetry before `crew.kickoff()` using one of the environment variables specified above. Verify that graded `MOCK_LLM` runs need no network access.

---

## 3. Scenario and Required Vocabularies

### 3.1 Loan categories

Use every value below at least once. Additional values are permitted.

- Personal Loan
- Home Loan
- Auto Loan
- Education Loan
- Business Loan

### 3.2 Application statuses

Use every value below at least once. Additional values are permitted.

- Submitted
- Under Review
- Approved
- Rejected
- Disbursed

### 3.3 Required knowledge-base topics

Create at least **12 separate documents**, each containing **2–5 sentences**, written in your own words and covering every topic:

1. Loan eligibility criteria by loan type
2. EMI calculation rules
3. Credit-card fee structure
4. KYC document requirements
5. Fraud-dispute resolution process
6. Account-closure process
7. Interest-rate slabs
8. Prepayment-penalty rules
9. Minimum-balance requirements
10. Credit-score impact factors
11. Joint-account rules
12. NRI-account eligibility

Knowledge-base content must be clearly identified as project-authored illustrative policy content, not an assertion of Cred's real policies. Avoid presenting invented rules as real company policy.

### 3.4 PII masking scope

The input-side guardrail must demonstrate masking of fixed-format:

- PAN number
- Aadhaar number
- Bank account number

Applicant names and income figures are free text or unformatted numbers that do not have a reliable pattern for a keyless `MOCK_LLM`-only masker. These are explicitly out of scope for automatic pattern masking. Use fabricated examples only for these fields.

---

## 4. Functional Requirements and Work Plan

## Part 1 — Dataset Design & RAG Core (30 marks)

### Task 1. Design and validate the loan-application dataset

Create `dataset.py` with a seeded, deterministic Python generator that produces a `LOAN_APPLICATIONS` list containing at least **40 records**.

Each record must contain:

- `record_id`
- `category`
- `status`
- `loan_amount_inr`
- `days_since_created` — integer from 0 to 30 inclusive
- `flagged_for_fraud_review` — boolean

Requirements:

- Use every required category and status at least once.
- Each required category must have at least 3 records.
- Each required status must have at least 1 record.
- Choose and document a realistic loan-amount range, with a one-sentence rationale.
- Fix and document the random seed, category weights, and status weights.
- Print and report counts by category and status.
- Print and report the percentage of records where `flagged_for_fraud_review=True`.
- The flagged percentage must be between **10% and 30% inclusive**. If the first random draw falls outside the band, change the seed or weights and regenerate; do not hand-edit individual records to force compliance.
- Add validation assertions or tests for all constraints.

### Task 2. Write the knowledge base

Author at least 12 separate knowledge-base documents, each 2–5 sentences long, covering every topic in Section 3.3.

Keep the content original and internally consistent. Clearly label it as illustrative project policy rather than official Cred policy.

### Task 3. Implement and index two chunking strategies

Implement both strategies:

1. Fixed-size chunks with overlap.
2. Sentence-based chunks.

Requirements:

- Embed every chunk in both strategies using a free local SentenceTransformers model.
- Store each strategy in its own separate ChromaDB collection.
- Use `collection.upsert()` to index chunks.
- Preserve metadata linking each chunk to its parent document so evaluation can deduplicate retrieved documents.
- Demonstrate that both collections return sensible results for a sample query.

### Task 4. Implement grounded generation

For a query:

1. Retrieve the top-k chunks from the selected collection.
2. Generate an answer using only the retrieved context.
3. Under `MOCK_LLM`, use retrieval similarity as the groundedness signal; do not claim a real model has independently judged semantic support.
4. Empirically calibrate the fallback threshold:
   - Measure top-1 cosine similarity for at least 3 in-scope queries.
   - Measure top-1 cosine similarity for at least 2 deliberately out-of-scope queries.
   - Choose a threshold between the clusters actually observed.
   - Do not select an untested preset such as 0.5, 0.6, or 0.7.
5. Record measured values and the selected threshold in `README.md`.
6. Demonstrate at least 5 in-scope queries and 1 out-of-scope query that triggers the “I don't know” fallback.

### Task 5. Evaluate and compare the chunking strategies

Use the same minimum of 5 in-scope queries from Task 4.

For both the fixed-size-with-overlap and sentence-based collections:

- Compute precision and recall at the **document level**.
- Map retrieved chunks back to their parent documents.
- Deduplicate parent documents before scoring.
- Show the per-query arithmetic for both strategies.
- Write a 2–3 sentence recommendation identifying the preferred strategy and citing the project's own precision/recall results.

---

## Part 2 — CrewAI Multi-Agent Orchestration, Tools, Memory & Guardrails (30 marks)

Use the RAG core and the recommended collection from Part 1 as fixed inputs to the orchestration layer.

### Task 6. Build the loan-application lookup tool and escalation score

Implement:

`check_loan_application_status(record_id: str) -> dict`

Use the dataset generated by `dataset.py`. The result must include:

- Application status
- `loan_amount_inr`
- `escalation_score` between 0 and 1

The escalation score must combine both `flagged_for_fraud_review` and a normalized recency signal based on `days_since_created`. It must not be a bare boolean OR.

Document the exact formula and the escalation threshold. Justify the threshold using the generated dataset's distribution; for example, explain whether it corresponds to a percentile of `days_since_created`. Include tests for valid and unknown record IDs and boundary values.

### Task 7. Build and run a CrewAI crew

Create a CrewAI crew with at least 3 agents:

1. **Retrieval Agent** — equipped with the RAG retrieval tool.
2. **Lookup Agent** — equipped with `check_loan_application_status`.
3. **Response Composer** — combines retrieval and lookup results into a final draft answer.

Requirements:

- Run the crew using `.kickoff()`.
- Demonstrate the RAG tool and lookup tool being invoked on different sample queries.
- Keep tool permissions explicit and minimal.
- Ensure the mock LLM implementation follows the constraints in Section 2.1.

### Task 8. Add session memory

Use LangChain session-based memory, for example `InMemoryChatMessageHistory` with `RunnableWithMessageHistory`.

Requirements:

- Maintain conversation history across turns within a single process run.
- Demonstrate state being carried across a multi-turn exchange in one transcript.
- Demonstrate a separate fresh conversation where the prior session's state is absent or reset.
- In-process memory is sufficient; persistence across restarts is not required.
- `RunnableWithMessageHistory` may emit a `LangChainDeprecationWarning` recommending LangGraph persistence. This is expected; the class remains usable and the warning need not be silenced.

### Task 9. Add a structured output schema

Define a Pydantic `BaseModel` for crew responses. Every crew response must conform to the schema and be validated in code. Invalid output must be handled safely rather than silently accepted.

### Task 10. Add guardrails

Implement and test:

**Input-side guardrails**
- Mask fixed-format PAN, Aadhaar, and bank-account numbers before model processing.
- Detect prompt injection and refuse or safely handle malicious instructions.
- Demonstrate each input guardrail firing on a deliberate test case.

**Output-side guardrail**
- Check whether the retrieved context supports the answer.
- Refuse to answer when the evidence does not support the question.
- Demonstrate the groundedness guardrail firing on a deliberate test case.

Ensure masking is consistently applied to the text that reaches the model and to the request text that is logged.

---

## Part 3 — Evaluation, Observability & FastAPI Deployment (20 marks)

Use the Part 2 crew as a fixed input.

### Task 11. Deploy with FastAPI

Expose the crew through at least two HTTP endpoints, for example:

- `POST /ask`
- `POST /add-document`

Use Pydantic request/response models where applicable.

Also expose a WebSocket endpoint using `@app.websocket` for real-time multi-turn chat.

Requirements:

- The WebSocket must handle a client disconnecting mid-conversation gracefully.
- Catch `WebSocketDisconnect`.
- A disconnect must not crash the server or prevent other clients from using it.
- Include tests or reproducible instructions for exercising the endpoints and WebSocket.

### Task 12. Add structured logging

Write one JSON Lines (`.jsonl`) entry for every request.

Each entry must include:

- Trace ID
- Timing information
- Appropriate request/outcome metadata

Privacy requirements:

- Logged request text must not contain any raw, unmasked fixed-format PII field that the input guardrail masks.
- Apply the same masking to the text sent to the model and the text written to logs.
- Never write fixed-format PAN, Aadhaar, or bank-account numbers to disk in clear text.
- Include a test that inspects generated logs for unmasked test values.

### Task 13. Evaluate Accuracy, Grounding, Completeness, and Safety

Build a 15-query test set and evaluate the complete system under `MOCK_LLM`.

The test set must include:

- At least one query touching every required knowledge-base topic.
- At least two deliberately out-of-scope or edge-case queries.

For every query, report all four scores:

- Accuracy
- Grounding
- Completeness
- Safety

Use an LLM-as-judge prompt running under `MOCK_LLM`; document how the mock judge assigns scores and its limitations. Report all 4 scores for each of the 15 queries and the average of each score across all 15 queries. Do not report only aggregate scores.

---

## Part 4 — Resilience & Governance (20 marks)

Use the Part 2 crew as a fixed input.

### Task 14. Add an AutoGen review stage

After CrewAI generates its draft, send the draft answer and the original retrieved context to a two-agent AutoGen review team.

Required agents:

1. `Policy-Compliance-Reviewer`
2. `Final-Editor`

Requirements:

- Use `RoundRobinGroupChat` with `max_turns=2`.
- If using `MaxMessageTermination` instead, use `MaxMessageTermination(3)` so both agents can speak; the initiating task message counts as message 1.
- Give the `Final-Editor` a Pydantic structured output using `output_content_type=<YourVerdictModel>`.
- Construct the team with `custom_message_types=[StructuredMessage[YourVerdictModel]]`; otherwise the structured message type may not be registered and the run can fail.
- The verdict model must include:
  - `approved: bool`
  - `final_answer: str`
  - `reason: str`
- The reviewer must either approve the draft unchanged or revise it.
- Demonstrate at least 2 sample queries:
  - One where the draft is approved unchanged.
  - One where the review stage revises the draft, such as a test draft containing a deliberately injected ungrounded claim.
- Include the verdicts and final outputs in transcripts or test artifacts.

### Task 15. Apply the four-layer AI-governance model

#### Application layer — least autonomy

- Only the Lookup Agent may call `check_loan_application_status`.
- No other crew agent may call the lookup tool directly.
- Demonstrate the restriction, for example by testing that the tool is never wired to another agent or by showing that an attempted unauthorized wiring is blocked.
- Include a one-paragraph explanation of the guard and why least autonomy reduces risk.

#### Risk classification

Classify the system as **Low**, **Medium**, or **High** risk using this scheme:

- **Low:** summarization/transcription
- **Medium:** code generation/customer-support tickets
- **High:** medical data, hiring decisions, financial data

Provide a paragraph justifying the classification for this project. Consider that the agent handles financial-domain policy and loan-application records, and explicitly state the limitations that prevent it from making lending decisions.

#### Runtime layer — per-request budget

- Enforce a per-request token/cost budget cap.
- Demonstrate a deliberately oversized request being rejected before it silently exceeds the budget.
- Under `MOCK_LLM`, define a reproducible token/cost accounting approximation and document its limitations.
- Test the boundary and rejection behavior.

### Task 16. Add response caching

Implement an in-memory cache for the grounded-generation step, keyed by normalized query text.

Requirements:

- Normalize query text consistently before key generation.
- Demonstrate that repeating an identical query produces a cache hit.
- Show evidence that the cache hit avoids a redundant LLM/tool call, using a call counter or timing comparison.
- Include before/after evidence in a transcript or test artifact.
- Keep cache behavior deterministic and testable.

---

## 5. Non-Functional Requirements

### 5.1 Reproducibility

- Seed dataset generation.
- Document package and model choices.
- Keep evaluation queries, expected evidence, scoring rules, and outputs in version control.
- Provide one documented setup and test workflow.

### 5.2 Privacy and security

- Use fabricated data only.
- Mask fixed-format PII before inference and logging.
- Detect prompt injection.
- Reject unsupported answers rather than inventing policy.
- Keep agent tool access least-privileged.
- Enforce request budgets.

### 5.3 Reliability

- Validate all generated responses against Pydantic schemas.
- Handle unknown record IDs, invalid inputs, unsupported queries, and oversized requests.
- Handle WebSocket disconnects without terminating the server.
- Include deterministic tests for important failure paths.

### 5.4 Observability

- Emit one JSONL log record per request with trace ID and timing.
- Record tool invocations, retrieval scores, cache hits/misses, guardrail outcomes, review verdicts, and evaluation results where appropriate.
- Never log unmasked fixed-format PII.

### 5.5 Cost and network control

- Default all LLM-dependent components to `MOCK_LLM`.
- Do not require API keys, paid services, or network access for graded runs.
- Disable CrewAI telemetry before crew execution.
- Optional real-provider integrations must be disabled by default and isolated behind environment configuration.

---

## 6. Recommended Repository Structure

The exact layout may vary, but the repository should make each deliverable easy to find. A suggested structure is:

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

Generated databases, virtual environments, secrets, tokens, and local cache files should not be committed unless a specific reproducibility artifact is intentionally required and contains no sensitive information.

---

## 7. README Requirements

The README must begin by stating that the Cred (Banking & FinTech) track has been completed. It must then document:

1. Project purpose and scope.
2. Explicit statement that all required demonstrations run under `MOCK_LLM`, with zero API keys and zero network access.
3. Confirmation that CrewAI telemetry was disabled before crew execution and how it was disabled.
4. Dataset seed, category weights, status weights, amount range, rationale, category counts, status counts, and fraud-review percentage.
5. Local embedding model and ChromaDB collection names.
6. Similarity measurements for at least 3 in-scope and 2 out-of-scope queries, plus the empirically selected fallback threshold.
7. Per-query document-level precision/recall arithmetic for both chunking strategies and the evidence-based recommendation.
8. Escalation-score formula and threshold rationale.
9. CrewAI agent responsibilities and tool invocation evidence.
10. Session-memory and fresh-session transcripts.
11. Structured response schema and validation behavior.
12. PII masking, injection detection, and groundedness guardrail demonstrations.
13. FastAPI endpoints, WebSocket usage, and disconnect handling.
14. JSONL logging format and evidence that raw fixed-format PII never reaches disk.
15. All 15 evaluation queries with Accuracy, Grounding, Completeness, and Safety scores, plus all four averages.
16. AutoGen approval and revision examples with structured verdicts.
17. Least-autonomy demonstration, risk classification, and runtime budget rejection example.
18. Cache-hit demonstration and before/after evidence.
19. Installation, setup, run, and test commands for Windows PowerShell and/or a clearly documented supported shell.
20. Known limitations, especially the limits of a deterministic mock model and the fact that the sample policy content is illustrative rather than official Cred policy.

---

## 8. Acceptance Criteria / Definition of Done

The project is complete only when all criteria below are demonstrably satisfied and the evidence is committed to the single public repository.

### Part 1 — Dataset and RAG

- [ ] `dataset.py` deterministically generates at least 40 valid applications.
- [ ] All required category values are present, with at least 3 records per category.
- [ ] All required status values are present, with at least 1 record per status.
- [ ] Fraud-review flag percentage is between 10% and 30%, achieved by seed/weight selection rather than record hand-editing.
- [ ] Dataset design choices and counts are documented in the README.
- [ ] At least 12 authored knowledge-base documents cover every required topic and each has 2–5 sentences.
- [ ] Both chunking strategies are implemented, embedded locally, and indexed in separate ChromaDB collections using `collection.upsert()`.
- [ ] Both collections demonstrate sensible retrieval.
- [ ] Grounded generation is demonstrated on at least 5 in-scope queries and 1 out-of-scope query that triggers the fallback.
- [ ] Similarity threshold is based on measured in-scope and out-of-scope values and is documented.
- [ ] Document-level precision and recall are computed for both collections on the same 5 or more queries, with per-query arithmetic and a recommendation citing the numbers.

### Part 2 — CrewAI, memory, schemas, and guardrails

- [ ] `check_loan_application_status` returns correct record data and a designed escalation score in `[0, 1]`.
- [ ] The escalation formula and threshold are documented and justified using the dataset distribution.
- [ ] CrewAI includes at least Retrieval, Lookup, and Composer agents and runs through `.kickoff()`.
- [ ] RAG and lookup tools are demonstrably invoked on different sample queries.
- [ ] Multi-turn memory works within one process and is demonstrated in a transcript.
- [ ] A separate fresh conversation demonstrates that previous session state is absent/reset.
- [ ] Every crew response is validated against a Pydantic structured-output schema.
- [ ] PII masking and prompt-injection guardrails each fire on a deliberate test case.
- [ ] The output groundedness guardrail refuses an unsupported answer in a deliberate test case.

### Part 3 — API, logs, and evaluation

- [ ] FastAPI exposes at least 2 working HTTP endpoints with appropriate Pydantic models.
- [ ] A working WebSocket endpoint supports multi-turn chat and handles `WebSocketDisconnect` gracefully.
- [ ] Every request creates one structured JSONL log entry containing a trace ID and timing information.
- [ ] Raw fixed-format PII is masked in both model input and logs; a test verifies it never appears in clear text in the log.
- [ ] A 15-query evaluation set covers every required KB topic and includes at least 2 out-of-scope/edge-case queries.
- [ ] All 15 queries have Accuracy, Grounding, Completeness, and Safety scores under `MOCK_LLM`.
- [ ] The average of each of the four scores is reported.

### Part 4 — Review and governance

- [ ] AutoGen uses a two-agent Round Robin review stage bounded by `max_turns=2`, or the correctly configured alternative termination condition.
- [ ] The Final-Editor uses a Pydantic verdict schema with `approved`, `final_answer`, and `reason`.
- [ ] The team registers `StructuredMessage[YourVerdictModel]` through `custom_message_types`.
- [ ] At least one draft is approved unchanged and at least one is revised; both are documented.
- [ ] Only the Lookup Agent is wired to the loan-lookup tool, and the least-autonomy restriction is demonstrated.
- [ ] Risk classification and justification are documented.
- [ ] An oversized request is rejected by the runtime budget control.
- [ ] A repeated normalized query produces a demonstrated cache hit and avoids a redundant LLM/tool call.

### Final submission

- [ ] One public GitHub repository contains all code, knowledge-base documents, tests, evaluation results, and transcripts.
- [ ] The README starts with the required track-completion statement and includes all required reproducibility choices.
- [ ] The graded path works in `MOCK_LLM` mode without API keys, paid services, or network access.
- [ ] The repository link is submitted before the end of the 14-day capstone window.

---

## 9. Suggested 14-Day Schedule

| Day | Focus | Expected evidence |
|---|---|---|
| 1 | Repository setup, configuration, deterministic dataset | `dataset.py`, validation output, README dataset choices |
| 2 | Knowledge-base authoring | 12+ topic documents |
| 3 | Chunking, embeddings, ChromaDB indexing | Two populated collections and indexing tests |
| 4 | Retrieval calibration and grounded generation | Similarity measurements, fallback demo |
| 5 | Chunking evaluation | Per-query precision/recall and recommendation |
| 6 | Lookup tool and escalation score | Lookup tests and score-distribution evidence |
| 7 | CrewAI mock LLM and three-agent crew | `.kickoff()` transcript and tool-call evidence |
| 8 | Session memory and structured outputs | Multi-turn/fresh-session transcripts and schema tests |
| 9 | Guardrails | PII, injection, and groundedness test evidence |
| 10 | FastAPI and WebSocket | Endpoint tests and disconnect test |
| 11 | JSONL logging and 15-query evaluation | Sanitized logs, full scores, averages |
| 12 | AutoGen review stage | One approval and one revision transcript |
| 13 | Governance, budget, cache, integration testing | Least-autonomy, budget, and cache demonstrations |
| 14 | Documentation, clean reproducibility run, public repository | Complete README, passing tests, final public GitHub link |

The schedule is a planning guide; all acceptance criteria remain mandatory.

---

## 10. Final Deliverable

Deliver **one public GitHub repository link** containing the complete Cred Domain Support Agent capstone. No separate files or media need to be submitted outside the repository. The repository must include the deterministic dataset, authored knowledge base, both RAG indexing strategies, CrewAI orchestration, AutoGen review, FastAPI deployment, governance controls, tests, evaluation reports, and transcripts demonstrating every required task.

All graded demonstrations must run in `MOCK_LLM` mode with zero API keys and zero network access.
