# Copilot_sdlc — project context

This is a **bank-oriented AI SDLC orchestration framework under development**, not a live banking application. It uses Python Playbooks, Copilot CLI Agents/Skills, Feature Maps and Java Cucumber verification. The current cross-system adapter is synthetic.

## Business invariants
- Financial amounts, ledger states, idempotency, authorization and customer privacy must be correct. Never invent banking policy when evidence or accepted rules are unavailable.
- Never send credentials or unredacted customer information to AI tools. Production writes, payment actions, merging or deployment require the bank's established authorization.
- Test conclusions are environment-specific: a demo result never proves staging or production correctness. Preserve real verification evidence.

## Autonomy and delivery
Within the user's authorized scope, choose normal engineering approaches independently. Investigate uncertainty, prototype when useful, and ask only for genuine business decisions, privileged actions or irreversible consequences.
Use `.github/skills/poteto-mode/SKILL.md` as the canonical goal-first Skill; `sdlc-mode` is the legacy alias. Playbooks, risk policy and tests govern execution; these instructions are not a substitute for CI or access controls.
Finish concisely: result, tests/evidence, key decisions, significant rejected alternatives and unresolved risks.
