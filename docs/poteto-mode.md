# Poteto Mode — Lauren Tan engineering philosophy on Copilot CLI

The **active Copilot session main agent** receives the user's goal, selects the
appropriate Playbook, owns the work and the verifier's verdict, and reports evidence.
It does **not** routinely spawn or require a dedicated `orchestrator` Agent.
The original `Orchestrate` Playbook is reserved for genuine standing,
long-running, multi-PR programs.

The canonical skill is `.github/skills/poteto-mode/SKILL.md`.
The original pstack source is MIT-licensed, pinned under `vendor/pstack/`.
The 100-file snapshot includes all **23 original Playbooks** and **58
leaf Skill definitions**, plus core references. It does not include all
external Cursor scripts/automations or provide identical Cursor behavior.

## The six engineering capabilities

| Capability | Original pstack techniques | Copilot integration |
| --- | --- | --- |
| Understand | `how`, `why`, recall, repo history | Inspect code, project Feature Maps, tests and Git evidence |
| Design | principles, `architect`, `interrogate`, `arena` | Simplify data model, test alternatives, consult independent reviews where available |
| Execute | selected Playbook, TDD, optional `swarm` | Main agent works directly or delegates scoped work with real available subagents |
| Verify | verification Skill, Feature Map, runtime drive, evidence | Approved project Cucumber/JUnit/HTTP/DB test adapters; no synthetic bank PASS |
| Learn | `reflect`, `correct`, Evals, decision trail | Turn recurring failure into code constraints, tests, CI or proven Skill refinements |
| Deliver | review, CI, PR evidence, concise report | Verify actual diff/checks; protected merges and deployment stay human-authorized |

## Architecture

```text
User goal
  -> Copilot main Agent activates Poteto Mode
      -> inspect real project -> choose local policy Playbook
      -> recommend original pstack Playbook (23 selectable)
      -> main agent owns design, implementation review and actual evidence
          -> simple task: main agent executes directly
          -> independent tasks: delegate when host supports it
          -> long multi-PR program: Orchestrate, optional coordinator
      -> verify real behavior, independently review, reflect/evaluate
      -> report actual results and blockers
```

The Python selector does **not** spawn Agents, subscribe to CI or run tests.
It makes recommendations; the main AI agent may change the chosen original
Playbook after inspecting the repository, documenting the reason.
The current eleven SDLC Playbooks remain the **regulated safety skeleton**.

## Launch from Windows PowerShell

```powershell
cd D:\git\Copilot_sdlc
git switch main
git pull --ff-only

# Read-only preflight
.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -CheckOnly

# Default: main agent owns workflow, no forced --agent=orchestrator
.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -Isolated -Goal "幫我修正申請狀態查詢錯誤"

# Optional legacy coordinator for specifically authorized long programs:
.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -Isolated -UseLegacyOrchestrator -Goal "協調多個 PR 的長期專案"
```

The launcher prepends the framework to PYTHONPATH for this process only,
runs its diagnostics, and adds the Framework to Copilot's Skill discovery.
No Skills are copied globally and no Java repo is modified during preflight.

In an authenticated Copilot CLI session, check `/skills info poteto-mode`.
The Skill can be explicitly referenced in a prompt as `/poteto-mode`.
This is a **Copilot Agent Skill reference**, not the original Cursor
Plugin slash command. Copilot CLI can also choose relevant Skills automatically.

## Confirm the selected methods

```powershell
python -m sdlc.pstack_bridge check
python -m sdlc.poteto_strategy --project-root "D:\git\bank-application" --goal "修正申請狀態查詢錯誤"
python -m sdlc.entrypoint route --project-root "D:\git\bank-application" --goal "修正申請狀態查詢錯誤"
python -m unittest discover -s tests -v
```

Individual pstack Playbooks can also be inspected explicitly with
`python -m sdlc.poteto_strategy --goal "..." --upstream-playbook orchestrate`
(or any of the other 23 original IDs). This **does not execute them**.

## Boundaries and unresolved capabilities

- **Bank policy wins:** project business rules, explicit user permissions,
  impact/risk checks, model allowlists, G1–G6, protected CI and human approvals.
- **Live verification:** Feature Maps and test code are knowledge, not PASS.
  A bank integration G4 must remain BLOCKED until an approved real Adapter
  produces trustworthy runtime evidence; the included Cucumber Demo is synthetic.
- **Delegation:** main agent can only delegate if real Copilot subagent tools
  exist in its session and the model/organization permits them. Python route
  output is not a delegation transcript or proof of an independent review.
- **No Cursor emulation claim:** upstream Task/background workers, `/loop`,
  Cursor plugin installs, `/setup-pstack`, cloud VMs, watcher events,
  model presets, full autopilot, PR merges and deployments are not supplied
  as executable capabilities by this migration.
- **Long work:** work across sessions requires an actual supported task
  orchestration/continuation mechanism; this Skill alone cannot provide it.

The legacy `.github/skills/sdlc-mode/SKILL.md` and `start-sdlc.ps1`
still delegate to the canonical mode. `-UseLegacyOrchestrator` explicitly
restores the previous custom Agent launch for compatibility.
