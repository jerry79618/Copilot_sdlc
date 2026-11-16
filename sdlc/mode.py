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

from .contracts import ContractError, ROOT, load_json, validate_task, test_changes_allowed
from .model_policy import resolve as resolve_model_policy

VALID_GATES = {"G1", "G2", "G3", "G4", "G5"}
VALID_SKILLS = {"task-routing", "development", "verification", "cross-system-data", "failure-analysis", "cucumber-authoring", "feature-map-discovery", "skill-eval", "reflection"}
INTENT_DEFAULTS = {"development": "feature", "verification": "verification", "investigation": "investigation"}
TERMINAL = {"READY_FOR_REVIEW", "COMPLETE"}
MUTATING_PLAYBOOKS = {"feature", "bug-fix", "refactor", "performance", "prototype"}
READONLY_PLAYBOOKS = {"verification", "investigation", "review", "figure-it-out", "skill-eval", "multi-phase"}
IDENT = re.compile(r"^[a-z][a-z0-9-]*$")

# This is a conservative suggestion layer, not a natural-language guarantee.
KEYWORDS = [
    ("skill-eval", ("skill eval", "evaluate skill", "eval a skill", "技能評估", "技能測試")),
    ("multi-phase", ("multi-phase", "multi phase", "多階段", "階段規劃", "多個 pr")),
    ("prototype", ("prototype", "兩種方案", "兩個方案", "原型", "概念驗證")),
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
        # A request to write tests without product edits is still verification.
        test_request = any(s in text for s in (
            "測試", "驗證", "回歸", "cucumber", "junit", "test"
        ))
        investigation_only = any(s in text for s in (
            "先調查", "只調查", "只分析", "investigate only", "analysis only"
        ))
        chosen = "verification" if test_request and not investigation_only else "investigation"
        reason = "test-only constraint" if chosen == "verification" else "explicit read-only constraint"
    elif re.search(r"(修正|修復|排除|解決).*(錯誤|異常|問題|失敗)", text):
        chosen, reason = "bug-fix", "Chinese bug-repair intent"
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
                  else "suggested" if matched or reason == "Chinese bug-repair intent" else "needs-review")
    return {
        "playbook": chosen, "intent": books[chosen]["intent"],
        "reason": reason, "confidence": confidence,
        "requires_confirmation": confidence == "needs-review",
        "cross_system_hint": any(s in text for s in ("跨系統", "cross-system", "another system", "其他系統")),
        "note": "Routing suggestion only. Copilot should verify the Task Contract and user permissions.",
    }


def choose_for_task(task, override=None, project_root=ROOT):
    validate_task(task, project_root=project_root)
    result = classify(task["goal"], task["intent"], override or task.get("playbook"))
    if result["intent"] != task["intent"]:
        raise ContractError("Selected playbook conflicts with Task Contract")
    return result


def make_worklist(task, override=None, project_root=ROOT):
    chosen = choose_for_task(task, override, project_root=project_root)
    book = catalog()[chosen["playbook"]]
    model_routing = resolve_model_policy(task, project_root=project_root)
    effective_risk = model_routing["effective_risk"]
    evidence_gates = set(model_routing["required_evidence_gates"])
    full_evidence = model_routing["all_stage_evidence"]
    digest = hashlib.sha256(json.dumps(task, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return {
        "schema_version": 1, "task_id": task["id"],
        "task_sha256": digest, "intent": task["intent"],
        "project_root": str(Path(project_root).resolve()),
        "environment": task["environment"], "playbook": book["id"],
        "route_reason": chosen["reason"], "status": "ACTIVE",
        "approval_required": model_routing["human_approval_required"],
        "model_routing": model_routing,
        "workflow_intensity": {"low": "lean", "medium": "standard", "high": "regulated"}[effective_risk],
        "test_code_changes_allowed": test_changes_allowed(task, project_root=project_root),
        "limitations": [
            "Non-required stages are progress records, not independently verified evidence.",
            "Worklist records completion; it does not execute AI Skills automatically.",
            "G4 verifies only sandbox evidence for now; production integrations are unavailable.",
        ],
        "stages": [
            {"id": s["id"], "title": s["title"], "skills": s["skills"],
             "gate": s.get("gate"), "optional": s.get("optional", False),
             "evidence_required": (
                 full_evidence or s.get("gate") in evidence_gates
             ) and not s.get("optional", False),
             "status": "PENDING", "evidence": None, "reason": None,
             "evidence_sha256": None, "updated_at": None}
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
        required = active.get("evidence_required", True)
        if required and not evidence_path:
            raise ContractError(
                "This risk/gate requires a real evidence file: " + active["id"]
            )
        if evidence_path:
            source = Path(evidence_path).resolve()
            if not source.is_file():
                raise ContractError("Evidence file does not exist: " + str(source))
            if active["gate"] == "G4":
                proof = load_json(source)
                if (proof.get("task_id") != worklist["task_id"] or
                        proof.get("environment") != worklist["environment"]):
                    raise ContractError("Verification evidence does not match task/environment")
                if proof.get("status") != "PASS":
                    raise ContractError("Verification evidence must contain PASS")
                if (worklist["environment"] != "demo" or
                        Path(worklist.get("project_root", ROOT)).resolve() != ROOT.resolve() or
                        proof.get("classification") not in {"DEMO_VERIFIED", "CUCUMBER_DEMO_VERIFIED"}):
                    raise ContractError("Real-system verification adapters are not implemented")
                if (proof.get("classification") == "CUCUMBER_DEMO_VERIFIED" and
                        (proof.get("runner") != "cucumber-jvm" or
                         not proof.get("feature_map") or not proof.get("checks"))):
                    raise ContractError("Incomplete Cucumber verification evidence")
            active["evidence"] = str(source)
            active["evidence_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        else:
            active["evidence"] = None
            active["evidence_sha256"] = None
        active["reason"] = None
    else:
        active["reason"] = reason
        active["evidence"] = str(Path(evidence_path).resolve()) if evidence_path else None
    active["updated_at"] = datetime.now(timezone.utc).isoformat()
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
    s.add_argument("--output-dir", help="Worklist directory; defaults to target artifacts/sdlc for external projects")
    s.add_argument("--project-root", default=str(ROOT), help="Root containing task scenarios; default framework demo")
    q = sub.add_parser("checkpoint", help="Read-only progress snapshot for pause/resume")
    q.add_argument("--run", required=True)
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
            run = make_worklist(task, args.playbook, project_root=args.project_root)
            now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            target_root = Path(args.project_root).resolve()
            output_root = (Path(args.output_dir) if args.output_dir else
                           (target_root / "artifacts" / "sdlc" if target_root != ROOT.resolve()
                            else Path("artifacts")))
            path = output_root / ("worklist-" + task["id"] + "-" + now + ".json")
            save_json(path, run, exclusive=True)
            result = {"worklist": str(path), "playbook": run["playbook"],
                      "status": run["status"], "next": next_stage(run)}
        elif args.command == "checkpoint":
            worklist = load_json(args.run)
            result = {
                "task_id": worklist["task_id"], "playbook": worklist["playbook"],
                "status": worklist["status"], "next": next_stage(worklist),
                "progress": {state: sum(s["status"] == state for s in worklist["stages"])
                             for state in ("DONE", "PENDING", "SKIPPED", "BLOCKED")},
                "proof_files": [
                    {"stage": s["id"], "path": s["evidence"],
                     "sha256": s.get("evidence_sha256")}
                    for s in worklist["stages"] if s["evidence"]
                ],
                "limitations": worklist.get("limitations", []),
            }
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
