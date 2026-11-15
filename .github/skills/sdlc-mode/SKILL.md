---
name: sdlc-mode
description: >
  Goal-first entry for feature development, bug fixes, verification,
  investigation, refactoring, review, prototype and multi-phase work.
  Choose a relevant Playbook, delegate situational Skills and verify results.
---

# SDLC Mode

1. Start with the **user's goal, done condition and authorization**. Gather enough repository context to choose a sensible approach. Routine design choices are yours to make; reserve questions for financial rules, privileged changes, irreversible operations or genuinely competing product directions.
2. Choose a Playbook using `python -m sdlc.mode route --goal "GOAL"`, then create or reuse a Task Contract (the agent may assemble routine fields). Check risk via `python -m sdlc.model_policy route --task TASK.json`. Risk flags can increase the level; no unapproved banking model may be invoked.
3. Start `python -m sdlc.mode start --task TASK.json`. Follow the stage order, loading **only the mapped Skill when needed**. Use `python -m sdlc.mode checkpoint --run RUN.json` to resume a stopped task.
4. **Lean low-risk:** ordinary stages can be completed without generating a separate evidence file. **Medium:** evidence for baseline, runtime verification and independent review. **High:** preserve full evidence and approved specialist/human review. All tiers must provide real G4 execution evidence for a Playbook that contains G4. `advance --outcome PASS --stage STEP --run RUN.json [--evidence FILE]`.
5. Inspect Feature Map when behavior or integration is relevant; draft a map when missing, then verify actual behavior. Cucumber Tester can maintain test-scoped Gherkin/Java Steps under a verification task (unless explicitly disabled), without changing product code.
6. FAIL calls for diagnosis; BLOCKED means state the missing prerequisite and owner. Never pass simulated bank E2E as real. Do not treat a worklist as a running Agent orchestrator or bypass GitHub protection rules.
7. Finish with actual changes, checks and findings, **decisions made and significant alternatives rejected**, plus any remaining approval or test coverage gaps.

The Worklist engine does not spawn agents. Copilot must actually invoke delegated agents and tests. `/poteto-mode` is a Cursor skill, not a built-in Copilot CLI slash command.
