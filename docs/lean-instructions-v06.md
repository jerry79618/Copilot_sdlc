# v0.6 — Lean Instructions, Bank-Safe Autonomy

## What changed

The **core instructions** are now intentionally short:
- `AGENTS.md` contains **project identity, business invariants, autonomy and reporting**.
- `.github/copilot-instructions.md` contains only repository orientation.
- `.github/agents/*.agent.md` describes each role and model choices, rather than copying a defensive checklist.
- `.github/skills/sdlc-mode/SKILL.md` is the entry point for Playbooks and the risk-aware execution policy.

This does **not** remove mandatory bank access controls. High-risk review, release authorization, sensitive-data protection, application tests, Cucumber evidence and missing real-system adapters remain relevant. Prompt instructions alone cannot enforce access policy; GitHub rulesets, CI, environments and bank approvals still need deployment configuration.

## Actual code-enforced rules

| Effective risk | Worklist intensity | Stages requiring attached evidence |
| --- | --- | --- |
| Low | Lean | G4 only (when present) |
| Medium | Standard | G2, G4 and G5 (when present) |
| High | Regulated | Every mandatory stage; manual approval is required separately |

Ordered stages still exist; the difference is **whether an extra proof file is required**. A stage without an evidence requirement is a progress record. The current G4 validator requires an actual matching PASS from the *demo* runner and **rejects staging or real bank E2E claims**. G4 is never optional just because a task is low-risk.

Risk flags for money movement, ledger consistency, authorization, customer PII or financial cross-system work override any low-risk declaration.

## Tester autonomy

Verification-only work can create, update, or refactor **test-scoped** Gherkin files, Java Step Definitions and synthetic fixtures without a separate development Task Contract. Set `allow_test_changes: false` to explicitly disallow such edits. The `allow_code_changes: false` restriction still protects product implementation and the investigation track remains read-only.

## Model fallback with guardrails

The normal Orchestrator, Developer, Tester and Reviewer include an ordered `models` list, with `modelPolicy: required` so only authored candidates are possible. Banking analyst, high-risk developer and cross-reviewer remain pinned to a single specialist model.

The configured candidates are NOT confirmed bank entitlements. `config/banking-model-policy.json` explicitly sets `org_approval_verified: false`. Administrators must confirm their model allowlists, provider contracts, data-handling terms and availability before using these choices on internal material. If no permitted candidate is available, do not silently choose an unlisted model. GitHub CLI policy reference: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference

## Routine usage

    python -m sdlc.mode route --goal "Verify review status in the demo system"
    python -m sdlc.model_policy check
    python -m sdlc.mode start --task contracts/examples/verification-low-risk.json

Use the worklist path returned by `start`. An un-gated lean stage may complete with:

    python -m sdlc.mode advance --run RUN.json --stage scope --outcome PASS

The `runtime-verify` G4 stage still needs **real JSON output** from the appropriate approved test runner:

    python -m sdlc.cli verify --task contracts/examples/verification-low-risk.json
    python -m sdlc.mode advance --run RUN.json --stage runtime-verify --outcome PASS --evidence PROOF.json

Only claim what the runner actually observed. The real bank integration adapter remains unimplemented.

## Evaluation before making further prompt rules

Instead of automatically adding more instructions, collect repeated mistakes, add failing regression/eval cases and check whether a short change actually improves behavior. We have **not** proven any specific percent reduction in tokens, elapsed time or AI Credits; run authenticated A/B trials to measure those.
