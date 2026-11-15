# SDLC Principles — enterprise interpretation of verification-first workflows

These are project principles, not a verbatim copy of pstack.

1. Begin with the user's goal, done check, proof and authority, not tool lists.
2. Discover code, Feature Map, scenarios and existing tests before editing.
3. Model data, state changes, identity, money, authorization and retries explicitly.
4. Design the verification before changing behavior; test what users can observe.
5. Select Playbook first, load situational Skills only as its stages need them.
6. Split design / implementation / independent checks across focused agents.
7. Make small reversible changes; require approval for irreversible bank actions.
8. Report real observed evidence; never call sandbox PASS a bank system PASS.
9. Encode lessons in architecture, schema, CI and regression tests, not only prose.
10. Guard sensitive data, secrets, external writes, audit trail and model allowlists.

High-risk tasks always retain two independent reviewers plus human release
approval. A worklist stage DONE is a recorded claim, not an authenticated proof
of model execution. Real systems require approved adapters and runtime evidence.
