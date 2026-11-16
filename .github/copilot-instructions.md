# Repository orientation

Copilot_sdlc is the **framework**, never the Java application being changed. Its Playbook source is `playbooks/catalog.json`; it also contains the Python engine `sdlc/` and opt-in Poteto Mode launcher `scripts/start-poteto.ps1` (legacy `start-sdlc.ps1`).

The canonical user-facing Skill is `.github/skills/poteto-mode/SKILL.md`, with `sdlc-mode` as a legacy alias. In an explicit SDLC session, the CLI working directory is the **target project**. The Orchestrator must run `python -m sdlc.entrypoint doctor --project-root .` followed by `python -m sdlc.entrypoint route --project-root . --goal "USER GOAL"` before choosing tasks/Skills. If the engine is unavailable, stop rather than inventing a Playbook. Select only stage-relevant Skills. Do not apply the framework's demo Feature Map/Cucumber fixtures as if they describe the target.

Maintain independent bank rules, approved models, and true runtime evidence. Do not mark unexecuted delegation or simulated tests as real.
