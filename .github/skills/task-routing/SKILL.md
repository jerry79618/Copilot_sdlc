---
name: task-routing
description: >
  Route new feature, bug fix, test-only and investigation requests into the correct SDLC workflow and Task Contract.
---


This is a subordinate Skill. Use the **sdlc-mode** Skill as the entry point; the selected Playbook decides when to use task-routing.

## Flow
1. Extract goal, intent, risk, system scope, environment, acceptance criteria and permissions.
2. Prefer explicit user intent. Ambiguous requests: inspect artifacts and ask one consolidated decision question only if necessary.
3. Represent an approved task using the JSON fields in `contracts/examples/`; do not silently upgrade verification to development.
4. Run `python -m sdlc.cli validate --task PATH` and `python -m sdlc.cli plan --task PATH`.
5. Development must enter verification before PR. Verification-only ends at evidence report, not a product code patch.
6. High-risk work needs explicit approval and non-demo external adapters remain blocked.
