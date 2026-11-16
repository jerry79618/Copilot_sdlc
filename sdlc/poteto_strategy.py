"""Goal-first main-agent workflow selection based on Lauren Tan's pstack methods.

This module chooses *advisory* playbook/role strategies. Actual Copilot
subagents, testing tools, approvals and cross-session continuity depend on the
real host environment and must never be inferred from this recommendation.
"""
import argparse
import json
import sys
from pathlib import Path

from .contracts import ContractError, ROOT, load_json
from .mode import classify
from .pstack_bridge import MANIFEST, _source, for_playbook


UPSTREAM_FOLDER = "skills/poteto-mode/playbooks/"
ENGINEERING_PILLARS = {
    "understand": [
        "skills/how/SKILL.md", "skills/why/SKILL.md",
        "skills/recall/SKILL.md",
    ],
    "design": [
        "skills/architect/SKILL.md", "skills/arena/SKILL.md",
        "skills/interrogate/SKILL.md", "skills/principle-model-the-domain/SKILL.md",
    ],
    "execute": [
        "skills/tdd/SKILL.md", "skills/swarm/SKILL.md",
        "skills/principle-fix-root-causes/SKILL.md",
    ],
    "verify": [
        "skills/create-verification-skill/SKILL.md",
        "skills/maintain-verification-skill/SKILL.md",
        "skills/principle-prove-it-works/SKILL.md",
    ],
    "learn": [
        "skills/reflect/SKILL.md", "skills/correct/SKILL.md",
        "skills/show-me-your-work/SKILL.md",
    ],
    "communicate": [
        "skills/technical-writing/SKILL.md", "skills/unslop/SKILL.md",
    ],
}
NATIVE_MAP = {
    "feature": "feature",
    "bug-fix": "bug-fix",
    "verification": None,  # Original verification Skills, no invented Playbook.
    "investigation": "investigation",
    "refactor": "refactoring",
    "performance": "perf-issue",
    "review": None,
    "figure-it-out": None,  # Original figure-it-out Skill.
    "prototype": "prototype",
    "skill-eval": "eval",
    "multi-phase": "multi-phase-plan",
}
PR_ONLY = {"babysit", "shipping", "autopilot-full", "autopilot-stack", "opening-a-pr"}
HOST_DEPENDENT = {"orchestrate", "autonomous-run", "babysit", "shipping",
                  "autopilot-full", "autopilot-stack", "session-pickup"}
SAFETY_SENSITIVE = {"shipping", "autopilot-full"}
PROGRAM_MARKERS = (
    "整個專案", "整套系統", "多個pr", "多個 pr", "長期專案",
    "長期計畫", "跨多個repo", "跨多個 repo", "whole project",
    "multi-day", "program of work", "many prs", "dozens of",
)
AUTONOMOUS_MARKERS = ("持續到完成", "執行直到完成", "run until done",
                      "until green", "until fixed")
SHIP_MARKERS = ("合併pr", "合併 pr", "merge pr", "merge pull request",
                "ship this", "land this pr")
PR_STATUS_MARKERS = ("pr 狀態", "pr 審查", "檢查 pr", "check pr status",
                     "pr checks", "babysit pr", "review comments")
REVIEW_MARKERS = ("code review", "審查pr", "審查 pr")
SCOPE_MARKERS = ("跨系統", "多個模組", "多個服務", "跨服務",
                 "multiple modules", "across services", "cross-system")
UNSAFE = (
    "Do not assume subagents or event subscriptions ran.",
    "Do not invoke Cursor-only tools, model overrides, /loop, or Task API.",
    "Never merge, deploy, write production data, or bypass bank approval from a suggested route.",
    "Runtime PASS requires actual approved adapter and evidence; demo is not production proof.",
)


def source_playbooks():
    """Return pinned upstream Playbooks, never auto-register them as CLI commands."""
    tracked = load_json(MANIFEST)["files"]
    names = sorted(
        path[len(UPSTREAM_FOLDER):-3] for path in tracked
        if path.startswith(UPSTREAM_FOLDER) and path.endswith(".md")
    )
    if not names:
        raise ContractError("Upstream pstack Playbook catalog is missing")
    for name in names:
        _source(UPSTREAM_FOLDER + name + ".md")
    return names


def pillar_sources():
    tracked = load_json(MANIFEST)["files"]
    result = {}
    for pillar, paths in ENGINEERING_PILLARS.items():
        if not all(p in tracked for p in paths):
            raise ContractError("Original pstack engineering reference missing: " + pillar)
        result[pillar] = [{"relative": p, "path": str(_source(p))} for p in paths]
    return result


