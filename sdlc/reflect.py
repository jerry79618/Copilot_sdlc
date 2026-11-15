"""Produce a human-reviewable postmortem draft; never modify enforced rules automatically."""
import argparse
import json
import sys
from pathlib import Path

from .contracts import ContractError, ROOT, load_json


def render(run):
    if not isinstance(run.get("stages"), list) or not run.get("task_id"):
        raise ContractError("Not a recognized SDLC worklist")
    lines = [
        "# SDLC Reflection Draft — " + run["task_id"], "",
        "> GENERATED DRAFT. Review and supply actual observations before changing Skills.",
        "", "## Task and outcome",
        "- Playbook: " + str(run.get("playbook")),
        "- Worklist state: " + str(run.get("status")),
        "- Environment: " + str(run.get("environment")),
        "", "## Verified stage ledger (not independent attestation)",
    ]
    for step in run["stages"]:
        lines.append("- " + step["id"] + ": " + step["status"] +
                     (" — " + step.get("reason", "") if step.get("reason") else "") +
                     (" — evidence " + step["evidence"] if step.get("evidence") else ""))
    lines.extend([
        "", "## Root-cause observations (human / agent fill in)",
        "- What failed, and which evidence proves it?",
        "- Was the source problem in architecture, type/schema, lint/CI, test, fixture or docs?",
        "- What user-visible behavior actually changed?",
        "", "## Proposed durable improvements (do NOT auto-edit)",
        "- Prefer design/schema/code-enforced fixes; next lint or CI; then tests; docs last.",
        "- Specify one regression case that would have caught this issue before release.",
        "- Add a test to evals/ if the Agent routing or Skill decision was wrong.",
        "- Re-run deterministic tests AND a real application verification before acceptance.",
        "", "## Approval / safety",
        "- Name owner, reviewers and next authorization; nothing is merged or deployed here.",
        "- Do not copy customer data, credentials or raw transactions into this document.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Generate reflection without altering source")
    p.add_argument("--run", required=True)
    p.add_argument("--output", default="artifacts/reflection-draft.md")
    args = p.parse_args(argv)
    try:
        run = load_json(args.run)
        target = Path(args.output).resolve()
        if not target.is_relative_to(ROOT):
            raise ContractError("Reflection must be written inside repository")
        if target.exists():
            raise ContractError("Refusing to overwrite reflection: " + str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(run), encoding="utf-8")
        print(json.dumps({"status": "DRAFT", "output": str(target)}, ensure_ascii=False))
        return 0
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
