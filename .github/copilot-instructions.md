# Repository orientation

Copilot_sdlc is the **framework**, never the Java application being changed. Its Playbook source is `playbooks/catalog.json`; it also contains the Python engine `sdlc/` and opt-in launcher `scripts/start-sdlc.ps1`.

In an explicit SDLC session, the CLI working directory is the **target project**. The Orchestrator must run `python -m sdlc.entrypoint doctor --project-root .` followed by `python -m sdlc.entrypoint route --project-root . --goal "USER GOAL"` before choosing tasks/Skills. If the engine is unavailable, stop rather than inventing a Playbook. Select only stage-relevant Skills. Do not apply the framework's demo Feature Map/Cucumber fixtures as if they describe the target.

Maintain independent bank rules, approved models, and true runtime evidence. Do not mark unexecuted delegation or simulated tests as real.
