---
name: skill-eval
description: >
  Evaluate SDLC routing and Skill changes against predeclared cases.
  Use when modifying Agent instructions, Skill descriptions, model policies,
  Playbook selection, generated Cucumber quality or agent prompt behavior.
---

# Skill and Agent Evals

1. State behavior to improve, risks, baseline and observable success metric.
2. Choose realistic positive and negative cases plus holdout failures.
3. Run deterministic check: python -m sdlc.quality_eval
   This tests routing and Skill data only, NOT an LLM's actual behavior.
4. For real Copilot evaluation use authenticated sessions, same workload,
   independent judges and real application verification. Record actual
   model, context, actions, evidence, time and AI Credits.
5. Compare predeclared metrics; don't trust self-rated correctness or weak tests.
6. Reject changes which hide failures by weakening assertions.
7. Record sample sizes, unknowns and confounders.
8. Add failing cases to evals, then rerun CI and actual harness after each edit.
9. Don't report a deterministic routing PASS as real Agent validation.
