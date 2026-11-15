"""A pstack-inspired, Copilot-compatible front door with auditable playbook worklists.

This module chooses playbooks and records evidence. It does not run an LLM,
invoke other skills, edit product code, connect to services, or merge PRs.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ContractError, ROOT, load_json, validate_task

VALID_GATES = {"G1", "G2", "G3", "G4", "G5"}
VALID_SKILLS = {"task-routing", "development", "verification", "cross-system-data", "failure-analysis"}
INTENT_DEFAULTS = {"development": "feature", "verification": "verification", "investigation": "investigation"}
TERMINAL = {"READY_FOR_REVIEW", "COMPLETE"}
MUTATING_PLAYBOOKS = {"feature", "bug-fix", "refactor", "performance"}
READONLY_PLAYBOOKS = {"verification", "investigation", "review", "figure-it-out"}
IDENT = re.compile(r"^[a-z][a-z0-9-]*$")

# This is a conservative suggestion layer, not a natural-language guarantee.
KEYWORDS = [
    ("review", ("code review", "review pr", "pull request review", "審查程式", "程式審查")),
    ("performance", ("performance", "latency", "bottleneck", "效能", "效能改善", "變慢", "慢速")),
    ("refactor", ("refactor", "restructure", "重構", "重新整理程式架構")),
    ("bug-fix", ("bug", "fix error", "fix the", "repair", "故障", "修復", "修正錯誤", "重複通知", "異常")),
    ("feature", ("new feature", "implement", "create endpoint", "add an", "新增", "開發", "實作", "建立功能")),
    ("verification", ("verify", "regression test", "testing only", "test only", "測試", "驗證", "回歸", "確認流程")),
    ("investigation", ("investigate", "explain", "how does", "why does", "調查", "分析", "為什麼", "了解")),
]
READ_ONLY = ("read-only", "readonly", "do not change code", "don't change code",
             "without modifying", "不要修改", "只調查", "只分析", "不改程式", "先調查")


def catalog():
    data = load_json(ROOT / "playbooks" / "catalog.json")
    if data.get("schema_version") != 1 or not isinstance(data.get("playbooks"), list):
        raise ContractError("Unsupported playbook catalog")
    playbooks = {}
    for book in data["playbooks"]:
        ident = book.get("id")
        if not isinstance(ident, str) or not IDENT.fullmatch(ident) or ident in playbooks:
            raise ContractError("Invalid or duplicated playbook id")
        if book.get("intent") not in INTENT_DEFAULTS:
            raise ContractError("Invalid playbook intent: " + ident)
        if (ident in MUTATING_PLAYBOOKS) != (book["intent"] == "development"):
            raise ContractError("Inconsistent mutating playbook: " + ident)
        steps = book.get("stages")
        if not isinstance(steps, list) or not steps:
            raise ContractError("Empty playbook: " + ident)
        seen = set()
        for step in steps:
            sid = step.get("id")
            if not isinstance(sid, str) or not IDENT.fullmatch(sid) or sid in seen:
                raise ContractError("Invalid or duplicated stage in " + ident)
            seen.add(sid)
            if not isinstance(step.get("title"), str) or not step["title"].strip():
                raise ContractError("Missing stage title")
            skills = step.get("skills")
            if not isinstance(skills, list) or not skills or any(s not in VALID_SKILLS for s in skills):
                raise ContractError("Unknown skill in " + ident + ":" + sid)
            if step.get("gate") and step["gate"] not in VALID_GATES:
                raise ContractError("Invalid gate")
            if step.get("gate") and step.get("optional"):
                raise ContractError("Mandatory gates cannot be skipped")
        playbooks[ident] = book
    if set(playbooks) != MUTATING_PLAYBOOKS | READONLY_PLAYBOOKS:
        raise ContractError("Catalog does not match supported routes")
    return playbooks


def classify(goal, intent=None, override=None):
    """Recommend a playbook. Explicit intent and read-only constraints take precedence."""
    books = catalog()
    if not isinstance(goal, str) or not goal.strip():
        raise ContractError("A nonempty goal is required")
    if intent is not None and intent not in INTENT_DEFAULTS:
        raise ContractError("Unknown intent")
    text = goal.casefold()
    read_only = any(s in text for s in READ_ONLY)
    matched = [(book, word) for book, words in KEYWORDS for word in words if word in text]
    if override:
        if override not in books:
            raise ContractError("Unknown playbook: " + override)
        chosen, reason = override, "explicit playbook"
    elif read_only:
        chosen, reason = "investigation", "explicit read-only constraint"
    elif matched:
        chosen, reason = matched[0][0], "keyword: " + matched[0][1]
    else:
        chosen, reason = INTENT_DEFAULTS.get(intent, "figure-it-out"), "no unique task signal"

    if intent:
        if books[chosen]["intent"] != intent:
            # A verified user/contract intent wins over heuristic routing.
            if override:
                raise ContractError("Playbook " + chosen + " conflicts with declared intent " + intent)
            chosen, reason = INTENT_DEFAULTS[intent], "declared intent overrides keywords"
    confidence = ("explicit" if override or read_only or reason.startswith("declared")
                  else "suggested" if matched else "needs-review")
    return {
        "playbook": chosen, "intent": books[chosen]["intent"],
        "reason": reason, "confidence": confidence,
        "requires_confirmation": confidence == "needs-review",
        "cross_system_hint": any(s in text for s in ("跨系統", "cross-system", "another system", "其他系統")),
        "note": "Routing suggestion only. Copilot should verify the Task Contract and user permissions.",
    }


def choose_for_task(task, override=None):
    validate_task(task)
    result = classify(task["goal"], task["intent"], override or task.get("playbook"))
    if result["intent"] != task["intent"]:
        raise ContractError("Selected playbook conflicts with Task Contract")
    return result


def make_worklist(task, override=None):
    chosen = choose_for_task(task, override)
    book = catalog()[chosen["playbook"]]
    digest = hashlib.sha256(json.dumps(task, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return {
        "schema_version": 1, "task_id": task["id"],
        "task_sha256": digest, "intent": task["intent"],
        "environment": task["environment"], "playbook": book["id"],
        "route_reason": chosen["reason"], "status": "ACTIVE",
        "approval_required": task.get("approval_required", False) or task["risk"] == "high",
        "limitations": [
            "Worklist records completion; it does not execute AI Skills automatically.",
            "G4 verifies only sandbox evidence for now; production integrations are unavailable.",
        ],
        "stages": [
            {"id": s["id"], "title": s["title"], "skills": s["skills"],
             "gate": s.get("gate"), "optional": s.get("optional", False),
             "status": "PENDING", "evidence": None, "reason": None}
            for s in book["stages"]
        ],
    }


def next_stage(worklist):
    return next((s for s in worklist["stages"] if s["status"] in {"PENDING", "BLOCKED"}), None)


def update_worklist(worklist, stage_id, outcome, evidence_path=None, reason=None):
    if worklist["status"] in TERMINAL:
        raise ContractError("Worklist is already finished")
    active = next_stage(worklist)
    if active is None or active["id"] != stage_id:
        raise ContractError("Stages must complete in order; expected " + str(active and active["id"]))
    if outcome not in {"PASS", "BLOCKED", "SKIP"}:
        raise ContractError("Outcome must be PASS, BLOCKED or SKIP")
    if outcome == "SKIP" and (not active["optional"] or not reason):
        raise ContractError("Only optional stages may be skipped, with a reason")
    if outcome == "BLOCKED" and not reason:
        raise ContractError("A blocked stage requires a specific reason")
    if outcome == "PASS":
        if not evidence_path:
            raise ContractError("Passing a stage requires a real evidence file")
        source = Path(evidence_path).resolve()
        if not source.is_file():
            raise ContractError("Evidence file does not exist: " + str(source))
        if active["gate"] == "G4":
            proof = load_json(source)
            if proof.get("task_id") != worklist["task_id"] or proof.get("environment") != worklist["environment"]:
                raise ContractError("Verification evidence does not match task/environment")
            if proof.get("status") != "PASS":
                raise ContractError("Verification evidence must contain PASS")
            if worklist["environment"] != "demo" or proof.get("classification") != "DEMO_VERIFIED":
                raise ContractError("Real-system verification adapters are not implemented")
        active["evidence"] = str(source)
        active["reason"] = None
    else:
        active["reason"] = reason
        active["evidence"] = str(Path(evidence_path).resolve()) if evidence_path else None
    active["status"] = {"PASS": "DONE", "BLOCKED": "BLOCKED", "SKIP": "SKIPPED"}[outcome]
    worklist["status"] = "BLOCKED" if outcome == "BLOCKED" else "ACTIVE"
    if next_stage(worklist) is None:
        worklist["status"] = ("READY_FOR_REVIEW" if worklist["intent"] == "development" else "COMPLETE")
    return worklist


def save_json(path, payload, exclusive=False):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("x" if exclusive else "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="Copilot SDLC mode: route, start, worklist, advance")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("catalog", help="Show available playbooks and stages")
    c.add_argument("--id", help="Optional playbook id")
    r = sub.add_parser("route", help="Recommend playbook from short natural-language goal")
    r.add_argument("--goal", required=True)
    r.add_argument("--intent", choices=list(INTENT_DEFAULTS))
    r.add_argument("--playbook")
    s = sub.add_parser("start", help="Create a persistent ordered worklist from a Task Contract")
    s.add_argument("--task", required=True)
    s.add_argument("--playbook")
    s.add_argument("--output-dir", default="artifacts")
    v = sub.add_parser("status", help="Display the next required stage")
    v.add_argument("--run", required=True)
    a = sub.add_parser("advance", help="Record completion/skip/block with evidence and enforce order")
    a.add_argument("--run", required=True)
    a.add_argument("--stage", required=True)
    a.add_argument("--outcome", required=True, choices=["PASS", "BLOCKED", "SKIP"])
    a.add_argument("--evidence")
    a.add_argument("--reason")
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            books = catalog()
            result = books[args.id] if args.id else [{"id": b["id"], "intent": b["intent"], "description": b["description"]} for b in books.values()]
        elif args.command == "route":
            result = classify(args.goal, args.intent, args.playbook)
        elif args.command == "start":
            task = load_json(args.task)
            run = make_worklist(task, args.playbook)
            now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            path = Path(args.output_dir) / ("worklist-" + task["id"] + "-" + now + ".json")
            save_json(path, run, exclusive=True)
            result = {"worklist": str(path), "playbook": run["playbook"],
                      "status": run["status"], "next": next_stage(run)}
        elif args.command == "status":
            worklist = load_json(args.run)
            result = {"task_id": worklist["task_id"], "playbook": worklist["playbook"],
                      "status": worklist["status"], "next": next_stage(worklist),
                      "stages": worklist["stages"]}
        else:
            worklist = load_json(args.run)
            update_worklist(worklist, args.stage, args.outcome, args.evidence, args.reason)
            save_json(args.run, worklist)
            result = {"task_id": worklist["task_id"], "playbook": worklist["playbook"],
                      "status": worklist["status"], "next": next_stage(worklist)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ContractError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(run_cli())
