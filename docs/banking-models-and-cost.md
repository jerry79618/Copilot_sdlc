# Banking AI Models, Security Gates and AI Credits (2026-11-16)

## Goals

Bank-grade implementation of Lauren Tan's **role-sensitive** model selection, but NOT the original pstack and NOT Lauren's measured usage. All model choices below require the bank organization's explicit authorization. The `.agent.md` model lock only restricts Copilot CLI dispatch; it is not a bank compliance certification.

## Which agent runs which model?

| Effective risk | Orchestrator | Developer | Tester | Reviewer(s) | Business sign-off |
| --- | --- | --- | --- | --- | --- |
| low | Sonnet 5.5 | GPT-6.1 Terra | Sonnet 5.5 | Sonnet 5.5 | task-level rules |
| medium | Sonnet 5.5 | GPT-6.1 Sol | Sonnet 5.5 | Sonnet 5.5 | task-level rules |
| high | Sonnet 5.5 + read-only Opus 5.5 analyst | GPT-6.1 Sol | Sonnet 5.5 | Opus 5.5 + independent GPT-6.1 Terra | Required business + release owners |

Each role is a different Copilot CLI custom Agent; a single agent's `model` does **not** change dynamically with task risk. The `sdlc.model_policy route` command chooses which Agents should be used. Copilot Orchestrator **must actually dispatch them**. High-risk analyst/reviewers have read-only tool restrictions; no AI may autonomously deploy or merge.

Impact flags such as `money_movement`, `ledger_consistency`, `customer_pii`, `authorization`, `cross_system_financial`, `production_change` escalate to high even when a Task Contract declares low. `external_dependency` and `customer_impact` elevate low to at least medium. Unknown flags fail validation at routing. Do not use task classification as permission to expose sensitive banking data.

### Commands

    python -m sdlc.model_policy check
    python -m sdlc.model_policy route --task contracts/examples/verification.json
    python -m sdlc.model_policy route --task contracts/examples/banking-high-risk.json
    python -m sdlc.credit_estimate --scenario all
    python -m sdlc.credit_estimate --scenario medium --retries 1

## Hypothetical tokens → AI Credits

**GitHub AI Credits are not Cursor pstack credits.** Official GitHub overage is based on tokens, at USD 0.01 per credit. Prices here reflect the published default context model rates as retrieved 2026-11-16. Rates are USD per 1M tokens:

| Model | Input | Cached input | Cache write | Output |
| --- | ---: | ---: | ---: | ---: |
| Sonnet 5.5 | $2.00 | $0.10 | $2.50 | $10.00 |
| Opus 5.5 | $4.00 | $0.20 | $5.00 | $20.00 |
| GPT-6.1 Terra | $1.00 | $0.05 | $1.25 | $5.00 |
| GPT-6.1 Sol | $2.00 | $0.10 | $2.50 | $10.00 |

**Model formula:** `credits = sum_agent[(input_tokens * usd_per_million_input + output_tokens * usd_per_million_output) / 1_000_000 / 0.01]`. Inputs are assumed uncached and each request within standard context tiers; output includes billed reasoning tokens. We do not model cache writes, context tier increases, retries beyond the specified budget, or organization-specific pricing. The estimator is a reproducible scenario approximation, **not** actual usage.

| Scope | Hypothetical included work | Agent run wall time (not measured) | Bank end-to-end elapsed (not measured) | Estimated base Credits | Scenario 0.5–2× tokens |
| --- | --- | --- | --- | ---: | ---: |
| Small low-risk | focused code + BDD/unit + review | 15–50 min | 30–120 min | 58 | 29–116 |
| Medium | Java API, data fixtures, Cucumber, CI and review | 1–4 h | 2–8 h | 265 | 133–530 |
| Large high-risk | many-system invariants, iterations and dual-review | 4–20 h | 1–5 business days | 1,578 | 789–3,156 |

The sensitivity range is deliberately wide. One full extra cycle doubles the estimate only if it repeats *all* the modeled usage; correcting just one stage costs less. High-context tier and extended investigation can raise costs above these ranges. Model total may decrease with cache reads but cache writes also cost money.

## Lauren Tan /poteto-mode comparison

Lauren's public pstack config specifies **Grok 4.7** for ordinary code roles, **Opus 5.5** for hardest judgment, and mixed-model review. There is **no independently verified public dataset mapping tiny, medium or large pstack runs to wall time and GitHub AI Credits**. Her coordinator runs are often parallel; throughput numbers are not comparable to the elapsed time for one regulated banking change.

For **illustration only** (not Lauren's measurements), assuming an existing verification environment and readily available dependencies, an analogous autonomous run might consume ~10–30 min for a small fix, ~30–120 min for a medium feature, and ~3–12 hours for a large cross-cutting task. These are rough planning ranges, **not observed Lauren metrics**. Banking elapsed time must account for review queues, test data approvals, integration dependencies and release controls, and can exceed the table.

## Bank controls / go-live checklist

1. Obtain an approved-provider/model list from bank administrators and confirm the exact model IDs in `/model`. The repository is only a proposal.
2. Ensure Copilot CLI policies, data retention/residency terms and any vendor terms are approved. Do not send raw personal, payment or bank account data to any model or MCP.
3. Define permissions independently of Agent instructions: branch protection, required CI, reviewer CODEOWNERS, staging-only test credentials and protected environments.
4. For high risk, store real review approvals and observed verification evidence in trusted systems; a worklist PASS is not signed evidence.
5. Monitor actual usage through `/usage` and organization billing, including retries, cache hits and long-context requests. Recalculate from logs with this estimator.
6. If `modelPolicy: required` model is unavailable, stop and ask for authorization; do not silently choose another provider.

## Primary sources

- GitHub AI Credits and pricing: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
- GitHub custom agent model policy: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- GitHub CLI custom agents: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
- Lauren Tan /setup-pstack: https://github.com/cursor/plugins/blob/main/pstack/skills/setup-pstack/SKILL.md
- Lauren Tan /poteto-mode: https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md
