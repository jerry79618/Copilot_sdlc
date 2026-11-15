---
name: sdlc-mode
description: >
  Primary front door for any substantive engineering request in this repository.
  Use when the user says sdlc mode, wants a new feature, bug fix, test,
  code investigation, refactor, performance work, PR review or an unclear
  multi-phase software task. Select a playbook, follow its stage worklist
  and activate other SDLC skills only when their stages need them.
---

# SDLC Mode — goal-first entry point (inspired by /poteto-mode)

**This is a native Copilot Agent Skill, not a registered Copilot CLI slash command.**
For reliable entry, explicitly select the \`orchestrator\` custom agent with
\`copilot --agent orchestrator --prompt "..."\` or pick it using \`/agent\`.

## Principles (mandatory)
1. Restate the user's **goal, done check, proof and constraints** in one compact brief.
2. Determine development, verification, investigation or a conservative plan-only fallback.
3. **Decide how to prove it before implementing**. Do not conflate sandbox and real E2E.
4. Protect permissions: read-only investigation/test must never modify product code;
   irreversible actions, customer data, prod deployment and merges require authorization.
5. Follow the selected Playbook **in order**, preserving skipped/blocked steps with reasons.
6. Invoke focused Skills only as their steps fire, avoid all-Skills-in-one-context.
7. Distinguish FAIL (observable mismatch), BLOCKED (missing input/system), ERROR (invalid execution).
8. Keep the worklist updated with actual artifacts and always report unresolved steps.
9. No invented evidence: G4 needs valid verification output; CI / reviewer / releases are separate.

## Workflow for a new task

1. Read \`AGENTS.md\`, \`docs/sdlc-mode.md\` and this Skill.
2. Route the user's goal:
   \`python -m sdlc.mode route --goal "USER GOAL"\`
   The route is only a **heuristic suggestion**, not an AI decision with guaranteed correctness.
   You can override it based on inspected evidence, but explain why.
3. Check existing code/Feature Map/issue and draft or reuse Task Contract from \`contracts/examples/\`.
   Require explicit \`allow_code_changes\` and environment. If ambiguous, do a
   **read-only investigation or plan** instead of guessing consent.
4. Start the selected playbook:
   \`python -m sdlc.mode start --task PATH\`
   or use \`--playbook bug-fix\` when explicitly justified and compatible with intent.
5. The command prints the worklist path and next stage. Read the stage's \`skills\` field and
   use that Skill's \`SKILL.md\` for this stage. This is the **skill selection rule**.
6. For each stage create a concrete evidence artifact. Update:
   \`python -m sdlc.mode advance --run RUN.json --stage STEP --outcome PASS --evidence FILE\`.
   Use \`BLOCKED --reason "..."\` if a prerequisite is missing.
   Skip only when stage is optional, always give a reason; never hide skips.
7. For G4 runtime stage, run real tools. Demo proof:
   \`python -m sdlc.cli verify --task PATH\`; use its JSON evidence as \`--evidence\`.
8. Use \`python -m sdlc.mode status --run RUN.json\` and keep working until
   READY_FOR_REVIEW or COMPLETE, or safely blocked. No silent phase skipping.
9. When the intent changes, start a **new Task Contract**; do not silently turn
   a testing-only failure into code changes.
10. Report selected Playbook, Skills used, worklist status, proof, skipped/blocked,
    reviewer findings and next authorized owner.

## Routing
Read \`playbooks/catalog.json\` or run \`python -m sdlc.mode catalog\`.
- feature → development → tests → PR review
- bug-fix → reproduce → root cause → regression → verify → review
- verification → feature-map → cross-system data → readiness → execute → report
- investigation → read-only explore → evidence → report
- refactor / performance → before-and-after evidence
- review → independent read-only review
- figure-it-out → plan only, no unauthorized changes

**Important:** This worklist ledger does not call GitHub Copilot automatically;
Copilot/Orchestrator executes the Skills, while the Python mode checks ordering.
For multi-system tests, never claim full integration proof from a mock adapter.

## Cucumber-backed Verification
The scenario and runtime verification stages may load cucumber-authoring Skill to translate a linked Feature Map into runnable Gherkin, Java Step Definitions, JSON/HTML reports and G4 evidence. Validate binding first; do not claim success without actual Cucumber execution.

## Banking risk-aware model routing
Before delegating, run `python -m sdlc.model_policy route --task TASK.json` and inspect `effective_risk`, escalations from `impact_flags`, required reviewers and human approvals. The proposed model roster is in `config/banking-model-policy.json`. Never downgrade risk or substitute models. If the bank's Copilot organization disallows a required model, report BLOCKED. For high risk, use banking-analyst before code, developer-high for implementation, tester for Cucumber, banking-reviewer AND cross-reviewer for independent reviews, plus human release approval. A worklist PASS does not prove these agents actually ran. Run `python -m sdlc.credit_estimate --scenario all` for planning only.

## Pstack-inspired workflow improvements (v0.5)
- The first step is to follow docs/principles.md and identify the user goal, rather than guessing what implementation is needed.
- Route to one of 11 Playbooks, including prototype, skill-eval, multi-phase. Stages map to focused Skills; only load what is needed when the stage starts.
- Read or draft user-facing Feature Map through feature-map-discovery. Drafts are NOT business validation. Use approved Cucumber or app harness to turn observations into evidence.
- Keep an ordered worklist using python -m sdlc.mode checkpoint --run RUN for pause/resume. BLOCKED captures the specific missing owner/tool/data, not a fake PASS.
- Before claiming success, run real verification and independent review. Reflect via sdlc.reflect and test routing regressions with sdlc.quality_eval; a deterministic eval is not an LLM eval.
- Never claim Cursor /poteto-mode, Swarm, Arena, autonomous GitHub merge, or dynamically chosen models are natively implemented here.
