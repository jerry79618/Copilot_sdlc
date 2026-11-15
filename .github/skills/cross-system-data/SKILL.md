---
name: cross-system-data
description: >
  Analyze multi-system data dependencies, fixture preparation, async sequence and environment readiness for testing.
---


For each cross-system scenario:
- Record upstream/downstream system owners, allowed API/MCP adapter, test environment and credentials policy.
- Define a dependency DAG with unique IDs, correlation IDs and expected state transitions.
- Prefer synthetic fixture or approved sandbox provisioning; never directly mutate production.
- Confirm prerequisites via read-only check before running the subject test.
- For asynchronous events use bounded status polling / correlation IDs (not arbitrary sleeps).
- If data cannot be created or observed, mark BLOCKED and specify the owner/unblock instructions.
- Capture cleanup plan; real cleanup must be approved and idempotent.
See `docs/external-adapters.md` before connecting a real system.
