# Poteto Mode — Copilot CLI native engineering entry

The current goal-first mode is `.github/skills/poteto-mode/SKILL.md`,
a **GitHub Copilot Agent Skill**. The `orchestrator` Agent remains responsible
for orchestration. This is a local Copilot adaptation of Lauren Tan's
MIT-licensed pstack philosophy; it is **not** the original Cursor plugin.

## Run against your own Java repository

```powershell
cd D:\git\Copilot_sdlc

# Check only: no Java repository changes, no Copilot launch
.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -CheckOnly

# Start with a short user outcome
.\scripts\start-poteto.ps1 -ProjectRoot "D:\git\bank-application" -Isolated -Goal "修正申請狀態查詢錯誤"
```

Within the Copilot CLI session (with the Framework in `--add-dir`), run:

```text
/skills list
/skills info poteto-mode
```

You can explicitly invoke a loaded skill with a prompt such as:

> Use the /poteto-mode skill to find gaps in Java query tests and close them. Do not change production code.

Copilot's `/poteto-mode` here is a **Skill reference in the prompt**;
it is not identical to Cursor's plugin `/poteto-mode` command.
Skill discovery depends on your Copilot CLI version and active directory.

## Architecture and source priority

- The **canonical** skill is `.github/skills/poteto-mode/SKILL.md`.
- The **internal Agent** is `.github/agents/orchestrator.agent.md`.
- The **stable Python API** remains `python -m sdlc.mode` (no migration).
- The local 11 Playbooks stay in `playbooks/catalog.json`.
- Original pstack references stay unchanged under `vendor/pstack` and use
  the pinned MIT license and `sdlc.pstack_bridge`.
- Target Java project business knowledge and tests remain inside that project.
- Banking risk restrictions, human approvals and evidence rules override
  any upstream method. No Cursor-only commands or auto-merge are enabled.

## Backward compatibility

Old `scripts/start-sdlc.ps1` delegates to `start-poteto.ps1`.
Old `.github/skills/sdlc-mode/SKILL.md` is a small deprecated shim pointing
to the new canonical Skill. They are not separate modes.

If a user-level or target-repository `poteto-mode`/`sdlc-mode` differs from
this Framework, the preflight reports a conflicting candidate. Back it up
rather than overwriting unrelated personal Skills. The optional `-Isolated`
Copilot profile may need a separate login and is not a security sandbox.

## Checks

```powershell
python -m sdlc.entrypoint doctor --project-root "D:\git\bank-application"
python -m sdlc.entrypoint route --project-root "D:\git\bank-application" --goal "修正查詢錯誤"
python -m sdlc.pstack_bridge check
python -m unittest discover -s tests -v
```

These deterministic checks only verify configuration and routing.
They do **not** prove Copilot used the skill, dispatched a subagent, or
executed live bank integration tests. Real G4 remains BLOCKED without
approved runtime adapters and verifiable test evidence.
