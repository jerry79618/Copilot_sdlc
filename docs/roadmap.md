# SDLC delivery roadmap

## v0.1 — merged
Task contracts, development/testing/investigation routes, Feature Map,
synthetic multi-system workflow, evidence runner, Copilot agents and Skills,
basic CI.

## v0.2 — SDLC Mode entry point
- [x] Goal-first route suggestion, no forced long prompt.
- [x] Eight declared Playbooks with ordered stages, mapped Skills and gates.
- [x] Persistent worklist with PASS/BLOCKED/optional SKIP and evidence paths.
- [x] Separate development/testing/read-only pathways.
- [x] G4 prevents non-demo or mismatched-task verification from claiming success.
- [x] Copilot \`orchestrator\` reads new Skill and runbook.
- [x] Routing evals and invalid-transition tests.
- [ ] Run authenticated Copilot CLI end-to-end session in a real operator environment.

## v0.3 — real adapters and enterprise protection (not built)
- Integrate verified Cucumber, Selenium, JUnit and Java build adapters.
- Test-only authenticated APIs/MCP for cross-system data provision/readiness.
- Correlation IDs, asynchronous event polling, safe cleanup, retries and owner alerts.
- Enforce evidence signing/provenance and protected CI / branch rulesets.
- Verify Copilot agent task selection and delegated Skill execution in authenticated sessions.

## Later
Dynamic long-running orchestration where supported, artifact governance,
Agent Evals, PR and release approvals, rollback and monitoring integrations.
**Never label a mock PASS as real bank system E2E.**
