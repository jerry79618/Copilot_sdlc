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

If a Feature Map has a Cucumber Binding, use cucumber-authoring Skill. Run python -m sdlc.feature_map validate, then mvn -B -ntp -f cucumber/pom.xml test and python -m sdlc.cucumber_evidence --task contracts/examples/verification.json --feature manual-review. Feed the resulting evidence to worklist G4; demo PASS is sandbox-only.

## Map discovery and maintenance
If needed use feature-map-discovery Skill first. Run python -m sdlc.discovery health and inspect / draft candidates for an unknown feature. Verify actual behavior with Cucumber or an approved harness before trusting the map. Do not treat Java annotations or Skill eval cases as banking end-to-end proof.
