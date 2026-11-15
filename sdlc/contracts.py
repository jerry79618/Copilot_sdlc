"""Strict task/scenario input checks. No network or side effects."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTENTS = {"development", "verification", "investigation"}
RISKS = {"low", "medium", "high"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,63}$")


class ContractError(ValueError):
    pass


def load_json(path):
    try:
        with Path(path).open(encoding="utf-8") as fp:
            return json.load(fp)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("Unable to read JSON from " + str(path) + ": " + str(exc)) from exc


def repo_path(relative, folder):
    """Allow only repository-relative files under a trusted directory."""
    if not isinstance(relative, str) or not relative:
        raise ContractError("A repository-relative file path is required")
    target = (ROOT / relative).resolve()
    safe_root = (ROOT / folder).resolve()
    if not target.is_relative_to(safe_root):
        raise ContractError("File must be under " + folder + ": " + relative)
    return target


def _non_empty_strings(value):
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def validate_task(task):
    if not isinstance(task, dict):
        raise ContractError("Task must be a JSON object")
    if not isinstance(task.get("id"), str) or not ID_RE.fullmatch(task["id"]):
        raise ContractError("Task id must be 2-64 safe characters")
    if not isinstance(task.get("goal"), str) or not task["goal"].strip():
        raise ContractError("Task goal is required")
    if task.get("intent") not in INTENTS:
        raise ContractError("Task intent must be development, verification or investigation")
    if not _non_empty_strings(task.get("acceptance_criteria")):
        raise ContractError("At least one acceptance criterion is required")
    if not _non_empty_strings(task.get("systems")):
        raise ContractError("At least one system is required")
    if task.get("risk") not in RISKS:
        raise ContractError("Risk must be low, medium or high")
    if task.get("environment") not in {"demo", "staging", "test"}:
        raise ContractError("Environment must be demo, staging or test")
    if type(task.get("allow_code_changes")) is not bool:
        raise ContractError("allow_code_changes must be boolean")
    if task["intent"] in {"verification", "investigation"} and task["allow_code_changes"]:
        raise ContractError("Non-development tasks cannot allow product code changes")
    if task["intent"] == "development" and not task["allow_code_changes"]:
        raise ContractError("Development task must explicitly allow code changes")
    scenario = task.get("scenario")
    if task["intent"] != "investigation" and not scenario:
        raise ContractError("Development and verification tasks need a scenario")
    if scenario:
        repo_path(scenario, "scenarios")
    if "approval_required" in task and type(task["approval_required"]) is not bool:
        raise ContractError("approval_required must be boolean")
    return task


def validate_scenario(scenario):
    if not isinstance(scenario, dict) or not isinstance(scenario.get("id"), str):
        raise ContractError("Scenario id is required")
    if not _non_empty_strings(scenario.get("systems")):
        raise ContractError("Scenario systems are required")
    steps = scenario.get("steps")
    checks = scenario.get("checks")
    if not isinstance(steps, list) or not steps:
        raise ContractError("Scenario must include execution steps")
    if not isinstance(checks, list) or not checks:
        raise ContractError("Scenario must include verification checks")
    known = set()
    for step in steps:
        if not isinstance(step, dict):
            raise ContractError("Steps must be objects")
        ident = step.get("id")
        if not isinstance(ident, str) or not ID_RE.fullmatch(ident) or ident in known:
            raise ContractError("Step id is invalid or duplicated")
        known.add(ident)
        if step.get("system") not in scenario["systems"]:
            raise ContractError("Step uses an unregistered system: " + ident)
        if not isinstance(step.get("operation"), str) or not step["operation"]:
            raise ContractError("Step needs an operation: " + ident)
        if not isinstance(step.get("depends_on", []), list):
            raise ContractError("depends_on must be a list")
        if "fixture" in step:
            fixture = step["fixture"]
            if not isinstance(fixture, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.json", fixture):
                raise ContractError("Fixture must be a simple JSON filename")
    for step in steps:
        deps = step.get("depends_on", [])
        if any(not isinstance(dep, str) or dep not in known or dep == step["id"] for dep in deps):
            raise ContractError("Unknown or circular self-dependency: " + step["id"])
    for check in checks:
        if not isinstance(check, dict) or check.get("system") not in scenario["systems"]:
            raise ContractError("Check requires a registered system")
        if not isinstance(check.get("field"), str) or "equals" not in check:
            raise ContractError("Check requires field and equals")
    order_steps(steps)  # raises for dependency cycles
    return scenario


def order_steps(steps):
    """Stable topological ordering; identifies cycles before execution."""
    pending = {step["id"]: step for step in steps}
    ordered = []
    completed = set()
    while pending:
        ready = [step for step in steps if step["id"] in pending
                 and set(step.get("depends_on", [])).issubset(completed)]
        if not ready:
            raise ContractError("Scenario dependency graph contains a cycle")
        for step in ready:
            ordered.append(step)
            completed.add(step["id"])
            del pending[step["id"]]
    return ordered
