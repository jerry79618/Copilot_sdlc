# Copilot SDLC — Enterprise AI SDLC v0.4

**GitHub Copilot CLI-first framework: goal-first SDLC Mode, eight Playbooks, staged Skills, development/testing separation and auditable verification evidence.**

> Status: **executable initial scaffold**, not a production-ready autonomous deployment platform. The included three-system journey is a **local, in-memory simulation**. No bank, payment, external API or production integration is configured. This project is an independent implementation inspired by Lauren Tan's verification-first ideas, not an official pstack port.


## SDLC Mode v0.2 — one goal, routed Playbook

The default entry point is the **`orchestrator` Copilot CLI agent + `sdlc-mode` Skill**, inspired by Lauren Tan's goal-first `/poteto-mode`. This is our own implementation: `/poteto-mode` is **not** a GitHub Copilot CLI command.

```bash
# Agent-facing invocation (requires authenticated Copilot CLI)
copilot --agent orchestrator --prompt "測試跨系統人工覆核；請確認資料與環境，保存證據，不得修改產品程式碼。"

# Deterministic workflow management (no Copilot authentication required)
python -m sdlc.mode catalog
python -m sdlc.mode route --goal "新增訂單查詢 API"
python -m sdlc.mode start --task contracts/examples/verification.json
# Use the worklist file returned above:
python -m sdlc.mode status --run artifacts/worklist-TASK-VERIFY-001-<timestamp>.json
```

Workflow: **Goal → Task Contract → Select Playbook → Ordered Worklist → Skill per stage → G1–G5 Evidence → Review / Report**.

Supported Playbooks: `feature`, `bug-fix`, `verification`, `investigation`, `refactor`, `performance`, `review`, `figure-it-out`. Unknown intent defaults to read-only planning. Each stage must record actual evidence, and runtime verification (G4) rejects unavailable external systems. Testing-only tasks cannot silently switch to source-code modification.

Read [SDLC Mode operator guide](docs/sdlc-mode.md), [playbook catalog](playbooks/README.md) and [central Skill](.github/skills/sdlc-mode/SKILL.md). **Copilot agent routing and delegation still require a real authenticated Copilot CLI run**; Python is the deterministic worklist engine, not an AI runtime.

## Cucumber BDD + Feature Map (v0.3)

**Testing now uses executable Cucumber-JVM Gherkin and Java Step Definitions.** The Feature Map remains behavioral, with a machine-readable link to actual tests and cross-system fixtures. See [Cucumber guide](docs/cucumber-bdd.md).

    python -m sdlc.feature_map validate
    mvn -B -ntp -f cucumber/pom.xml test
    python -m sdlc.cucumber_evidence --task contracts/examples/verification.json --feature manual-review

The JSON/HTML report lives in cucumber/target/cucumber-report/. The normalized artifacts/cucumber-evidence.json feeds SDLC G4. The demo adapter is in-memory; PASS does **not** prove a real integration.

## Banking risk-aware agents and AI credits (v0.4)

Risk-aware routing maps Task Contract risk (low/medium/high) and critical impact flags to role-specific agent models. Transaction, ledger, customer privacy, authorization and cross-system financial risks require TWO independent reviews and human release approval. All models must be approved by the bank organization.

    python -m sdlc.model_policy check
    python -m sdlc.model_policy route --task contracts/examples/banking-high-risk.json
    python -m sdlc.credit_estimate --scenario all
    python -m sdlc.credit_estimate --scenario medium --retries 1

Agent roles: orchestrator (Claude Sonnet 5.5); standard developer (GPT-6.1 Terra); complex developer (GPT-6.1 Sol); tester (Sonnet 5.5); standard reviewer (Sonnet 5.5); banking analyst/reviewer (Opus 5.5); cross-reviewer (GPT-6.1 Terra). Model availability is organization-dependent; each agent requires its configured model rather than silent fallback.

Costs use GitHub's published per-million-token rates (1 AI credit = USD 0.01), not actual agent bills. See [Bank model policy and credit methodology](docs/banking-models-and-cost.md).

## Architecture

