# Copilot repository context

This repository is the **orchestration framework**, not an existing Java/React application. Do not invent external integration endpoints. Use `AGENTS.md` for cross-agent policy.

- Task input: `contracts/examples/*.json` / Task Contracts described in `docs/architecture.md`.
- Intent: `development`, `verification`, `investigation`; route using `sdlc/workflow.py`.
- Feature Map: `docs/feature-map/`. Scenario dependencies: `scenarios/`. Sandbox data: `fixtures/`.
- Verification engine: `sdlc/verification.py`; it is intentionally in-memory, with no network calls.
- If test needs external prerequisites, show BLOCKED with exact missing adapter/data; do not guess or fake a PASS.
- Tests: `python -m unittest discover -s tests -v`. Full quickstart: `README.md`.
- No approval bypass, no autonomous production deployment, no secret copying.
- Run deterministic checks prior to claiming done; differentiate static review and executed tests.
