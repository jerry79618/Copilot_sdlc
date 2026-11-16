import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from sdlc.contracts import ROOT, ContractError, repo_path, validate_task
from sdlc.discovery import main as discovery_main, map_health
from sdlc.entrypoint import doctor, main as entry_main
from sdlc.feature_map import load_feature_map
from sdlc.mode import classify, make_worklist, update_worklist
from sdlc.project_context import prepare
from sdlc.verification import verify


class Version08Tests(unittest.TestCase):
    def test_short_goal_preparation_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text("<project/>")
            (root / "AGENTS.md").write_text("project rules")
            result = prepare("幫我新增查詢 API", root)
            self.assertEqual(result["state"], "DRAFT_NOT_EXECUTABLE")
            self.assertEqual(result["routing"]["playbook"], "feature")
            self.assertEqual(result["project"]["build_files"], ["pom.xml"])
            self.assertEqual(result["authorization"]["product_code_changes"], "REVIEW_USER_SCOPE")
            self.assertIn("acceptance_criteria", result["unconfirmed"])
            self.assertFalse((root / "artifacts").exists())

    def test_testing_without_product_edits_routes_as_verification(self):
        goal = "請補齊 Cucumber 測試，不要修改產品程式碼"
        self.assertEqual(classify(goal)["playbook"], "verification")
        with tempfile.TemporaryDirectory() as tmp:
            draft = prepare(goal, tmp)
            self.assertEqual(draft["authorization"]["product_code_changes"], "NOT_ALLOWED")
        self.assertEqual(classify("先調查這個 bug，不要修改程式")["playbook"], "investigation")

    def test_external_contract_paths_are_scoped_and_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scenarios").mkdir()
            (root / "scenarios" / "test.json").write_text("{}")
            task = {
                "id": "TASK-TEMP", "goal": "測試", "intent": "verification",
                "acceptance_criteria": ["Valid response"], "systems": ["sample"],
                "risk": "low", "environment": "test", "allow_code_changes": False,
                "scenario": "scenarios/test.json"
            }
            self.assertEqual(validate_task(task, project_root=root)["id"], "TASK-TEMP")
            with self.assertRaises(ContractError):
                validate_task(task)
            with self.assertRaises(ContractError):
                repo_path("../../outside", "scenarios", project_root=root)
            self.assertEqual(repo_path("scenarios/test.json", "scenarios", project_root=root),
                             root / "scenarios" / "test.json")

    def test_external_repo_cannot_relabel_framework_demo_as_g4_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scenarios").mkdir()
            (root / "scenarios" / "manual-review.json").write_text(
                (ROOT / "scenarios" / "manual-review.json").read_text()
            )
            task = json.loads((ROOT / "contracts" / "examples" / "verification.json").read_text())
            task["risk"] = "low"
            run = make_worklist(task, project_root=root)
            self.assertEqual(run["project_root"], str(root))
            self.assertEqual(verify(task, project_root=root)["status"], "BLOCKED")
            evidence = root / "demo.json"
            evidence.write_text(json.dumps(verify(task)))
            for step in run["stages"]:
                if step["gate"] == "G4":
                    with self.assertRaises(ContractError):
                        update_worklist(run, step["id"], "PASS", evidence_path=str(evidence))
                    break
                update_worklist(run, step["id"], "PASS")

    def test_discovery_candidates_are_stored_in_target_not_framework(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "main" / "java"
            src.mkdir(parents=True)
            (src / "LookupController.java").write_text(
                '@RestController class LookupController { '
                '@GetMapping("/query") String lookup(){return "";} }'
            )
            with patch("sys.stdout", new_callable=StringIO):
                self.assertEqual(discovery_main(["candidates", "--project-root", str(root)]), 0)
            drafts = list((root / "artifacts" / "discovery").glob("*.candidate.md"))
            self.assertEqual(len(drafts), 1)
            self.assertIn("NOT VERIFIED", drafts[0].read_text())
            with patch("sys.stdout", new_callable=StringIO):
                self.assertEqual(discovery_main(["candidates", "--project-root", str(root)]), 3)
                self.assertEqual(discovery_main([
                    "candidates", "--project-root", str(root),
                    "--output-dir", str(root.parent / "outside")
                ]), 3)

    def test_external_feature_map_candidate_is_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "docs" / "feature-map"
            folder.mkdir(parents=True)
            (folder / "account.md").write_text(
                "# Feature Map\n## Sub-features\n- Query\n"
                "## How to get to it (user POV)\n- TODO\n"
            )
            self.assertEqual(map_health(tmp)[0]["status"], "CANDIDATE_REVIEW_REQUIRED")

    def test_external_feature_map_supports_java_standard_test_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                "docs/feature-map", "src/test/resources/features",
                "contracts", "scenarios", "fixtures"
            ):
                (root / rel).mkdir(parents=True)
            (root / "src/test/resources/features/account.feature").write_text(
                "@feature_account\nFeature: Query\n  Scenario: Query\n    Given a record exists\n"
            )
            scenario = json.loads((ROOT / "scenarios/manual-review.json").read_text())
            (root / "scenarios/manual-review.json").write_text(json.dumps(scenario))
            task = json.loads((ROOT / "contracts/examples/verification.json").read_text())
            (root / "contracts/verification.json").write_text(json.dumps(task))
            (root / "fixtures/manual-review.json").write_text("{}")
            binding = {
                "feature_id": "account", "scenario_id": scenario["id"],
                "gherkin": "src/test/resources/features/account.feature",
                "scenario": task["scenario"], "contract": "contracts/verification.json",
                "fixture": "fixtures/manual-review.json",
                "systems": scenario["systems"], "adapter": "demo"
            }
            fence = chr(96) * 3
            (root / "docs/feature-map/account.md").write_text(
                "# Feature Map\n## Sub-features\n- Query\n"
                "## How to get to it (user POV)\n- API\n"
                "## Driving it (runtime)\n- TODO\n"
                "## Gotchas\n- TODO\n"
                "## SDLC Cucumber Binding\n" + fence + "json\n" +
                json.dumps(binding) + "\n" + fence + "\n"
            )
            self.assertEqual(
                load_feature_map("docs/feature-map/account.md", project_root=root)["feature_id"],
                "account"
            )
            self.assertEqual(map_health(root)[0]["status"], "STATIC_LINKS_VALID")

    def test_project_override_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            home = Path(tmp) / ".copilot"
            root.mkdir()
            home.mkdir()
            agent = root / ".github" / "agents" / "orchestrator.agent.md"
            agent.parent.mkdir(parents=True)
            agent.write_text("old project agent")
            result = doctor(root, copilot_home=home)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any(item["kind"] == "agent" for item in result["shadow_conflicts"]))
            self.assertTrue(any(item["name"] == "orchestrator"
                                for item in result["source_candidates"]))

    def test_entrypoint_prepare_does_not_create_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("sys.stdout", new_callable=StringIO) as output:
                self.assertEqual(entry_main(["prepare", "--project-root", tmp, "--goal", "分析 API"]), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report["type"], "SDLC_TASK_CONTEXT_DRAFT")
            self.assertFalse((Path(tmp) / "artifacts").exists())


if __name__ == "__main__":
    unittest.main()
