---
name: sdlc-mode
description: >
  Explicit SDLC mode for goal-first Java development, testing and investigation.
  Follow the real central Playbook catalog, not a user-supplied step-by-step recipe.
---

# SDLC Mode (v0.8 cross-project)

1. From the **target project root**, first execute `python -m sdlc.entrypoint doctor --project-root .`. If the engine is missing or a user-level Agent/Skill shadows the framework, stop and report the blocker. Launch with `scripts/start-sdlc.ps1 -ProjectRoot TARGET` to supply the framework path and per-session Agent/Skill scope.
2. Execute `python -m sdlc.entrypoint prepare --project-root . --goal "USER GOAL"` for the read-only draft Task Context, then `python -m sdlc.entrypoint route --project-root . --goal "USER GOAL"` for actual catalog stages and Skill paths. Neither command authorizes edits.
3. If the route also returns `pstack_reference`, use the mapped upstream source under `vendor/pstack/` only as read-only engineering guidance; do not execute Cursor slash commands, implicit model changes, merges or deployment. The official local stages, selected bank risk tier and evidence gates take priority.
4. Inspect only the Skill file(s) referenced by the **current** Playbook stage. Treat other globally available personal Skills as unrelated unless the actual task requires them. Skills are instructions, not automatic evidence of delegation.
5. Keep Java project paths separate from Framework demo sources. For an authorized task, incrementally establish acceptance criteria, risk, environment, scenarios and a validated Task Contract. Then check model policy and use `python -m sdlc.mode start --task TASK.json --project-root .` to record progress. Do not require a scenario file just to begin understanding a goal; this engine cannot launch Copilot subagents.
6. Preserve the original user goal and scope; choose routine implementation steps yourself. A test-only task may edit scoped Gherkin, Java Steps or synthetic fixtures unless disabled, never product logic.
7. Preserve G4 actual verification evidence when its Playbook requires runtime verification. Low risk requires G4, medium G2/G4/G5, and high risk all mandatory evidence and human approval. Missing approved real bank adapter means BLOCKED rather than a forged PASS.
8. Finish with actual edits, actual test results, independent review outcomes, decisions and significant alternatives. Do not merge/deploy without authorization.

Copilot CLI requires a real authenticated session and tool permissions. No Cursor plugin or `/poteto-mode` slash command is required.
