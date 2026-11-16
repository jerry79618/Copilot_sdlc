# v0.7 — Opt-in SDLC from any Java repository (no plugin)

## Goal

Run the **existing** framework from a sibling project, without copying ten SDLC
Skills to your personal Copilot folder or prompting for the SDLC's internal steps.

A Windows example:

```text
D:\git\Copilot_sdlc\
D:\git\bank-application\
D:\git\bank-risk\
```

## One-command launcher

Open PowerShell and run:

```powershell
cd D:\git\Copilot_sdlc
.\scripts\start-sdlc.ps1 -ProjectRoot "D:\git\bank-application" -CheckOnly
.\scripts\start-sdlc.ps1 -ProjectRoot "D:\git\bank-application" -Goal "幫我修正申請查詢的錯誤"
```

The launcher temporarily prepends the framework root to `PYTHONPATH`, runs
`python -m sdlc.entrypoint doctor`, changes the working directory to the target,
and launches `copilot --agent=orchestrator --add-dir=<framework-root>`.
It restores working directory and environment afterward. `--add-dir` makes the
framework's agents/skills discoverable for **this CLI session**. Existing bank
source, AGENTS.md and Cucumber tests remain in the target repository. Nothing is
copied to the target or global `~/.copilot/skills`.

To isolate the Copilot user configuration and avoid personal Skills/Agents:

```powershell
.\scripts\start-sdlc.ps1 -ProjectRoot "D:\git\bank-application" -Isolated -Goal "補齊申請查詢測試，不要修改產品程式"
```

`-Isolated` uses a separate `$HOME\.copilot-sdlc` via `COPILOT_HOME`.
**It does not transfer your existing login, model selection, trusted paths,
permissions or sessions**: you may need to sign in and configure that profile
once. Files under `~/.agents/skills` and repository skills may still be
discoverable; this is not a hard security sandbox. Do not disable enterprise controls.

## Why the preflight may BLOCK

1. An older `~/.copilot/agents/orchestrator.agent.md` can override the repository
   Orchestrator. Back it up and update it from
   `Copilot_sdlc/.github/agents/orchestrator.agent.md`, **or use -Isolated**.
2. Older SDLC Skill copies in `~/.copilot/skills/<name>/SKILL.md` or
   `~/.agents/skills/<name>/SKILL.md` can shadow the framework. Back up/remove
   only stale *SDLC-named* copies; preserve unrelated personal Skills.
3. If Python cannot import the engine, use this launcher rather than running
   `copilot --agent orchestrator` directly from a sibling Java repo. Do not
   assume a sibling folder is automatically on Python's import path.
4. To inspect discovery manually, run:
   `python -m sdlc.entrypoint route --goal "修復查詢錯誤" --project-root "D:\git\bank-application"`
   with the framework on `PYTHONPATH`.

## What is and is not automatic

- **Yes:** deterministically inspect the actual Playbook catalog; resolve the
  selected Playbook and per-stage Skill paths from any project; diagnose stale
  user-level SDLC copies; opt into framework agents and skills per CLI session.
- **No:** this Python command does not dispatch an LLM, create a valid banking
  Task Contract from arbitrary natural language, run live bank adapters, enforce
  external approvals, or automatically guarantee real Agent delegation.
- **No hard isolation with the default profile:** unrelated personal Skills can
  still be exposed to Copilot. The Orchestrator is instructed to choose only
  stage-relevant Skills, but this is a **behavioral instruction**, not a security
  boundary. Prefer `-Isolated` when you want a cleaner profile.

For high-risk banking tasks, obtain the organization model approvals and use
real bank-system testing and protected CI; G4 demo evidence is not SIT proof.
