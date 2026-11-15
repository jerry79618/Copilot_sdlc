# Playbooks — the ordered worklists used by SDLC Mode

The machine-readable single source of truth is [catalog.json](catalog.json).
Each playbook has a route, intent, ordered stages, Skills to load at that stage
and mandatory G1–G5 evidence gates (where relevant). The playbook is NOT a
separate GitHub Copilot Slash Command.

| Route | Intent | Purpose |
| --- | --- | --- |
| feature | development | implement a new capability and verify it |
| bug-fix | development | reproduce → diagnose → repair → regression |
| verification | verification | existing behavior, including cross-system test data |
| investigation | investigation | read-only analysis and evidence |
| refactor | development | change structure without behavior drift |
| performance | development | compare measured baseline against after |
| review | investigation | read-only independent code review |
| figure-it-out | investigation | ambiguous task → safe multi-phase plan |

\`sdlc.mode\` translates the catalog into a persistent worklist. It does not
actually spawn LLM subagents; that is the job of the CLI's orchestrator agent
and the related Skills. Record completion accurately; only gates required by the effective risk tier need separate evidence artifacts. A G4 execution stage always needs real verification evidence. Optional stages may be SKIPPED with a written reason.

G1: scope and acceptance criteria.
G2: verifiability and baseline.
G3: authorized data/environment readiness.
G4: actual runtime behavior evidence (sandbox-only in v0.2).
G5: review and quality assessment. Production release still requires external
branch protection, environment approvals and CI.

## Additional pstack-inspired routes in v0.5
- prototype (development): compare two disposable approaches with actual evidence; promote only after approval.
- skill-eval (investigation): predefine cases, run routing eval, then validate real Copilot behavior separately.
- multi-phase (investigation): plan independently verifiable, reviewable slices and dependencies without changing product code.
- All normal development/testing Playbooks now offer optional reflection after evidence. Review task and cross-system risk before any release.

## v0.6 evidence policy
The canonical evidence rules are under `config/banking-model-policy.json`: low G4, medium G2/G4/G5, high G1–G5 plus evidence for all mandatory stages. Skipped optional stages need a reason; unrequired attachments may be omitted. The tool cannot grant model/provider approvals or human release signoff.
