# Cucumber JVM testing in Enterprise AI SDLC

## Model
Feature Map (behavioral knowledge) → Gherkin (acceptance behavior)
→ Java Step Definitions → approved test adapter → actual Cucumber run
→ JSON/HTML reports → Cucumber evidence converter → SDLC G4.

The original Lauren Tan-style Feature Map sections remain intact. Add
SDLC Cucumber Binding (JSON) as a link to executable tests, not a duplicate
business rule catalog.

## Quick start
    python -m sdlc.feature_map validate
    mvn -B -ntp -f cucumber/pom.xml test
    python -m sdlc.cucumber_evidence --task contracts/examples/verification.json --feature manual-review

Cucumber JSON and HTML are in cucumber/target/cucumber-report/.
Normalized evidence is artifacts/cucumber-evidence.json.

## Add a project Feature Map
1. Write docs/feature-map/<id>.md with Sub-features, How to get to it (user POV),
   Driving it (runtime), Gotchas and a SDLC Cucumber Binding JSON code block.
2. Link the Gherkin .feature, Scenario Catalog JSON, Task Contract and synthetic
   fixture. The parser validates those files and system scope.
3. Gherkin must contain @feature_<id_with_underscores> and runnable scenarios.
4. Implement Java step definitions, reuse existing steps and adapters.
5. Validate links, execute Maven tests, convert actual results and gate releases.

## Safety
The included DemoReviewSystems is memory-only. No Selenium browser is
configured and no real external API is accessed. For real integration, replace
the adapter behind a reviewed interface, constrain credentials to staging,
track correlation IDs, require readiness evidence, and implement safe cleanup.
Do not claim mock test PASS proves real banking integration. No automatic
release, database writes or application source modifications from test-only tasks.
