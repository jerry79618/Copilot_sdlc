"""Portable, read-only SDLC CLI bootstrap for any target repository.

This checks the real framework catalog and user-level shadowing before an
operator starts Copilot. It does not run agents or prove runtime verification.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from .contracts import ContractError, ROOT
from .mode import catalog, classify
from .project_context import prepare
from .pstack_bridge import for_playbook, verify_sources


def _root(project_root):
    project = Path(project_root).expanduser().resolve()
    if not project.is_dir():
        raise ContractError("Project directory does not exist: " + str(project))
    return project


def _copilot_home():
    return Path(os.environ.get("COPILOT_HOME") or (Path.home() / ".copilot")).expanduser().resolve()


def _shadow_conflicts(home):
    """Report stale local copies that can shadow the framework's agent/skills."""
    conflicts = []
    local_agent = home / "agents" / "orchestrator.agent.md"
    canonical_agent = ROOT / ".github" / "agents" / "orchestrator.agent.md"
    if not canonical_agent.is_file():
        raise ContractError("Framework orchestrator agent is missing")
    if local_agent.is_file() and local_agent.read_bytes() != canonical_agent.read_bytes():
        conflicts.append({
            "kind": "agent", "path": str(local_agent),
            "resolution": "Back up and update this user agent, or launch with -Isolated.",
        })
    skill_root = ROOT / ".github" / "skills"
    if not skill_root.is_dir():
        raise ContractError("Framework skills directory is missing")
    for skill in sorted(skill_root.glob("*/SKILL.md")):
        for location in (home / "skills" / skill.parent.name / "SKILL.md",
                         Path.home() / ".agents" / "skills" / skill.parent.name / "SKILL.md"):
            if location.is_file() and location.read_bytes() != skill.read_bytes():
                conflicts.append({
                    "kind": "skill", "name": skill.parent.name, "path": str(location),
                    "resolution": "Back up and remove/update the stale SDLC skill copy, or use a separate Copilot profile.",
                })
    return conflicts


def _project_shadow_conflicts(project):
    """Report project-local files that may override central SDLC definitions."""
    if project == ROOT.resolve():
        return []
    conflicts = []
    for relative, kind in (
        (".github/agents/orchestrator.agent.md", "agent"),
        (".github/skills/poteto-mode/SKILL.md", "skill"),
        (".github/skills/sdlc-mode/SKILL.md", "skill"),
    ):
        local = project / relative
        framework = ROOT / relative
        if local.is_file() and framework.is_file() and local.read_bytes() != framework.read_bytes():
            conflicts.append({
                "kind": kind, "path": str(local),
                "resolution": "Review this project's SDLC override, or use the matching framework version.",
            })
    return conflicts


def _source_inventory(project, home):
    results = []
    for name, relative, user_relative in (
        ("orchestrator", ".github/agents/orchestrator.agent.md", "agents/orchestrator.agent.md"),
        ("poteto-mode", ".github/skills/poteto-mode/SKILL.md", "skills/poteto-mode/SKILL.md"),
        ("sdlc-mode", ".github/skills/sdlc-mode/SKILL.md", "skills/sdlc-mode/SKILL.md"),
    ):
        options = (("framework", ROOT / relative),
                   ("user", home / user_relative),
                   ("project", project / relative))
        results.append({
            "name": name,
            "available_sources": [{"scope": scope, "path": str(p)}
                                  for scope, p in options if p.is_file()],
            "effective_source": "NOT_RUNTIME_VERIFIED",
        })
    return results


def doctor(project_root=".", copilot_home=None):
    project = _root(project_root)
    books = catalog()
    if not books:
        raise ContractError("Framework Playbook catalog is empty")
    home = Path(copilot_home).expanduser().resolve() if copilot_home else _copilot_home()
    conflicts = _shadow_conflicts(home) + _project_shadow_conflicts(project)
    canonical_mode = ROOT / ".github" / "skills" / "poteto-mode" / "SKILL.md"
    if not canonical_mode.is_file():
        raise ContractError("Canonical Poteto Mode Skill is missing: " + str(canonical_mode))
    bridge_health = verify_sources()
    return {
        "status": "BLOCKED" if conflicts else "READY",
        "project_root": str(project),
        "framework_root": str(ROOT.resolve()),
        "catalog_path": str((ROOT / "playbooks" / "catalog.json").resolve()),
        "playbook_count": len(books),
        "playbook_ids": list(books),
        "mode": {"name": "poteto-mode", "kind": "copilot-agent-skill",
                 "skill_path": str(canonical_mode.resolve()),
                 "agent": "orchestrator", "legacy_skill": "sdlc-mode"},
        "copilot_home": str(home),
        "shadow_conflicts": conflicts,
        "source_candidates": _source_inventory(project, home),
        "pstack_vendor_health": bridge_health,
        "note": "Static sources only; actual loaded Agent/Skill, CLI model permissions and delegation are NOT verified.",
    }


def route(goal, project_root="."):
    project = _root(project_root)
    books = catalog()
    decision = classify(goal)
    selected = books.get(decision["playbook"])
    if selected is None:
        raise ContractError("Playbook is absent from catalog: " + decision["playbook"])
    skill_dir = ROOT / ".github" / "skills"
    stages = []
    for stage in selected["stages"]:
        stages.append({
            "id": stage["id"], "title": stage["title"],
            "gate": stage.get("gate"),
            "optional": stage.get("optional", False),
            "skills": [{
                "name": name,
                "path": str((skill_dir / name / "SKILL.md").resolve()),
            } for name in stage.get("skills", [])],
        })
    return {
        "status": "ROUTED",
        "project_root": str(project),
        "framework_root": str(ROOT.resolve()),
        "catalog_path": str((ROOT / "playbooks" / "catalog.json").resolve()),
        "decision": decision,
        "mode": {"name": "poteto-mode", "kind": "copilot-agent-skill",
                 "skill_path": str((ROOT / ".github" / "skills" / "poteto-mode" / "SKILL.md").resolve()),
                 "agent": "orchestrator"},
        "pstack_reference": for_playbook(decision["playbook"]),
        "playbook_description": selected.get("description", ""),
        "stages": stages,
        "note": "Route is a hint, not permission to edit or proof that agents executed.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run SDLC bootstrap checks and real Playbook lookup")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "route", "prepare"):
        command = commands.add_parser(name)
        command.add_argument("--project-root", default=".")
        if name in {"route", "prepare"}:
            command.add_argument("--goal", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            result = doctor(args.project_root)
        elif args.command == "route":
            result = route(args.goal, args.project_root)
        else:
            result = prepare(args.goal, args.project_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("status") == "BLOCKED" else 0
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
