---
name: failure-analysis
description: >
  Triage failed or blocked verification with evidence and safe bounded remediation rather than assuming every failure is a code bug.
---


Inspect exact evidence and reproduce once when safe. Classify:
- PRODUCT_DEFECT: supported by reproducible assertion/root-cause evidence; ask authorization to patch if testing-only.
- TEST_DEFECT: invalid test logic, wrong locator/assertion.
- TEST_DATA_OR_ENVIRONMENT: missing fixture/permissions/CI service.
- EXTERNAL_ADAPTER_UNAVAILABLE: no approved integration connector.
- UNKNOWN: insufficient evidence; propose diagnostics.
Max three bounded attempts in any remediation loop; stop if side effects or confidence are unclear.
Never edit unrelated code to force a PASS. Summarize actual evidence and remaining gaps.
