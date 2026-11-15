
import json
import tempfile
import unittest
from pathlib import Path

from sdlc.contracts import ContractError, load_json, test_changes_allowed, validate_task
from sdlc.mode import make_worklist, next_stage, update_worklist
from sdlc.model_policy import check_agents, resolve
from sdlc.verification import verify


class RiskAwareWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.task = load_json("contracts/examples/verification.json")

    def test_low_risk_progress_does_not_require_evidence_per_step(self):
        task = dict(self.task, risk="low")
        run = make_worklist(task)
        self.assertEqual(run["workflow_intensity"], "lean")
        self.assertEqual(run["model_routing"]["required_evidence_gates"], ["G4"])
        self.assertTrue(run["test_code_changes_allowed"])
        for stage in run["stages"]:
            if stage["gate"] == "G4":
                break
            update_worklist(run, stage["id"], "PASS")
        with self.assertRaises(ContractError):
            update_worklist(run, "runtime-verify", "PASS")
        self.assertEqual(next_stage(run)["id"], "runtime-verify")

    def test_low_risk_can_finish_with_single_runtime_artifact(self):
        task = dict(self.task, risk="low")
        run = make_worklist(task)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "proof.json"
            path.write_text(json.dumps(verify(task)), encoding="utf-8")
            for step in run["stages"]:
                evidence = str(path) if step["gate"] == "G4" else None
                update_worklist(run, step["id"], "PASS", evidence_path=evidence)
            self.assertEqual(run["status"], "COMPLETE")
            other = [s for s in run["stages"] if s["gate"] != "G4"]
            self.assertTrue(all(s["evidence"] is None for s in other))

    def test_medium_risk_requires_baseline_and_review_proof(self):
        run = make_worklist(self.task)
        required = {s["gate"] for s in run["stages"] if s["evidence_required"]}
        self.assertEqual(required, {"G2", "G4", "G5"})
        update_worklist(run, "scope", "PASS")
        with self.assertRaises(ContractError):
            update_worklist(run, "feature-map", "PASS")
        self.assertEqual(next_stage(run)["id"], "feature-map")

    def test_high_risk_requires_artifacts_and_human_release_approval(self):
        high = load_json("contracts/examples/banking-high-risk.json")
        run = make_worklist(high)
        self.assertEqual(run["workflow_intensity"], "regulated")
        self.assertTrue(run["approval_required"])
        self.assertTrue(run["model_routing"]["all_stage_evidence"])
        self.assertIn("G6-human-approval", run["model_routing"]["quality_gates"])
        self.assertTrue(all(s["evidence_required"] for s in run["stages"] if not s["optional"]))
        with self.assertRaises(ContractError):
            update_worklist(run, "understand", "PASS")

    def test_bank_impact_flag_cannot_stay_low(self):
        task = dict(self.task, risk="low", impact_flags=["authorization"])
        run = make_worklist(task)
        self.assertEqual(run["model_routing"]["effective_risk"], "high")
        self.assertTrue(run["approval_required"])
        with self.assertRaises(ContractError):
            update_worklist(run, "scope", "PASS")

    def test_test_code_edits_are_independent_from_product_code_edits(self):
        self.assertTrue(test_changes_allowed(self.task))
        self.assertFalse(self.task["allow_code_changes"])
        disabled = dict(self.task, allow_test_changes=False)
        self.assertFalse(test_changes_allowed(disabled))
        read_only = load_json("contracts/examples/investigation.json")
        self.assertFalse(test_changes_allowed(read_only))
        with self.assertRaises(ContractError):
            validate_task(dict(read_only, allow_test_changes=True))
        with self.assertRaises(ContractError):
            validate_task(dict(self.task, allow_test_changes="yes"))
        dev = load_json("contracts/examples/development.json")
        self.assertTrue(test_changes_allowed(dev))

    def test_fallback_is_limited_to_authored_models(self):
        routed = resolve(self.task)
        for agent in routed["dispatch"]:
            self.assertEqual(agent["policy"], "required")
            self.assertFalse(agent["approval_verified"])
            self.assertNotIn(agent["model"], agent["fallback_candidates"])
        self.assertEqual(check_agents()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
