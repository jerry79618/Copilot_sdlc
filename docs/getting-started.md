# Operator guide

## Requirements
Python 3.11+, Git, optional GitHub Copilot CLI with a valid account. No pip dependencies for the demo.

## Run locally
```bash
python -m unittest discover -s tests -v
python -m sdlc.cli validate --task contracts/examples/verification.json
python -m sdlc.cli plan --task contracts/examples/development.json
python -m sdlc.cli verify --task contracts/examples/verification.json --output-dir artifacts
```

## Read the result
- `PASS` / exit 0: **only the specified adapter** verified its assertions.
- `FAIL` / exit 1: check observed state and assertions.
- `BLOCKED` / exit 2: input is valid but adapter, data, or environment is unavailable.
- `ERROR` / exit 3: invalid contract or execution runtime problem.

## CLI-assisted run
```bash
copilot --agent orchestrator --prompt "Route the test request in contracts/examples/verification.json, validate it, execute safe verification and summarize evidence. No product code changes."
```

Copilot access and tools require your local GitHub permissions and CLI setup. This command is a **manual launch**, not an unattended GitHub Actions trigger.

## Production controls
Set up repository required checks, code owners and protected environments in GitHub settings separately. Never use unchecked agent-run shell access as a substitute for those controls.
