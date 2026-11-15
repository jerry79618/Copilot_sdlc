# External adapters — connection policy (not implemented in v0.1)

To support real A/B/C systems, implement a **separately reviewed** adapter using approved test-only APIs, a sandbox or trusted MCP tools.

## Required integration contract

Each operation must document:
1. Owning system and team; read/write privileges and test environment only.
2. Identity and permissions (secrets supplied by CI secret store, never committed).
3. Supported fixture types / prerequisites, correlation ID and idempotency.
4. Readiness/read-only precheck, bounded retry/backoff and timeout.
5. Observable assertions (API/DB/event/trace) and evidence retention/redaction.
6. Cleanup/rollback strategy and authorization, including failure paths.
7. A test showing `BLOCKED` on outage/missing permission; never false-PASS.

## Integration strategy

- Start with a read-only adapter to discover records and status.
- Add approved synthetic provisioning to staging with explicit environmental guardrails.
- Implement per-system retry/rate limits and correlation IDs.
- Integrate Selenium/Cucumber/JUnit runners through controlled subprocesses or GitHub Actions jobs; keep their results in structured evidence.
- Keep real adapters unavailable by default. `DemoAdapter` in `sdlc/verification.py` is intentionally in-memory and cannot mutate external systems.
