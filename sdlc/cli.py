"""python -m sdlc.cli {validate|plan|verify} --task ..."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ContractError, ROOT, load_json, repo_path, validate_scenario, validate_task
from .workflow import plan
from .verification import verify

EXIT_CODES = {"PASS": 0, "FAIL": 1, "BLOCKED": 2, "ERROR": 3}


def run(argv=None):
    parser = argparse.ArgumentParser(description="Enterprise AI SDLC v0.1 sandbox runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "plan", "verify"):
        p = sub.add_parser(command)
        p.add_argument("--task", required=True, help="Task Contract JSON file")
        p.add_argument("--project-root", default=str(ROOT), help="Task scenario root (framework demo by default)")
        if command == "verify":
            p.add_argument("--output-dir", default="artifacts", help="Evidence output directory")
    args = parser.parse_args(argv)
    try:
        task = validate_task(load_json(args.task), project_root=args.project_root)
        if args.command == "validate":
            if task.get("scenario"):
                validate_scenario(load_json(repo_path(task["scenario"], "scenarios", args.project_root)))
            result = {"status": "PASS", "task_id": task["id"], "message": "Contract and scenario are valid"}
        elif args.command == "plan":
            result = plan(task, project_root=args.project_root)
        else:
            result = verify(task, project_root=args.project_root)
            # Keep evidence inside the active working directory, but never overwrite existing runs.
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            path = out / (task["id"] + "-" + ts + ".json")
            with path.open("x", encoding="utf-8") as fp:
                json.dump(result, fp, indent=2, ensure_ascii=False)
                fp.write("\n")
            result["evidence_file"] = str(path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return EXIT_CODES.get(result.get("status", "PASS"), 3)
    except (ContractError, ValueError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return EXIT_CODES["ERROR"]


if __name__ == "__main__":
    raise SystemExit(run())
