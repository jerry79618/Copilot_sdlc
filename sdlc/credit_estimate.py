"""Scenario-based AI Credits estimator using documented per-token USD rates.

No actual usage is fetched. This is not a claim about Lauren Tan's bills or
the user's GitHub account balance.
"""
import argparse
import json
import sys
from .contracts import ROOT, ContractError, load_json
from .model_policy import policy


def calculate(scenario, retries=0):
    if not isinstance(retries, int) or retries < 0 or retries > 10:
        raise ContractError("Retries must be between 0 and 10")
    budgets = load_json(ROOT / "config" / "usage-estimates.json")
    p = policy()
    if scenario not in budgets["cases"]:
        raise ContractError("Unknown scenario")
    case = budgets["cases"][scenario]
    expected_roles = set(p["profiles"][case["risk"]]["agents"])
    if set(case["tokens"]) != expected_roles:
        raise ContractError("Scenario tokens do not cover the selected risk profile")
    components = []
    for agent, counts in case["tokens"].items():
        if any(type(counts.get(k)) is not int or counts[k] < 0 for k in ("input", "output")):
            raise ContractError("Invalid token assumptions")
        model = p["agent_models"][agent]
        rate = p["prices_usd_per_million_tokens"][model]
        dollars = (counts["input"] * rate["input"] + counts["output"] * rate["output"]) / 1_000_000
        components.append({"agent": agent, "model": model, "input_tokens": counts["input"],
                           "output_tokens": counts["output"], "usd": round(dollars, 5),
                           "credits": round(dollars / budgets["usd_per_credit"], 2)})
    base = sum(part["usd"] for part in components)
    total = base * (1 + retries)
    return {
        "scenario": scenario, "risk": case["risk"], "description": case["description"],
        "source_date": budgets["as_of"], "assumption": "all input uncached, default context",
        "retries": retries, "model_components": components,
        "estimated_ai_credits": round(total / budgets["usd_per_credit"], 2),
        "estimated_usd": round(total, 2),
        "sensitivity_credits": {
            "half_token_budget": round(0.5 * total / budgets["usd_per_credit"], 2),
            "double_token_budget": round(2 * total / budgets["usd_per_credit"], 2),
        },
        "estimated_active_time_min": case["active_time_min"],
        "estimated_banking_end_to_end_time_min": case["bank_end_to_end_time_min"],
        "limitations": budgets["assumptions"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Estimate Copilot AI Credits from assumed token budgets")
    parser.add_argument("--scenario", choices=["small", "medium", "large", "all"], default="all")
    parser.add_argument("--retries", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        names = ["small", "medium", "large"] if args.scenario == "all" else [args.scenario]
        print(json.dumps({"estimates": [calculate(n, args.retries) for n in names]},
                         ensure_ascii=False, indent=2))
        return 0
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
