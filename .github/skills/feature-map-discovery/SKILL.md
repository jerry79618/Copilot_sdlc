---
name: feature-map-discovery
description: >
  Discover, draft and maintain user-facing Feature Maps for Java Spring
  and Cucumber projects. Use when a feature is undocumented, maps may have
  drifted after changes, or a Testing Playbook needs to find real behavior.
---

# Feature Map Discovery and Maintenance

1. Discover existing docs/feature-map and Gherkin before creating anything.
2. Inspect source endpoints and BDD tags using:
   python -m sdlc.discovery inspect --project-root .
3. Draft candidates using:
   python -m sdlc.discovery candidates --project-root .
   Output stays in the selected project's artifacts/discovery, never the central Framework.
   It never overwrites an existing candidate or verified map.
4. Static candidates are NOT verified. Require owner confirmation of business
   invariants, actual UI/API navigation, permissions and observed expected states.
5. Build/reuse an approved harness; invoke cucumber-authoring Skill to create
   Gherkin + Java Steps + executable test adapter and collect evidence.
6. Only promote a candidate into docs/feature-map after an observed test journey
   and acceptance-criteria review. The SDLC Cucumber Binding references real assets.
7. Check drift with python -m sdlc.discovery health --project-root .
   and validate fully bound maps with python -m sdlc.feature_map validate --project-root .
   Unbound maps are candidates requiring review, not verified runtime behavior.
8. Missing approved staging adapter means BLOCKED, not PASS. Never invent bank
   data, customer flows or live behavior from annotation discovery.

Independent adaptation of pstack's user-facing Feature Map concept; this
static scanner is NOT an app browser or runtime verification.
