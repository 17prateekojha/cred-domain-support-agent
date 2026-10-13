# Governance demo

Permission check: only the LookupAgent is allowed to call check_loan_application_status.
Budget check: an oversized request is rejected before exceeding the cap.
Cache check: identical queries reuse the normalized cached result.
