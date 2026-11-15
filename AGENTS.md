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

For Feature Maps with a Cucumber Binding, use .github/skills/cucumber-authoring/SKILL.md to build real Gherkin and Java Step Definitions, validate links, execute Maven and collect Cucumber evidence. Testing-only never authorizes modifying product code. Mock PASS is not real E2E.

## Bank-grade model and evidence controls
1. Resolve effective risk using `python -m sdlc.model_policy route --task TASK.json`; impact flags may escalate risk.
2. The model list is a proposal pending bank approvals, not proof of approved providers. Required model locks prevent silent fallback, not bank policy enforcement.
3. Financial transactions, ledger, privacy, authorization and cross-system money movement require specialist analysis, independent two-model review, and signed human approvals before release.
4. Never expose passwords, production secrets, raw customer data or unredacted transactions to model prompts, tools or evidence.
5. Use the cost estimator as a scenario model, not actual GitHub charges; monitor `/usage` and admin billing to calibrate.

## Goal-first pstack-inspired SDLC v0.5
- Read `docs/principles.md` before selecting Playbook. Confirm business goal, accepted results and required observable proof.
- Choose one of 11 Playbooks; use each stage's `skills` for situational loading, not every Skill on every turn.
- Before new testing/code changes, check `python -m sdlc.discovery health`; missing Feature Maps can be drafted with `sdlc.discovery candidates`, but a static draft cannot be treated as runtime verified.
- Build/reuse Cucumber steps from approved Feature Map and signed-off business conditions; never invent banking acceptance criteria.
- For recurring errors use `python -m sdlc.quality_eval` and `sdlc.reflect` to recommend enforceable changes. Require peer review for all rule/skill updates.
- Worklist checkpoints are records. No command here spawns autonomous subagents, auto-merges PRs or certifies unapproved models.
