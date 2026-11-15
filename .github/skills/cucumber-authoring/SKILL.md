---
name: cucumber-authoring
description: >
  Read repository Feature Maps and author executable Cucumber JVM Gherkin
  and Java step definitions. Use for BDD testing, regression, special test data,
  cross-system workflows, Cucumber reports and evidence-driven validation.
---

# Feature Map → Cucumber → SDLC Verification

1. Discover the target Feature Map: Sub-features, How to get to it, Driving it, Gotchas.
   Check its binding with python -m sdlc.feature_map validate --feature manual-review.
2. Read linked Scenario Catalog and Task Contract. Treat the Feature Map as a
   behavior/operation guide, not a guarantee of correct banking rules.
3. Plan positive, negative, boundary, state transition and cross-system cases.
   Unknown business rules must be clarified, never invented.
4. Search existing Cucumber .feature and Java step definitions before creating
   new ones; reuse stable steps and test adapters.
5. Write Gherkin in cucumber/src/test/resources/features/ with a
   @feature_<feature-id> tag (hyphens become underscores). Steps express
   observable business behavior, not Java implementation details.
6. Write actual io.cucumber.java.en Java steps in cucumber/src/test/java/.
   Use test-scoped state and approved synthetic fixtures. With external systems,
   use cross-system-data Skill: data ownership, order, readiness, correlation IDs,
   bounded polling, cleanup. Without an approved adapter, report BLOCKED.
7. Run Maven Cucumber; do not invent PASS. Generate JSON/HTML test reports.
8. Translate real JSON to evidence with python -m sdlc.cucumber_evidence
   --task contracts/examples/verification.json --feature manual-review.
9. Feed the generated artifacts/cucumber-evidence.json to the SDLC G4 stage.
   A demo adapter's PASS is not real multi-system E2E.
10. Keep verification-only tasks from changing application code. Fixing an
    application defect requires a separately authorized development task.
