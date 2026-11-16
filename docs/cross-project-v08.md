# v0.8 cross-project setup (Poteto Mode)

Canonical entry: `scripts/start-poteto.ps1` and `.github/skills/poteto-mode/SKILL.md`. Legacy `start-sdlc.ps1` and `sdlc-mode` remain aliases; see [Poteto Mode](poteto-mode.md).

## Goal

Keep one centrally versioned SDLC engine and Playbook catalog. Java business
knowledge, test scenarios and Feature Maps stay with the target project.

~~~text
D:\git\Copilot_sdlc\       # shared framework
D:\git\bank-application\   # Java source, AGENTS.md, maps, scenarios
D:\git\bank-risk\          # another independent project
~~~

## Update and launch

~~~powershell
cd D:\git\Copilot_sdlc
git switch main
git pull --ff-only

.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -CheckOnly
.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -Isolated -Goal "幫我補齊查詢測試，不要修改產品程式碼"
~~~

The launcher runs read-only doctor and goal preparation before Copilot starts.
No project files are written during launch. Isolated uses a separate Copilot
home and may require a separate login. This is not a security sandbox.

## Inspect the real project and Playbooks

~~~powershell
# Run from Framework root, or ensure Framework is on PYTHONPATH
python -m sdlc.entrypoint doctor --project-root "D:\git\bank-application"
python -m sdlc.entrypoint prepare --project-root "D:\git\bank-application" --goal "修正查詢錯誤"
python -m sdlc.entrypoint route --project-root "D:\git\bank-application" --goal "修正查詢錯誤"
~~~

prepare returns DRAFT_NOT_EXECUTABLE. It does not fabricate acceptance criteria,
environment permissions, risk flags, scenario data or PASS results. A full Task
Contract is still required for a valid worklist and execution. Doctor lists
candidate Agent/Skill sources; actual runtime resolution still needs checking
inside Copilot CLI. Back up/update only conflicting SDLC copies. Other personal
Skills are not modified.

## Feature Map and scenario paths

- Framework contains the Python engine, Skills, Agents, Playbooks and demo.
- Target project contains docs/feature-map, AGENTS.md, src/main and src/test;
  it may also contain scenarios, contracts and fixtures if needed.
- Candidate map generation is explicitly requested and writes only into the
  target project's artifacts/discovery directory, without overwrite.
- Unbound maps have CANDIDATE_REVIEW_REQUIRED status. Strict bound maps support
  src/test resources/features and legacy cucumber paths; static links are not
  runtime evidence.

~~~powershell
python -m sdlc.discovery inspect --project-root "D:\git\bank-application"
python -m sdlc.discovery candidates --project-root "D:\git\bank-application"
python -m sdlc.discovery health --project-root "D:\git\bank-application"
python -m sdlc.feature_map validate --project-root "D:\git\bank-application"
~~~

The strict validation command requires complete links to Gherkin, scenario,
Task Contract and fixture. For drafts, inspect discovery health instead.

## Worklists for complete project-specific Task Contracts

~~~powershell
python -m sdlc.mode start --task "D:\git\bank-application\contracts\verification.json" --project-root "D:\git\bank-application"
python -m sdlc.cli validate --task "D:\git\bank-application\contracts\verification.json" --project-root "D:\git\bank-application"
~~~

External-project worklists default to the target project's artifacts/sdlc folder,
not Framework artifacts, unless an explicit output directory is provided.
These require an existing real Task Contract and a matching scenario file. The
generic draft from prepare is not a runnable Task Contract.

## Safeguards and limitations

The Python engine does not invoke AI subagents, connect to bank services, or
implement real Java integration test adapters. External project evidence
cannot be accepted as framework Demo G4 PASS. Do not treat static Feature Map
links or synthetic Cucumber demos as proof of staging/prod behavior.

Actual Agent/Skill CLI loading, enterprise model approval and a real
Cucumber/JUnit evidence adapter are future integration requirements.
