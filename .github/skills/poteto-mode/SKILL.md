---
name: poteto-mode
description: >
  Goal-first engineering with Lauren Tan's pstack philosophy, adapted for
  GitHub Copilot CLI. The current session main agent owns the task, chooses
  the original Playbook, delegates only when useful, verifies real behavior,
  and learns from errors. For bug fixes, features, tests, refactoring,
  investigations, PR delivery and long-running programs.
---

# Poteto Mode — Main-agent owned workflow

**Owner: the Copilot session main agent that receives this Skill.**
This Skill is the canonical workflow entry. Never spawn a separate
`orchestrator` or a generic worker just to *run* Poteto Mode. The optional
`orchestrator` custom Agent is reserved for explicitly coordinated
long-running multi-PR programs and backwards compatibility.

**Upstream attribution:** Lauren Tan's unmodified, MIT-licensed pstack mode,
23 Playbooks, all 58 leaf Skills, and reference material are pinned in
`vendor/pstack/` (source hash in `MANIFEST.json`). Their principles and
playbook **decision logic** inform this native adaptation; references do not
register Cursor tools or bypass local financial controls.

## Work from the outcome, not the user's step list

1. Restate the real goal, what observable result counts as complete, and the
   **smallest evidence-backed change** likely to achieve it. Do not request
   the user to select Playbooks, Agents, Feature Maps, gates or models.
2. Run `python -m sdlc.entrypoint doctor --project-root .`,
   `python -m sdlc.entrypoint prepare --project-root . --goal "USER GOAL"`,
   `python -m sdlc.entrypoint route --project-root . --goal "USER GOAL"`.
   Use `execution_strategy` and `pstack_reference`. The Python classifiers
   **suggest** a route; inspect actual project facts, then confirm or override
   with an explicit reason. On a long program, consult
   `python -m sdlc.poteto_strategy --goal "USER GOAL" --project-root .`.
3. Read the selected original `vendor/pstack/skills/poteto-mode/playbooks/*.md`
   in full and only the relevant original `principle-*/SKILL.md` leaves.
   Read original `poteto-mode/SKILL.md` for the complete original decision
   framework; follow the adaptation boundary below. Keep a concise list of
   applicable versus inapplicable steps with reasons, not a rigid waterfall.
4. Inspect the target Java repo's code, AGENTS.md, requirements, Git history,
   Feature Map, tests and contracts. Use original `how`, `why`, `recall`
   methods where helpful, **not** unsupported Cursor commands. Identify
   uncertain business rules and obtain authoritative evidence rather than
   treating a generated Feature Map as truth.
5. Form observable done conditions. Investigations may remain read-only;
   test-only tasks can edit authorized test code but **not** product code.
   Establish acceptance criteria, dependencies, impact/risk flags and an
   approved environment before making a validated Task Contract. The draft
   context itself is neither a permission grant nor verified evidence.

## Original pstack engineering habits (implemented for Copilot)

- **Own the work.** Main agent owns the goal, Playbook, design, review,
  result and every delegate's output. A worker never becomes the owner.
- **Model the domain / subtract before adding.** Prefer a simpler data shape,
  smaller diff, idempotent boundaries, typed invariants and deletion of
  unnecessary layers to adding a new framework. Use `architect` for
  contested cross-boundary design; `arena` for meaningful alternatives.
- **Do not guess when you can observe.** Reproduce bugs on the same real
  surface; test competing root-cause hypotheses. Benchmark before and
  after performance changes. Prototype uncertain technical options instead
  of asking the user to choose what can be measured.
- **Parallelize deliberately.** Directly handle small, coherent tasks.
  Delegate independent implementation, coverage or reviews to available
  Copilot subagents if authorized and supported. If no subagent capability
  is available, perform the work directly, disclose loss of independent
  verification, and never claim a delegate ran. Assign one writer per
  overlapping branch/file; keep the brief's goal, paths, evidence and
  prohibited actions explicit.
- **Orchestrate only actual programs.** For an ongoing multi-PR project,
  original `orchestrate.md` is the selected Playbook: main agent coordinates
  owners, checks diffs/CI and uses independent verifiers. It does **not**
  edit those worker branches. Never make every trivial task pay for a
  coordinator. Cross-session monitoring needs actual host support.
- **Verify behavior, not stories.** If a suitable runtime surface is
  authorized, launch it, check its health, drive the real feature, collect
  reproducible evidence and clean up. For Java use approved Maven/JUnit/
  Cucumber runners and project-local test adapters. Feature Maps document
  user journeys; they do not establish PASS by themselves.
- **Encode the lesson.** If a failure repeats, fix a root cause, type
  constraint, lint/test/CI rule, or a narrowly scoped Skill. Compare behavior
  with an evaluation before accepting Skill improvements. Use original
  `reflect`, `correct` and `show-me-your-work` on appropriate tasks,
  including an auditable decision trail for consequential long work.
- **Communicate precisely.** Short user replies with observed results,
  proof, important tradeoffs, unfinished work and links. Read the original
  `unslop` and `technical-writing` guidance when needed.

## Source priority and hard safety gates

The **local SDLC Playbook Catalog**, project business rules, user scope and
bank-specific Task Contract/model-policy/G1-G6 requirements are mandatory
constraints, regardless of the chosen original pstack Playbook.
A high-risk action still requires authorized human approval.

The vendored pstack materials include instructions for Cursor `Task`,
`/loop`, cloud agents, Cursor plugins, model swaps, autonomous merges,
Bugbot and shipping. Those commands must **not** be executed as-is in
Copilot CLI. Only use equivalent host tools when present and authorized;
record missing capabilities as BLOCKED, not imaginary work.
`sdlc.mode` is a deterministic contract/worklist engine, not an Agent
dispatcher. A demo G4 cannot verify real bank staging.

## Copilot CLI entry

Default: `scripts/start-poteto.ps1 -ProjectRoot TARGET -Goal "outcome"`.
It adds the Framework directory to the session, then starts the **main
Copilot Agent**, explicitly requesting this Skill. It does *not* force
`--agent=orchestrator`. For old program-coordinator behavior, use
`-UseLegacyOrchestrator` explicitly.

Check discovery with `/skills list` and `/skills info poteto-mode`.
The slash-prefixed Skill reference is a Copilot Skill invocation, not
a native installation of Cursor's original `/poteto-mode` Plugin.
