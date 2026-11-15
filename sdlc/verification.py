"""Evidence-first sandbox verification, with no external-system mutation."""
from datetime import datetime, timezone

from .contracts import ContractError, ROOT, load_json, order_steps, repo_path, validate_scenario, validate_task


class BlockedError(Exception):
    pass


class DemoAdapter:
    """Deterministic in-memory simulation; NOT proof of real external integration."""

    OPERATIONS = {
        "provision_manual_review", "submit_application", "process_status_sync"
    }

    def __init__(self):
        self.state = {
            "risk": {"status": "NOT_FOUND"},
            "application": {"status": "NOT_SUBMITTED"},
            "sync": {"delivered": False},
        }

    def execute(self, step):
        operation = step["operation"]
        if operation not in self.OPERATIONS:
            raise BlockedError("No approved demo operation for: " + operation)
        if operation == "provision_manual_review":
            if step["system"] != "risk":
                raise BlockedError("Wrong system for risk provisioning")
            fixture_name = step.get("fixture")
            if not fixture_name:
                raise BlockedError("Risk provisioning needs an approved fixture")
            fixture = load_json(ROOT / "fixtures" / fixture_name)
            if fixture.get("status") != "MANUAL_REVIEW":
                raise BlockedError("Fixture is not in the approved review state")
            self.state["risk"] = {"status": fixture["status"], "reference": fixture.get("reference", "demo-only")}
        elif operation == "submit_application":
            if step["system"] != "application" or self.state["risk"]["status"] != "MANUAL_REVIEW":
                raise BlockedError("Risk prerequisite is not ready")
            self.state["application"]["status"] = "PENDING_REVIEW"
        elif operation == "process_status_sync":
            if step["system"] != "sync" or self.state["application"]["status"] != "PENDING_REVIEW":
                raise BlockedError("Application prerequisite is not ready")
            self.state["sync"]["delivered"] = True
        return {"id": step["id"], "system": step["system"], "operation": operation, "status": "PASS"}


def verify(task):
    """Always return an evidence report; no execution against remote systems."""
    task = validate_task(task)
    if not task.get("scenario"):
        raise ContractError("This task has no executable scenario")
    scenario = validate_scenario(load_json(repo_path(task["scenario"], "scenarios")))
    report = {
        "task_id": task["id"], "scenario_id": scenario["id"],
        "environment": task["environment"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED", "classification": None, "steps": [], "checks": [],
        "limitations": ["Demo checks only simulate services; not a real multi-system E2E proof."],
    }
    if not set(scenario["systems"]).issubset(set(task["systems"])):
        report["classification"] = "CONFIGURATION"
        report["reason"] = "Scenario references systems absent from Task Contract"
        return report
    if task["environment"] != "demo" or scenario.get("adapter") != "demo":
        report["classification"] = "EXTERNAL_ADAPTER_UNAVAILABLE"
        report["reason"] = "Non-demo systems require a separately implemented and approved adapter"
        return report

    adapter = DemoAdapter()
    try:
        for step in order_steps(scenario["steps"]):
            report["steps"].append(adapter.execute(step))
    except (BlockedError, ContractError) as exc:
        report["classification"] = "TEST_DATA_OR_ENVIRONMENT"
        report["reason"] = str(exc)
        return report

    mismatches = []
    for check in scenario["checks"]:
        observed = adapter.state.get(check["system"], {}).get(check["field"])
        passed = type(observed) is type(check["equals"]) and observed == check["equals"]
        report["checks"].append({
            "system": check["system"], "field": check["field"],
            "expected": check["equals"], "actual": observed,
            "status": "PASS" if passed else "FAIL",
        })
        if not passed:
            mismatches.append(check["system"] + "." + check["field"])
    if mismatches:
        report["status"] = "FAIL"
        report["classification"] = "ASSERTION_FAILURE"
        report["reason"] = "Incorrect observed state: " + ", ".join(mismatches)
    else:
        report["status"] = "PASS"
        report["classification"] = "DEMO_VERIFIED"
        report["reason"] = "All sandbox scenario assertions passed"
    return report
