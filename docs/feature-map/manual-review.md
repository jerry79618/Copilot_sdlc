# Feature Map — Manual Review (synthetic example)

## Sub-features
- Create a review case.
- Submit an application that needs manual review.
- Observe a downstream status synchronization.

## How to get to it (user POV)
This repository has **no UI**. In a future integrated application, document the real navigation here after confirming it in the running system. In v0.1 use the scenario ID `REVIEW-001`.

## Driving it (runtime)
- Contract: `contracts/examples/verification.json`
- Scenario: `scenarios/manual-review.json`
- Approved synthetic fixture: `fixtures/manual-review.json`
- Run: `python -m sdlc.cli verify --task contracts/examples/verification.json`
- Evidence appears in `artifacts/`. Pass means **local simulation only**.

## Gotchas
- Risk fixture must exist before application submission.
- Application must be pending before sync; the scenario dependency DAG is enforced.
- A real external status sync may be asynchronous and will need a bounded polling adapter.
- Do not confuse a sandbox mock PASS with production or staging E2E.
- Never directly write a real banking datastore for fixture creation.

## Multi-surface / cross-system journey
`risk_data -> submit -> sync_event`, with assertions on each of the three systems.

## SDLC Cucumber Binding

Machine-readable links for the runnable BDD scenario. The original four sections remain behavioral documentation.

```json
{
  "feature_id": "manual-review",
  "scenario_id": "REVIEW-001",
  "gherkin": "cucumber/src/test/resources/features/manual-review.feature",
  "scenario": "scenarios/manual-review.json",
  "contract": "contracts/examples/verification.json",
  "fixture": "fixtures/manual-review.json",
  "adapter": "demo",
  "systems": [
    "risk",
    "application",
    "sync"
  ]
}
```
