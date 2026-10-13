# RAG demo

This transcript demonstrates the deterministic retrieval and policy-context flow used in the project. The system accepts project-authored knowledge-base content and uses the calibrated threshold to refuse unsupported claims.

Example query: "What are the general eligibility requirements for a home loan?"
Answer: "Based on the knowledge base: Loan eligibility, EMI, KYC, fraud reviews, interest-rate slabs, and minimum balance rules are covered in the project knowledge base."

Example unsupported query: "What is the weather in Mumbai today?"
System answer: "I don't know. The retrieved policy context does not support a confident answer."
