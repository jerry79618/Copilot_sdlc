# Operator guide

## Requirements
Python 3.11+, Git, and GitHub Copilot CLI with a valid authorized account for
Agent use. No Python package installation is needed when using the v0.7
PowerShell launcher.

## Launch against a sibling Java repository (Windows, v0.8)

```powershell
cd D:\git\Copilot_sdlc
.\scripts\start-sdlc.ps1 -ProjectRoot "D:\git\bank-application" -CheckOnly
.\scripts\start-sdlc.ps1 -ProjectRoot "D:\git\bank-application" -Goal "幫我補齊查詢功能測試，不要修改產品程式"
```

Use `-Isolated` when you do not want the default `~/.copilot` personal
Agents/Skills in the same session; that profile will need its own login.
Read [cross-project setup, conflicts and scope](cross-project-v07.md).
The user only supplies an outcome and authorization scope; Orchestrator must
verify the real Playbook through `sdlc.entrypoint`.
The v0.8 launcher also runs entrypoint prepare to produce a read-only draft
Task Context. See [v0.8 migration](cross-project-v08.md).

## Framework demo checks

```bash
python -m unittest discover -s tests -v
python -m sdlc.entrypoint doctor --project-root .
python -m sdlc.entrypoint route --project-root . --goal "新增訂單查詢"
python -m sdlc.cli validate --task contracts/examples/verification.json
python -m sdlc.cli plan --task contracts/examples/development.json
python -m sdlc.cli verify --task contracts/examples/verification.json --output-dir artifacts
```

- `PASS` / exit 0: **only the specified adapter** verified assertions.
- `FAIL` / exit 1: inspected actual failed assertions.
- `BLOCKED` / exit 2: a prerequisite or authorized real adapter is missing.
- `ERROR` / exit 3: invalid data or execution problem.

## Production controls

SDLC Worklists are **not** running Agent dispatchers. Test-only tasks must not
change product code, and synthetic Cucumber demo evidence is **not** proof of
bank integration. Configure GitHub required checks, CODEOWNERS and protected
environments separately. Never bypass authorization.
