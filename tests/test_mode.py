import copy
import json
import tempfile
import unittest
from pathlib import Path

from sdlc.contracts import ContractError, load_json
from sdlc.mode import catalog, classify, make_worklist, next_stage, update_worklist
from sdlc.verification import verify


class SDLCModeTests(unittest.TestCase):
    def setUp(self):
        self.task = load_json("contracts/examples/verification.json")
        self.development = load_json("contracts/examples/development.json")

    def test_all_playbooks_are_valid(self):
        books = catalog()
        self.assertEqual(len(books), 8)
        for book in books.values():
            self.assertGreater(len(book["stages"]), 3)
            self.assertTrue(any(stage.get("gate") for stage in book["stages"]))

    def test_english_bug_routes_to_repro_first(self):
        route = classify("Users receive a duplicate notice. Fix the bug, reproduce first.")
        self.assertEqual(route["playbook"], "bug-fix")
        self.assertEqual(route["intent"], "development")

    def test_chinese_verification_routes_correctly(self):
        route = classify("測試跨系統人工覆核流程，確認特殊資料就緒")
        self.assertEqual(route["playbook"], "verification")
        self.assertTrue(route["cross_system_hint"])

    def test_chinese_feature_routes_correctly(self):
        self.assertEqual(classify("新增訂單查詢功能")["playbook"], "feature")

    def test_read_only_constraint_overrides_bugfix(self):
        route = classify("先調查這個 bug，暫時不要修改程式")
        self.assertEqual(route["intent"], "investigation")
        self.assertEqual(route["playbook"], "investigation")

    def test_unknown_goal_requires_review(self):
        route = classify("Could we make this better?")
        self.assertEqual(route["playbook"], "figure-it-out")
        self.assertTrue(route["requires_confirmation"])

    def test_explicit_intent_wins_over_keywords(self):
        route = classify("新增訂單功能並進行驗證", intent="verification")
        self.assertEqual(route["playbook"], "verification")

    def test_explicit_conflicting_playbook_is_rejected(self):
        with self.assertRaises(ContractError):
            classify("修復 bug", intent="verification", override="bug-fix")

    def test_worklist_selects_verification_from_task(self):
        run = make_worklist(self.task)
        self.assertEqual(run["playbook"], "verification")
        self.assertEqual(run["intent"], "verification")
        self.assertEqual(next_stage(run)["id"], "scope")
        self.assertFalse(any(s["id"] == "implement" for s in run["stages"]))

    def test_development_includes_real_verification_gate(self):
        run = make_worklist(self.development)
        self.assertEqual(run["playbook"], "feature")
        self.assertEqual([s["gate"] for s in run["stages"] if s["gate"]],
                         ["G1", "G2", "G3", "G4", "G5"])
        self.assertTrue(run["approval_required"] is False)

    def test_reject_wrong_stage_and_missing_proof(self):
        run = make_worklist(self.task)
        with self.assertRaises(ContractError):
            update_worklist(run, "runtime-verify", "PASS", "fixtures/manual-review.json")
        with self.assertRaises(ContractError):
            update_worklist(run, "scope", "PASS")
        self.assertEqual(next_stage(run)["id"], "scope")

    def test_can_block_then_resume_with_proof(self):
        run = make_worklist(self.task)
        update_worklist(run, "scope", "BLOCKED", reason="Acceptance criteria missing")
        self.assertEqual(run["status"], "BLOCKED")
        self.assertEqual(next_stage(run)["id"], "scope")
        update_worklist(run, "scope", "PASS", evidence_path="contracts/examples/verification.json")
        self.assertEqual(run["status"], "ACTIVE")
        self.assertEqual(next_stage(run)["id"], "feature-map")

    def test_mandatory_stage_may_not_be_skipped(self):
        run = make_worklist(self.task)
        with self.assertRaises(ContractError):
            update_worklist(run, "scope", "SKIP", reason="Not needed")

    def test_optional_stage_requires_reason_to_skip(self):
        run = make_worklist(self.task)
        for stage in run["stages"]:
            if stage["id"] == "test-data":
                break
            update_worklist(run, stage["id"], "PASS", evidence_path="contracts/examples/verification.json")
        with self.assertRaises(ContractError):
            update_worklist(run, "test-data", "SKIP")
        update_worklist(run, "test-data", "SKIP", reason="Synthetic fixture already present")
        self.assertEqual(next_stage(run)["id"], "readiness")

    def test_demo_can_complete_worklist_with_actual_verification_evidence(self):
        run = make_worklist(self.task)
        proof = verify(self.task)
        self.assertEqual(proof["status"], "PASS")
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "evidence.json"
            evidence.write_text(json.dumps(proof), encoding="utf-8")
            for stage in run["stages"]:
                file = str(evidence if stage["gate"] == "G4" else Path("contracts/examples/verification.json"))
                update_worklist(run, stage["id"], "PASS", evidence_path=file)
            self.assertEqual(run["status"], "COMPLETE")
            self.assertIsNone(next_stage(run))
            with self.assertRaises(ContractError):
                update_worklist(run, "report", "PASS", evidence_path=file)

    def test_wrong_task_evidence_is_rejected(self):
        run = make_worklist(self.task)
        with tempfile.TemporaryDirectory() as temp:
            proof = verify(self.task)
            proof["task_id"] = "OTHER"
            path = Path(temp) / "wrong.json"
            path.write_text(json.dumps(proof), encoding="utf-8")
            for stage in run["stages"]:
                if stage["gate"] == "G4":
                    with self.assertRaises(ContractError):
                        update_worklist(run, stage["id"], "PASS", evidence_path=str(path))
                    break
                update_worklist(run, stage["id"], "PASS", evidence_path="contracts/examples/verification.json")

    def test_real_environment_cannot_fake_demo_evidence(self):
        task = dict(self.task)
        task["environment"] = "staging"
        run = make_worklist(task)
        with tempfile.TemporaryDirectory() as temp:
            fake = verify(self.task)
            fake["environment"] = "staging"
            path = Path(temp) / "not-real.json"
            path.write_text(json.dumps(fake), encoding="utf-8")
            for stage in run["stages"]:
                if stage["gate"] == "G4":
                    with self.assertRaises(ContractError):
                        update_worklist(run, stage["id"], "PASS", evidence_path=str(path))
                    break
                update_worklist(run, stage["id"], "PASS", evidence_path="contracts/examples/verification.json")

    def test_routing_evals(self):
        for item in load_json("evals/mode-routing-cases.json"):
            with self.subTest(goal=item["goal"]):
                route = classify(item["goal"], item.get("intent"))
                self.assertEqual(route["playbook"], item["expected_playbook"])


if __name__ == "__main__":
    unittest.main()
