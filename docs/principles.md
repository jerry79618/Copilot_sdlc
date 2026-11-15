# Engineering principles for Copilot_sdlc

**Project context.** We are building an AI SDLC orchestration framework for banking engineering. It currently uses synthetic cross-system verification, not live bank interfaces. Match effort and documentation to the actual task.

**Non-negotiable business invariants.** Money calculations, consistency, authorization and privacy must be correct. Treat business rules and production operations as requiring proper authority. An observed demo test is not proof of production behavior.

**Autonomous, accountable delivery.** Within the given scope, decide reasonable implementation details and test them rather than repeatedly requesting permission. Explain outcomes, meaningful decisions, significant alternatives and unresolved evidence gaps. Do not confuse instructions with access control: CI, protected environments and bank approvals enforce the mandatory boundaries.

A repeated failure should lead to a precise test, schema check or tooling rule where possible. Do not accumulate defensive prose without measurable value.
