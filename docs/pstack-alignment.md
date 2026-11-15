# pstack philosophy -> Copilot_sdlc v0.5

Original public pstack: https://github.com/cursor/plugins/tree/main/pstack

This is an independent bank-safe interpretation of Lauren Tan's workflow
concepts, NOT an installation/fork of pstack. GitHub Copilot CLI does not
automatically gain the Cursor slash command /poteto-mode.

## Concept-to-implementation map

| pstack concept | Copilot_sdlc counterpart | Real boundary |
| --- | --- | --- |
| Short goal /poteto-mode | Orchestrator + sdlc-mode Skill | Native Copilot Agent, not Cursor slash command |
| Engineering principles first | docs/principles.md | Agent instruction |
| Select Playbook | playbooks/catalog.json and sdlc.mode route | Deterministic hint |
| Copy Playbook steps to todos | sdlc.mode start/status/advance/checkpoint | Auditable worklist |
| Situational Skills | stages[].skills | Needs actual Copilot delegation |
| Feature Map / how-to-use | sdlc.discovery and feature-map-discovery Skill | Static evidence only until driven in app |
| Verification-first | Cucumber JVM + normalized G4 evidence | Memory-only adapter currently |
| Reflect / correct | reflection Skill + sdlc.reflect | Human-reviewed suggestions |
| Skills evals | skill-eval + sdlc.quality_eval | Deterministic routing checks, not real LLM eval |
| Prototype / multi-phase | Prototype and multi-phase Playbooks | Specified, not unattended background jobs |
| Model specialization | banking-model-policy.json | Fixed model policies; org approval required |
| Swarm / interrogate | reviewer and cross-reviewer roles | Actual parallel dispatch unverified |
| Babysit / ship | GitHub Actions + PR handoff | No autonomous merge |
| Bank risk / human sign-off | Task Contract + risk escalation + G6 plan | Enterprise addition, GitHub permissions external |

## Operator runbook

1. Give goal and done check. Orchestrator reads principles, relevant Feature Map,
   Task Contract and business rules. Risk planner checks financial impact.
2. Select an authorized Playbook; open ordered worklist.
3. At each stage load ONLY mapped Skills; create a real evidence file.
4. Missing Feature Map: scan source into candidate under artifacts/discovery;
   review business facts, create a runnable Cucumber journey, verify behavior.
5. PASS at G4 requires real evidence. FAIL -> diagnose root cause; BLOCKED ->
   name missing data/owner. Do not switch test-only task to code changes.
6. Review CI and code; high-risk case needs independent two-model review and
   authorized human release approval. Changes are not auto-merged or deployed.
7. Reflect on observed problems and encode durable checks; run quality evals.

## Limitations

The router cannot invoke Copilot agents itself or check model entitlements.
Static Java scans are incomplete and cannot confirm UI behavior or banking rules.
The present Cucumber tests are an in-memory demo, not connected to bank APIs.
Routing evals don't measure real model accuracy. Worklist gates other than G4
validate evidence file existence only, not source authenticity. CI checks,
G6 authorizations and data permissions require bank/GitHub administration.

## Commands

    python -m sdlc.mode catalog
    python -m sdlc.discovery inspect
    python -m sdlc.discovery health
    python -m sdlc.quality_eval
    python -m unittest discover -s tests -v
    mvn -B -ntp -f cucumber/pom.xml test
