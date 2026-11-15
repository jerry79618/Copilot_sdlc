---
name: verification
description: >
  Verify application behavior using a Feature Map, scenario dependencies, observable assertions and evidence reports.
---


1. Find the relevant feature in `docs/feature-map/`.
2. Read scenario `scenarios/` and its Task Contract; check prerequisite step DAG.
3. Run `python -m sdlc.cli validate --task PATH`.
4. For the included *mock* scenario run `python -m sdlc.cli verify --task PATH`.
5. Inspect JSON evidence: environment, adapter limitations, steps, expected and observed checks.
6. PASS is valid only within the adapter's tested boundary. If external data/tool unavailable, BLOCKED.
7. Capture errors, report exactly what was NOT executed, and never change product code for test-only tasks.
