# Copilot repository context

This repository is the **orchestration framework**, not an existing Java/React application. Do not invent external integration endpoints. Use `AGENTS.md` for cross-agent policy.

- Primary entry for substantial engineering requests: `sdlc-mode` Skill + `orchestrator` agent. Its `playbooks/catalog.json` maps task goals to stages and Skills; `python -m sdlc.mode` manages ordered worklist evidence. Do not assume `/poteto-mode` exists in Copilot CLI.
- Task input: `contracts/examples/*.json` / Task Contracts described in `docs/architecture.md`.
- Intent: `development`, `verification`, `investigation`; route using `sdlc/workflow.py`.
- Feature Map: `docs/feature-map/`. Scenario dependencies: `scenarios/`. Sandbox data: `fixtures/`.
- Verification engine: `sdlc/verification.py`; it is intentionally in-memory, with no network calls.
- If test needs external prerequisites, show BLOCKED with exact missing adapter/data; do not guess or fake a PASS.
- Tests: `python -m unittest discover -s tests -v`. Full quickstart: `README.md`.
- No approval bypass, no autonomous production deployment, no secret copying.
- Run deterministic checks prior to claiming done; differentiate static review and executed tests.

- Banking routing: `python -m sdlc.model_policy route --task TASK.json`. `config/banking-model-policy.json` is the model plan; bank organization allowlists and approvals must be enforced separately. Agents use `modelPolicy: required`; do not silently replace a blocked model. Sensitive changes require independent double review and authorized human sign-off. Never send real customer PII, production account data, or credentials to models.

- Goal-first workflow v0.5: `docs/principles.md` → `sdlc-mode` Skill → chosen Playbook's stage skills → Feature Map / Cucumber evidence → independent review → optional reflection and static Skill eval. Use `python -m sdlc.discovery inspect|health`, `python -m sdlc.quality_eval` and `python -m sdlc.mode checkpoint`. Do not mistake static source discovery for actual behavior.
