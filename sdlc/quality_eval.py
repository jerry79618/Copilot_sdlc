"""Deterministic routing/skill regressions. NOT an authenticated LLM agent evaluation."""
import argparse
import json
import sys
from pathlib import Path

from .contracts import ROOT, ContractError, load_json
from .mode import catalog, classify


def evaluate(routing_cases=None, skill_cases=None):
    routing_cases = routing_cases if routing_cases is not None else load_json(
        ROOT / "evals" / "mode-routing-cases.json")
    skill_cases = skill_cases if skill_cases is not None else load_json(
        ROOT / "evals" / "skill-routing-cases.json")
    books = catalog()
    checks = []
    for case in routing_cases:
        got = classify(case["goal"], case.get("intent"))["playbook"]
        checks.append({"type": "route", "case": case["goal"],
                       "expected": case["expected_playbook"],
                       "actual": got, "pass": got == case["expected_playbook"]})
    for case in skill_cases:
        book = books.get(case["playbook"])
        steps = {s["id"]: s for s in book["stages"]} if book else {}
        actual = steps.get(case["stage"], {}).get("skills", [])
        expected = case["must_use_skill"]
        checks.append({"type": "stage-skill",
                       "case": case["playbook"] + "/" + case["stage"],
                       "expected": expected, "actual": actual,
                       "pass": expected in actual})
    passing = sum(row["pass"] for row in checks)
    return {
        "type": "deterministic-routing-regression",
        "status": "PASS" if passing == len(checks) else "FAIL",
        "passed": passing, "total": len(checks),
        "accuracy": round(passing / len(checks), 3) if checks else 0,
        "cases": checks,
        "limitation": "No LLM, real Copilot delegation, or user behavior was evaluated.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Static SDLC routing/skills quality evals")
    parser.add_argument("--output", default="artifacts/skill-routing-eval.json")
    args = parser.parse_args(argv)
    try:
        result = evaluate()
        target = Path(args.output).resolve()
        if not target.is_relative_to(ROOT):
            raise ContractError("Evaluation output must remain inside repository")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(json.dumps({"status": result["status"], "passed": result["passed"],
                          "total": result["total"], "report": str(target)}, ensure_ascii=False))
        return 0 if result["status"] == "PASS" else 1
    except (ContractError, KeyError, OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
