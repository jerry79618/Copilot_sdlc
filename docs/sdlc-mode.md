# Legacy SDLC Mode v0.2 — historical

This is an older design document. New users should follow [Poteto Mode](poteto-mode.md) and `.github/skills/poteto-mode/SKILL.md`. Internal `python -m sdlc.mode` is still supported.

Independent orchestration inspired by Lauren Tan's **goal → playbook → task list →
situational Skills → real verification** design. This is NOT pstack or the
Cursor \`/poteto-mode\` plugin, and it does not claim API or slash-command compatibility.

## End-to-end map

\`\`\`mermaid
flowchart TD
  P["Short task goal"] --> O["Copilot CLI orchestrator + sdlc-mode Skill"]
  O --> C["Read rules, clarify intent, inspect relevant Feature Map"]
  C --> R["sdlc.mode route: suggest Playbook"]
  R --> T["Task Contract: intent, acceptance, proof, permissions"]
  T --> W["sdlc.mode start: persistent ordered worklist"]
  W --> D{"Selected Playbook"}
  D -->|"feature / bug-fix / refactor / performance"| DEV["Development: explore → proof plan → implement → unit"]
  D -->|"verification"| TEST["Testing: feature → scenarios → cross-system data → readiness"]
  D -->|"investigation / review / figure-it-out"| RO["Read-only: inspect → report / plan"]
  DEV --> TEST
  TEST --> V["Verification Skill + runner + actual evidence"]
  V --> G{"Gates + classification"}
  G -->|"PASS"| CR["Independent review / CI / PR handoff"]
  G -->|"FAIL"| F["Failure analysis, authorize fix if allowed"]
  G -->|"BLOCKED"| B["Record missing data / adapter / permissions"]
  F --> DEV
  RO --> END["Investigation output"]
  CR --> E["Release approval outside mode"]
  E --> L["Regression / eval / feature-map lessons"]
  L -.-> C
\`\`\`

## Official Copilot CLI invocation

Within the repository:

\`\`\`bash
copilot --agent orchestrator --prompt "新增訂單查詢 API；完成代表單元與整合測試通過，保留證據，請勿部署。"
\`\`\`

Alternatively run interactive \`copilot\` and select \`/agent\` → \`orchestrator\`,
then state only your **goal + done check + proof + constraints**. The agent loads
\`.github/skills/sdlc-mode/SKILL.md\`.

**Current behavior:** `/poteto-mode` refers to a discoverable Copilot Agent Skill in a prompt, not to Cursor's plugin slash-command implementation. The older `sdlc-mode` is a legacy alias.

## Deterministic commands (stdlib Python 3.11+)

\`\`\`bash
# Suggest a Playbook without changing any files:
python -m sdlc.mode route --goal "測試跨系統人工覆核"
# Show Playbook definitions:
python -m sdlc.mode catalog
# Start actual ordered worklist from approved Task Contract:
python -m sdlc.mode start --task contracts/examples/verification.json
# Save returned path as RUN (artifacts/worklist-TASK-VERIFY-001-...json)
python -m sdlc.mode status --run "$RUN"
# Mark first stage PASS, with a real reviewable file:
python -m sdlc.mode advance --run "$RUN" --stage scope --outcome PASS --evidence contracts/examples/verification.json
# If a step cannot proceed, record the blocker (no fake PASS):
python -m sdlc.mode advance --run "$RUN" --stage feature-map --outcome BLOCKED --reason "Target feature is not documented"
# After resolving the blocker, use PASS on same stage to resume.
# Only optional stages support SKIP with a reason.
\`\`\`

For the runtime verification stage, produce real JSON evidence via
\`python -m sdlc.cli verify --task contracts/examples/verification.json\` and
supply its \`artifacts/TASK-VERIFY-001-...json\` path to \`advance\`.
G4 checks task ID, environment, PASS, and demo classification before allowing
progress. It will reject a staging/prod "PASS" in this version.

Other stage evidence files, when required by the risk tier, are logged but not cryptographically authenticated:
**a recorded "PASS" there is not an independent quality/security certification**.
Real CI checks and authorization outside this ledger remain necessary.

## Selection algorithm

- Copilot: reads your prompt, repo state and Task Contract. The selected
  Playbook is still a model judgment, so verify intent and permissions.
- \`sdlc.mode route\`: conservative multilingual keyword-based **suggestion**,
  supports explicit \`--intent\` or \`--playbook\`. Unknown goals route to
  read-only \`figure-it-out\`, asking for a scoped plan before implementation.
- \`sdlc.mode start\`: validates declared intent and refuses conflicting
  Playbook (e.g. bug-fix for testing-only contract).
- Each \`stages[].skills\` determines when to load the other Skills.
  It is a staged plan, not "import all Skills at once".

## Cross-system special data

Use Feature Map for the surface; Scenario Catalog for ordered dependencies.
When the Playbook reaches \`scenario\` / \`dependencies\`, load
\`cross-system-data\` only then. For A → B → C:
1. inspect authorized sandbox fixture/provision API for B;
2. verify data is in the required state and correlation IDs exist;
3. confirm A precondition, execute subject;
4. wait for C with bounded polling once a real adapter is implemented;
5. compare actual cross-system evidence;
6. CLEANUP with an approved, idempotent method.

In the current repository, \`DemoAdapter\` is **memory-only**; staging is BLOCKED.
This infrastructure cannot yet connect to real bank systems.

## Quality ownership

| Check | Who performs it |
| --- | --- |
| Task intent and Playbook selection | Orchestrator, task contract |
| Step/Skill selection and status | Playbook catalog + worklist engine |
| Product implementation / manual actions | Copilot CLI selected agents |
| Test run / local evidence | verification runner and adapters |
| CI hard gates | GitHub Actions and required status checks |
| Production merge/deploy | Authorized humans + GitHub environments |

Unknown or blocked failures do not authorize modifying the production code.
As each real integration is added, create eval cases proving the routing,
evidence integrity, and denied operations.

## v0.6 risk-based evidence and autonomy

The ordered Playbook remains the same but the `evidence_required` field now comes from the **effective risk tier** in `config/banking-model-policy.json`. Low-risk stages that aren't G4 can be advanced without separate evidence files; medium-risk G2/G4/G5 still require files; high-risk requires evidence for every mandatory stage. Any G4 must contain valid runtime verification proof. Passing a planning stage without a file records progress, not an independent proof of correctness.

Example for low-risk tasks only: `python -m sdlc.mode advance --run RUN.json --stage scope --outcome PASS`. For medium-risk `feature-map` G2, supply `--evidence path`. For high-risk tasks keep all stage artifacts and human sign-off; a worklist status never substitutes for bank approvals.

Verification tasks may edit **test-scoped** code unless `allow_test_changes: false` is in the Task Contract. Such work does not grant access to application source, customer data or production changes.
