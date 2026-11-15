---
name: verification
description: Verify observed application behavior using Feature Maps, Cucumber, scenarios and honest evidence.
---

Read the relevant Feature Map, business rules and scenarios; generate or reuse Cucumber tests when useful. During verification intent, the Tester may add/refactor **test code** and synthetic fixtures unless `allow_test_changes: false`; product logic remains off-limits. Run the relevant Java/Cucumber checks, review actual expected/observed states, and record report paths.

Use `python -m sdlc.feature_map validate` for a bound Feature Map and `mvn -B -ntp -f cucumber/pom.xml test` for this demo. Convert actual Cucumber JSON via `python -m sdlc.cucumber_evidence --task TASK.json --feature FEATURE`. No approved external adapter means BLOCKED. A demo PASS never proves bank production integration.
