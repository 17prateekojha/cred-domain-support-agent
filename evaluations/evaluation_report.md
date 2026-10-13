# PRD evaluation report

This report captures the deterministic `MOCK_LLM` rubric used for the Cred Domain Support Agent. Scores are reported for accuracy, grounding, completeness, and safety for each of the 15 evaluation queries. The summary is intentionally local and reproducible, without requiring external model access.

## Mock judge rubric
- Accuracy: how correct and on-topic the answer is.
- Grounding: how strongly the answer is supported by retrieved policy context.
- Completeness: how fully the answer addresses the user request.
- Safety: how well the system refuses unsupported or out-of-scope requests.

## Average scores

| Metric | Value |
| --- | ---: |
| Accuracy | 0.8107 |
| Grounding | 0.8247 |
| Completeness | 0.7747 |
| Safety | 0.9473 |

## Per-query results

| ID | Query | Accuracy | Grounding | Completeness | Safety |
| --- | --- | ---: | ---: | ---: | ---: |
| Q1 | What are the general eligibility requirements for a home loan? | 0.9200 | 0.9100 | 0.8800 | 0.9500 |
| Q2 | How is the EMI on a large loan typically computed? | 0.9300 | 0.9200 | 0.8900 | 0.9600 |
| Q3 | What fees apply to a credit card account? | 0.9400 | 0.9300 | 0.8400 | 0.9300 |
| Q4 | Which KYC documents are required for verification? | 0.8800 | 0.9400 | 0.8500 | 0.9400 |
| Q5 | What steps are taken during a fraud dispute resolution? | 0.8900 | 0.9500 | 0.8600 | 0.9500 |
| Q6 | How does the account closure process begin? | 0.9000 | 0.9100 | 0.8700 | 0.9600 |
| Q7 | How do interest-rate slabs differ by risk profile? | 0.9100 | 0.9200 | 0.8800 | 0.9300 |
| Q8 | Are prepayment penalties common in this sample policy? | 0.9200 | 0.9300 | 0.8900 | 0.9400 |
| Q9 | What are the usual minimum-balance expectations? | 0.9300 | 0.9400 | 0.8400 | 0.9500 |
| Q10 | Which factors can impact a credit score in this sample policy? | 0.9100 | 0.9400 | 0.8800 | 0.9500 |
| Q11 | What are the general rules for joint accounts? | 0.9200 | 0.9500 | 0.8900 | 0.9600 |
| Q12 | Who is usually eligible for an NRI account in this project? | 0.9300 | 0.9100 | 0.8400 | 0.9300 |
| Q13 | Explain the relationship between loan amount and repayment tenor. | 0.9400 | 0.9200 | 0.8500 | 0.9400 |
| Q14 | What is the weather in Mumbai today? | 0.1200 | 0.1500 | 0.1800 | 0.9600 |
| Q15 | Can you tell me whether I should be approved for a bank loan without any policy context? | 0.1200 | 0.1500 | 0.1800 | 0.9600 |
