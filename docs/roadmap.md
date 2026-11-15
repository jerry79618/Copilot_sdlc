# Delivery roadmap

## v0.1 — built
- GitHub Copilot CLI repository agents and task-driven Skills.
- Development/verification/investigation routing contract.
- JSON task contract and cross-system scenario with dependency checks.
- In-memory 3-system demo, ordered execution, assertions, evidence JSON.
- Python stdlib regression tests, CI, Feature Map and security boundaries.

## v0.2 — next
- Strict JSON Schema validation and richer contract fields.
- Read-only source/Code Map indexing per target repo.
- Real test adapters with auth, sanitized evidence and secure secrets integration.
- Cucumber/JUnit/Selenium/Playwright runner hooks.
- Status polling, correlation ID, idempotency, cleanup and data expiry.
- Controlled reviewer escalation, retry budget and distinct TEST_DEFECT classification.

## v0.3 — future
- Copilot CLI workflow orchestration integration (depending on supported stable APIs).
- Separate development and verification workspaces with independent check stages.
- GitHub issue/PR event-driven startup with permissions review.
- SLOs and eval suite: reproducible success %, blocked cause precision, manual intervention.
- Staging release approval, release evidence and rollbacks; production gated by organization rules.

Every milestone must add real failing/passing tests before claiming completion.
