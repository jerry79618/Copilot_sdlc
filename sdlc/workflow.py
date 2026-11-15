"""Deterministic work routing. AI agents follow this contract; the code does not call an LLM."""
from .contracts import validate_task

WORKFLOWS = {
    "development": [
        "explore", "verification-contract", "architecture", "implementation",
        "unit-and-contract-tests", "scenario-readiness", "integration-e2e",
        "independent-review", "ci-gate", "pull-request",
    ],
    "verification": [
        "explore", "scenario-selection", "dependency-analysis",
        "test-data", "readiness-gate", "integration-e2e", "evidence", "report",
    ],
    "investigation": ["explore", "reproduce-if-safe", "evidence", "root-cause-report"],
}


def plan(task):
    task = validate_task(task)
    required_approval = task.get("approval_required", False) or task["risk"] == "high"
    return {
        "task_id": task["id"],
        "intent": task["intent"],
        "workflow": WORKFLOWS[task["intent"]],
        "environment": task["environment"],
        "code_changes_allowed": task["allow_code_changes"],
        "approval_required": required_approval,
        "gates": ["G1-spec", "G2-verifiability", "G3-readiness",
                  "G4-execution", "G5-review-ci", "G6-release-approval"],
    }
