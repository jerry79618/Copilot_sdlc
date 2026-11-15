# Repository rules for all AI agents

**Unified entry**: for new SDLC engineering requests use `.github/skills/sdlc-mode/SKILL.md` and `playbooks/catalog.json`; the `orchestrator` agent must select one playbook and record stage evidence using `python -m sdlc.mode`. Load sub-Skills only when the selected stage requires them. Unclear requests are read-only plans until scope and permissions are established.


1. **Verification before completion**: define observable acceptance criteria and required evidence before coding. Never claim external E2E success from `demo` evidence.
2. **Classify intent first**: development may modify product code; verification and investigation are read-only for product code. A failed test does not by itself authorize development work.
3. **Discover before changing**: read repository, feature map, business rules, task contract, tests, and relevant implementation.
4. **Context only as needed**: load relevant Feature Map entries; do not stuff all docs into a prompt.
5. **Safe data**: fixtures must be synthetic. Never write to production DB, trigger a real payment, change permissions, bypass GitHub rulesets, or deploy without explicit authorization.
6. **Structured evidence**: classify outcomes as PASS, FAIL, BLOCKED, or ERROR. Preserve observed/expected values, environment, run method and known limitations.
7. **Correct failure classification**: distinguish product bug, test script bug, fixture/data issue, integration outage, environmental issue and unknown. Do not patch production code for a blocked test.
8. **Scope discipline**: smallest valid change, independent reviewer when appropriate, all CI checks green, no speculative API/schema edits.
9. **No silent retries**: bounded retries, reproducible commands, clearly report unresolved prerequisites.
10. **Learning loop**: after verified defects, improve tests, Skills and feature map. Facts from code are hypotheses until confirmed where business rules matter.

To check a task: `python -m sdlc.cli validate --task <path>`.
To plan: `python -m sdlc.cli plan --task <path>`.
To verify the sandbox example: `python -m sdlc.cli verify --task contracts/examples/verification.json`.