def _pick_original(goal, default):
    text = goal.casefold()
    if any(s in text for s in SHIP_MARKERS):
        return "shipping", "explicit PR shipping goal"
    if any(s in text for s in PR_STATUS_MARKERS):
        return "babysit", "PR lifecycle goal"
    if any(s in text for s in PROGRAM_MARKERS):
        return "orchestrate", "explicit large ongoing program goal"
    if any(s in text for s in AUTONOMOUS_MARKERS):
        return "autonomous-run", "explicit run-to-predicate goal"
    if any(s in text for s in ("多階段", "多個階段", "multi-phase", "multiple phases")):
        return "multi-phase-plan", "multiple phase goal"
    if any(s in text for s in ("原型", "prototype")):
        return "prototype", "prototype goal"
    if any(s in text for s in ("效能", "performance", "latency")):
        return "perf-issue", "performance goal"
    if any(s in text for s in ("程式重構", "重構", "refactor")):
        return "refactoring", "refactor goal"
    if any(s in text for s in ("程式漏洞調查", "runtime forensics", "追蹤執行異常")):
        return "runtime-forensics", "forensics goal"
    if any(s in text for s in ("開立 pr", "建立 pr", "open a pr", "opening a pr")):
        return "opening-a-pr", "PR drafting goal"
    if any(s in text for s in REVIEW_MARKERS):
        return None, "review performed in main-agent flow"
    return default, "local Playbook aligned to upstream"


def propose(goal, project_root=".", upstream_playbook=None):
    if not isinstance(goal, str) or not goal.strip():
        raise ContractError("A concrete goal is required for Poteto Mode")
    root = ROOT if project_root is None else Path(project_root).expanduser().resolve()
    if not root.is_dir():
        raise ContractError("Target project root does not exist: " + str(root))
    decision = classify(goal)
    local = decision["playbook"]
    original, reason = _pick_original(goal, NATIVE_MAP[local])
    available = source_playbooks()
    if upstream_playbook:
        if upstream_playbook not in available:
            raise ContractError("Unknown original pstack Playbook: " + upstream_playbook)
        original, reason = upstream_playbook, "explicit, original-source selection"
    if original and original not in available:
        raise ContractError("Selected upstream Playbook not found in pinned source: " + original)

    # The main session is ALWAYS responsible for the workflow. A dedicated
    # coordinator is only useful for the original "Orchestrate" program strategy.
    if original == "orchestrate":
        shape = "main-agent-program-coordinator"
        delegation = "workers-per-independent-PR-when-host-authorizes"
    elif original in {"feature", "bug-fix", "refactoring", "perf-issue",
                      "multi-phase-plan"}:
        shape = "main-agent-leads"
        delegation = "optional-specialists-for-independent-work"
    else:
        shape = "main-agent-direct"
        delegation = "none-by-default"

    detected_scope = "complex" if any(s in goal.casefold() for s in SCOPE_MARKERS) else "unspecified"
    return {
        "mode": "POTETO_MAIN_AGENT",
        "owner": "current-copilot-session-main-agent",
        "dedicated_orchestrator_required": False,
        "local_bank_playbook": local,
        "local_routing": decision,
        "upstream_playbook": original,
        "upstream_source_path": (str(_source(UPSTREAM_FOLDER + original + ".md"))
                                 if original else None),
        "selection_reason": reason,
        "coordination": shape,
        "delegation": delegation,
        "scope_hint": detected_scope,
        "main_agent_may_override_selection": True,
        "override_requirement": "Record the observed project-specific reason and preserve applicable bank gates",
        "source_method_guidance": for_playbook(local),
        "engineering_pillars": pillar_sources(),
        "host_status": ("HOST_CAPABILITY_REQUIRED" if original in HOST_DEPENDENT
                        else "SUGGESTION_ONLY"),
        "execution_authorized": False,
        "human_approval_for_merge": True,
        "verified_work": False,
        "risk_constraints": list(UNSAFE),
        "note": ("Playbook/source discovery and delegation strategy, not a real "
                 "agent spawn, CI result, bank permission, or release approval."),
        "project_root": str(root),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only main-agent Poteto strategy")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--upstream-playbook", help="Select any pinned original Playbook explicitly")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(propose(args.goal, args.project_root, args.upstream_playbook),
                         ensure_ascii=False, indent=2))
        return 0
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
