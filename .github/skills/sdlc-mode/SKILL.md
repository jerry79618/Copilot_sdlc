---
name: sdlc-mode
description: >
  Explicit SDLC mode for goal-first Java development, testing and investigation.
  Follow the real central Playbook catalog, not a user-supplied step-by-step recipe.
---

# SDLC Mode (v0.7 cross-project)

1. From the **target project root**, first execute `python -m sdlc.entrypoint doctor --project-root .`. If the engine is missing or a user-level Agent/Skill shadows the framework, stop and report the blocker. Launch with `scripts/start-sdlc.ps1 -ProjectRoot TARGET` to supply the framework path and per-session Agent/Skill scope.
2. Execute `python -m sdlc.entrypoint route --project-root . --goal "USER GOAL"`. This returns the actual catalog path, chosen Playbook and ordered stage-to-Skill bindings. Do not guess the Playbook from a prompt or memory.
3. Inspect only the Skill file(s) referenced by the **current** Playbook stage. Treat other globally available personal Skills as unrelated unless the actual task requires them. Skills are instructions, not automatic evidence of delegation.
4. For an authorized task, create or reuse its Task Contract and check `python -m sdlc.model_policy route --task TASK.json` before dispatch. Execute `python -m sdlc.mode start --task TASK.json` to record progress. This engine cannot launch Copilot subagents for you.
5. Preserve the original user goal and scope; choose routine implementation steps yourself. A test-only task may edit scoped Gherkin, Java Steps or synthetic fixtures unless disabled, never product logic.
6. Preserve G4 actual verification evidence when its Playbook requires runtime verification. Low risk requires G4, medium G2/G4/G5, and high risk all mandatory evidence and human approval. Missing approved real bank adapter means BLOCKED rather than a forged PASS.
7. Finish with actual edits, actual test results, independent review outcomes, decisions and significant alternatives. Do not merge/deploy without authorization.

Copilot CLI requires a real authenticated session and tool permissions. No Cursor plugin or `/poteto-mode` slash command is required.
