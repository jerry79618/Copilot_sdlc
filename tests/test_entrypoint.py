import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sdlc.contracts import ROOT
from sdlc.entrypoint import doctor, route, main


class EntrypointTests(unittest.TestCase):
    def test_other_project_reads_canonical_playbooks_without_install(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "copilot-home"
            home.mkdir()
            java_repo = Path(d) / "bank-service"
            java_repo.mkdir()
            result = doctor(java_repo, copilot_home=home)
            self.assertEqual(result["status"], "READY")
            self.assertEqual(result["playbook_count"], 11)
            self.assertEqual(Path(result["catalog_path"]),
                             ROOT / "playbooks" / "catalog.json")
            routed = route("修復申請查詢 bug", project_root=java_repo)
            self.assertEqual(routed["decision"]["playbook"], "bug-fix")
            self.assertEqual(Path(routed["project_root"]), java_repo)
            self.assertTrue(any(s["gate"] == "G4" for s in routed["stages"]))
            for stage in routed["stages"]:
                for skill in stage["skills"]:
                    self.assertTrue(Path(skill["path"]).is_file())

    def test_stale_user_agent_blocks_launcher_diagnosis(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / ".copilot"
            agent = home / "agents" / "orchestrator.agent.md"
            agent.parent.mkdir(parents=True)
            agent.write_text("outdated", encoding="utf-8")
            result = doctor(ROOT, copilot_home=home)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["shadow_conflicts"][0]["kind"], "agent")

    def test_old_global_sdlc_skill_blocks_diagnosis(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / ".copilot"
            local = home / "skills" / "sdlc-mode" / "SKILL.md"
            local.parent.mkdir(parents=True)
            local.write_text("outdated", encoding="utf-8")
            result = doctor(ROOT, copilot_home=home)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["shadow_conflicts"][0]["kind"], "skill")

    def test_unknown_target_fails_before_running_copilot(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("sys.argv", ["entrypoint", "doctor", "--project-root", str(Path(d) / "nope")]):
                self.assertEqual(main(), 3)

    def test_cli_route_json_contains_real_catalog(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / ".copilot"
            home.mkdir()
            with patch.dict("os.environ", {"COPILOT_HOME": str(home)}):
                from io import StringIO
                with patch("sys.stdout", new_callable=StringIO) as out:
                    code = main(["route", "--goal", "新增訂單查詢功能", "--project-root", d])
                self.assertEqual(code, 0)
                payload = json.loads(out.getvalue())
                self.assertEqual(payload["decision"]["playbook"], "feature")
                self.assertIn("catalog.json", payload["catalog_path"])


if __name__ == "__main__":
    unittest.main()
