import copy
import json
import tempfile
import unittest
from pathlib import Path
from sdlc.contracts import ContractError, load_json
from sdlc.feature_map import load_feature_map
from sdlc.cucumber_evidence import convert
from sdlc.mode import catalog, make_worklist, update_worklist


def sample_report(status="passed"):
    steps = [{"name": "the prerequisite exists", "result": {"status": status}}]
    return [{"tags": [{"name": "@feature_manual_review"}], "elements": [
        {"type": "scenario", "name": "happy path", "steps": steps}]}]


class CucumberIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.map = load_feature_map("docs/feature-map/manual-review.md")
        self.task = load_json("contracts/examples/verification.json")

    def test_map_matches_all_real_sources(self):
        self.assertEqual(self.map["binding"]["scenario_id"], "REVIEW-001")
        self.assertEqual(self.map["binding"]["systems"], ["risk", "application", "sync"])

    def test_cucumber_pass_is_sandbox_only(self):
        result = convert(self.task, self.map, sample_report())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["classification"], "CUCUMBER_DEMO_VERIFIED")
        self.assertEqual(result["runner"], "cucumber-jvm")

    def test_skipped_or_undefined_step_causes_fail(self):
        for status in ("failed", "skipped", "undefined", "pending"):
            with self.subTest(status=status):
                result = convert(self.task, self.map, sample_report(status))
                self.assertEqual(result["status"], "FAIL")

    def test_missing_tag_blocks(self):
        report = sample_report()
        report[0]["tags"] = []
        self.assertEqual(convert(self.task, self.map, report)["status"], "BLOCKED")

    def test_missing_steps_is_not_pass(self):
        report = sample_report()
        report[0]["elements"][0]["steps"] = []
        self.assertEqual(convert(self.task, self.map, report)["status"], "FAIL")

    def test_staging_is_blocked(self):
        task = dict(self.task, environment="staging")
        self.assertEqual(convert(task, self.map, sample_report())["status"], "BLOCKED")

    def test_bdd_skill_is_registered(self):
        books = catalog()
        verification = next(s for s in books["verification"]["stages"] if s["id"] == "scenario")
        self.assertIn("cucumber-authoring", verification["skills"])

    def test_bdd_evidence_is_accepted_at_demo_gate(self):
        worklist = make_worklist(self.task)
        proof = convert(self.task, self.map, sample_report())
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "cucumber-evidence.json"
            evidence.write_text(json.dumps(proof), encoding="utf-8")
            for stage in worklist["stages"]:
                selected = str(evidence) if stage["gate"] == "G4" else "contracts/examples/verification.json"
                update_worklist(worklist, stage["id"], "PASS", evidence_path=selected)
            self.assertEqual(worklist["status"], "COMPLETE")

    def test_bdd_evidence_cannot_masquerade_as_staging(self):
        worklist = make_worklist(dict(self.task, environment="staging"))
        proof = convert(self.task, self.map, sample_report())
        proof["environment"] = "staging"
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "evidence.json"
            evidence.write_text(json.dumps(proof), encoding="utf-8")
            for stage in worklist["stages"]:
                if stage["gate"] == "G4":
                    with self.assertRaises(ContractError):
                        update_worklist(worklist, stage["id"], "PASS", evidence_path=str(evidence))
                    break
                update_worklist(worklist, stage["id"], "PASS", evidence_path="contracts/examples/verification.json")


if __name__ == "__main__":
    unittest.main()