```mermaid
flowchart TD
  A[Issue / Request] --> B[Copilot CLI Orchestrator]
  B --> C[Task Contract / Context Discovery]
  C --> D{Intent}
  D -->|Development| E[Explore > Design > Implement > Unit/Contract]
  D -->|Verification| F[Scenario > Dependency > Test Data > Readiness]
  D -->|Investigation| G[Read-only Evidence / Root Cause]
  E --> F
  F --> H[Runner / Verification Skills]
  H --> I{Evidence}
  I -->|PASS| J[Review / CI Gate / PR]
  I -->|FAIL| K[Classify / Repair with authorization]
  I -->|BLOCKED| L[Missing adapter / data / environment]
  K --> E
  J --> M[Approval / Release]
  M --> N[Regression / Evals / Improve Knowledge]
  N -.-> C
```

## Quick start (Python 3.11+, stdlib only)

```bash
git clone https://github.com/jerry79618/Copilot_sdlc.git
cd Copilot_sdlc
python -m unittest discover -s tests -v
python -m sdlc.cli validate --task contracts/examples/verification.json
python -m sdlc.cli plan --task contracts/examples/development.json
python -m sdlc.cli verify --task contracts/examples/verification.json
```

Last command writes a timestamped JSON evidence file to `artifacts/`. It checks the fixture, orders steps by dependencies, executes a **mock risk → application → sync journey**, and verifies three assertions. The result contains `classification: DEMO_VERIFIED`, **not** a real E2E certification.

For a non-demo environment, the safe behavior is intentional:

```bash
python -m sdlc.cli verify --task contracts/examples/verification.json
# Try setting "environment" to "staging" in a *copy* of the contract:
# result = BLOCKED / EXTERNAL_ADAPTER_UNAVAILABLE, exit code 2
```

## Use with GitHub Copilot CLI

Install/sign into GitHub Copilot CLI according to [GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview); enter the repository and run `copilot`.

Example prompt (no unofficial slash command required):

> Use the orchestrator agent and task-routing skill. Implement the requirements in `contracts/examples/development.json`. Explore the repository first, explain the actual code changes, keep all non-demo integrations blocked, run the contract checks and verification suite, then report evidence and unresolved gaps. Do not deploy.

For testing-only:

> Use the tester agent and verification skill for `contracts/examples/verification.json`. Do not change product code. Run scenario readiness and verification, distinguish PASS from BLOCKED, and link the JSON evidence.

Select agents using `/agent` or `copilot --agent tester --prompt "..." ` where supported. See `.github/agents/`, `.github/skills/`, `AGENTS.md`.

## Repository map

| Directory | Responsibility |
| --- | --- |
| `sdlc/` | Deterministic Task Contract validation, routing, demo runner, evidence |
| `.github/agents/` | Orchestrator / developer / tester / reviewer agent definitions |
| `.github/skills/` | Reusable route, implementation, verification, cross-system data, failure triage |
| `contracts/examples/` | Sample development, testing, investigation requests |
| `scenarios/` | Ordered steps, dependencies and assertions |
| `fixtures/` | Synthetic-only seed data |
| `docs/feature-map/` | Human/agent-readable navigation + verification guidance |
| `docs/` | Architecture, quality gates, adapter interface and future work |
| `tests/` | Python contract/runtime/evaluation tests |
| `.github/workflows/ci.yml` | Mandatory deterministic validation and example evidence on pushes/PRs |

## Gates and outcomes

G1 Spec → G2 Verifiability → G3 Readiness → G4 Execution → G5 Independent Review/CI → G6 Release approval.

`PASS` means verified against the **explicit adapter and evidence**; `FAIL` means an assertion failed; `BLOCKED` means the prerequisites/adapter are unavailable; `ERROR` means malformed inputs or internal runtime errors. Exit codes: 0/1/2/3 respectively.

**Do not treat prompt text as access control.** Configure repository rulesets, CI required checks, environment protection, approved adapters, and credentials in the target organization before enabling real integrations. The initial repo cannot enforce these GitHub settings itself.

## Initial scope / intentionally not done

- No Copilot CLI API call is automated by Python. Agent invocation and task interpretation use Copilot CLI with repository agents/skills; the Python side is a deterministic contract and demonstration verifier.
- No live external system, real credentials, automatic write API, database writes, continuous incident processing or production deployment.
- No claim that a synthetic three-service simulation proves a banking integration.
- Dynamic Workflows, authenticated test data provisioning, Cucumber/Selenium/Java adapters, reliable cleanup, long-running async polling, and production ruleset configuration are later phases; see `docs/roadmap.md`.

## References

- [GitHub Copilot CLI custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [GitHub Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Lauren Tan verification-skill example](https://github.com/poteto/verification-skill-example)
