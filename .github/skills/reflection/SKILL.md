---
name: reflection
description: >
  Reflect on a verified or blocked SDLC run; prevent repeated mistakes with
  enforceable checks instead of only longer prompts. Use for recurring
  corrections, stale Feature Maps and test failures after investigation.
---

# Reflect / Correct

1. Read actual run status and proof, not just an Agent-written summary.
2. Generate draft: python -m sdlc.reflect --run path/to/worklist.json
3. List observed failure classes and where each one came from.
4. Prefer architecture/schema -> types -> CI/lint -> regression tests ->
   Agent prompt/docs, in that order where feasible.
5. Add failing eval cases when the wrong Skill/Playbook was selected.
6. Re-run deterministic and application tests before promoting the change.
7. Peer review is required for rules, code, quality gates and bank policy edits.
8. Update Feature Map Gotchas only after observing real behavior.
9. Never automatically weaken assertions, grant permissions or deploy.
