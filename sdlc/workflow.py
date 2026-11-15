"""Deterministic work routing. AI agents follow this contract; the code does not call an LLM."""
from .contracts import validate_task, test_changes_allowed
from .model_policy import resolve as resolve_models

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
    routing = resolve_models(task)
    required_approval = routing["human_approval_required"]
    return {
        "task_id": task["id"],
        "intent": task["intent"],
        "workflow": WORKFLOWS[task["intent"]],
        "environment": task["environment"],
        "code_changes_allowed": task["allow_code_changes"],
        "test_code_changes_allowed": test_changes_allowed(task),
        "approval_required": required_approval,
        "model_routing": routing,
        "required_evidence_gates": routing["required_evidence_gates"],
        "gates": ["G1-spec", "G2-verifiability", "G3-readiness",
                  "G4-execution", "G5-review-ci", "G6-release-approval"],
    }
