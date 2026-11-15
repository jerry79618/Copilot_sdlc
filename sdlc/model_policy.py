"""Risk-aware model dispatch recommendations for GitHub Copilot CLI.

The planner cannot attest that a model was actually invoked. Copilot CLI's
required model policy, organization allowlists and human approvals are separate.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from .contracts import ROOT, ContractError, load_json, validate_task

RISK = {"low": 0, "medium": 1, "high": 2}
PATTERN = re.compile(r"^([a-zA-Z][A-Za-z0-9]*):\s*(\S+)\s*$", re.M)


def policy():
    p = load_json(ROOT / "config" / "banking-model-policy.json")
    if p.get("version") != 1 or p.get("mode") != "fail-closed":
        raise ContractError("Invalid banking model policy")
    if set(p.get("profiles", {})) != set(RISK):
        raise ContractError("Missing risk profiles")
    return p


def resolve(task, config=None):
    validate_task(task)
    config = config or policy()
    effective = task["risk"]
    causes = []
    flags = task.get("impact_flags", [])
    if not isinstance(flags, list) or any(not isinstance(f, str) for f in flags):
        raise ContractError("impact_flags must be a list of strings")
    unknown = sorted(set(flags) - set(config["impact_minimum_risk"]))
    if unknown:
        raise ContractError("Unknown impact flags: " + ", ".join(unknown))
    for flag in sorted(set(flags)):
        minimum = config["impact_minimum_risk"][flag]
        if RISK[minimum] > RISK[effective]:
            effective = minimum
            causes.append(flag + " → " + minimum)
    profile = config["profiles"][effective]
    agents = []
    for name in profile["agents"]:
        if name not in config["agent_models"]:
            raise ContractError("Undefined model mapping for agent " + name)
        model = config["agent_models"][name]
        if model not in config["prices_usd_per_million_tokens"]:
            raise ContractError("Model not in local price/allowlist: " + model)
        agents.append({"agent": name, "model": model})
    approval = bool(profile["human_approval"] or task.get("approval_required", False))
    return {
        "task_id": task["id"],
        "declared_risk": task["risk"],
        "effective_risk": effective,
        "escalated": effective != task["risk"],
        "escalation_reasons": causes,
        "dispatch": agents,
        "quality_gates": profile["quality_gates"],
        "human_approval_required": approval,
        "review_owners": profile.get("review_owners", []),
        "manual_approvers": profile.get("manual_approvers", []),
        "external_deployment_allowed": False,
        "enforcement_notes": [
            "Routing is an auditable recommendation, not automatic agent dispatch.",
            "Fail closed if organization has not approved all listed models.",
            "Configure GitHub rulesets, required checks and approval externally.",
        ],
    }


def check_agents(config=None):
    """Static fail-closed consistency check; not proof of Copilot CLI authentication."""
    config = config or policy()
    for name, expected in config["agent_models"].items():
        path = ROOT / ".github" / "agents" / (name + ".agent.md")
        if not path.is_file():
            raise ContractError("Agent missing: " + str(path))
        contents = path.read_text(encoding="utf-8")
        if not contents.startswith("---\n") or "\n---" not in contents[4:]:
            raise ContractError("Agent missing frontmatter: " + name)
        header = contents.split("---", 2)[1]
        actual = dict(PATTERN.findall(header))
        if actual.get("model") != expected:
            raise ContractError("Model mismatch for " + name + ": " + str(actual.get("model")))
        if (actual.get("modelPolicy") or actual.get("model-policy")) != "required":
            raise ContractError("Agent model is not locked: " + name)
        if name in {"reviewer", "banking-reviewer", "cross-reviewer", "banking-analyst"}:
            if "strict-tools-list: true" not in header or "tools:" not in header:
                raise ContractError("Sensitive analyst/reviewer must be read-only: " + name)
    return {"status": "PASS", "agents_checked": len(config["agent_models"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Banking risk model planner and policy checker")
    parser.add_argument("command", choices=["route", "check"])
    parser.add_argument("--task", help="Task contract JSON file for route")
    args = parser.parse_args(argv)
    try:
        if args.command == "route":
            if not args.task:
                raise ContractError("route requires --task")
            result = resolve(load_json(args.task))
        else:
            result = check_agents()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ContractError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
