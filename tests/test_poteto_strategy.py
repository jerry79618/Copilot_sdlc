import tempfile
import unittest
from pathlib import Path

from sdlc.contracts import ROOT, ContractError
from sdlc.entrypoint import route
from sdlc.poteto_strategy import (
    ENGINEERING_PILLARS, propose, source_playbooks, pillar_sources,
)
from sdlc.pstack_bridge import verify_sources


class LaurenTanPotetoStrategyTests(unittest.TestCase):
    def test_original_method_catalog_is_complete_and_pinned(self):
        self.assertEqual(len(source_playbooks()), 23)
        skills = list((ROOT / "vendor/pstack/skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 58)
        report = verify_sources()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["source_files"], 100)
        self.assertEqual(len(ENGINEERING_PILLARS), 6)
        for values in pillar_sources().values():
            self.assertTrue(all(Path(item["path"]).is_file() for item in values))

    def test_main_agent_owns_simple_bug_without_forced_coordinator(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = propose("幫我修正申請查詢錯誤", tmp)
            self.assertEqual(value["owner"], "current-copilot-session-main-agent")
            self.assertFalse(value["dedicated_orchestrator_required"])
            self.assertEqual(value["local_bank_playbook"], "bug-fix")
            self.assertEqual(value["upstream_playbook"], "bug-fix")
            self.assertEqual(value["coordination"], "main-agent-leads")
            self.assertFalse(value["execution_authorized"])
            self.assertFalse(value["verified_work"])

    def test_program_orchestrate_only_for_explicit_large_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = propose("負責整個專案，管理多個 PR 的長期計畫", tmp)
            self.assertEqual(value["upstream_playbook"], "orchestrate")
            self.assertEqual(value["coordination"], "main-agent-program-coordinator")
            self.assertEqual(value["delegation"], "workers-per-independent-PR-when-host-authorizes")
            self.assertEqual(value["host_status"], "HOST_CAPABILITY_REQUIRED")

    def test_autonomous_run_and_shipping_are_advisory_not_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            loop = propose("持續到完成，直到測試通過", tmp)
            self.assertEqual(loop["upstream_playbook"], "autonomous-run")
            self.assertEqual(loop["host_status"], "HOST_CAPABILITY_REQUIRED")
            ship = propose("請幫我合併 PR", tmp)
            self.assertEqual(ship["upstream_playbook"], "shipping")
            self.assertTrue(ship["human_approval_for_merge"])
            self.assertFalse(ship["execution_authorized"])
            self.assertTrue(any("Never merge" in r for r in ship["risk_constraints"]))

    def test_pr_lifecycle_uses_babysit_playbook(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = propose("檢查 PR 狀態與 CI", tmp)
            self.assertEqual(value["upstream_playbook"], "babysit")
            self.assertEqual(value["coordination"], "main-agent-direct")
            self.assertFalse(value["verified_work"])

    def test_test_only_keeps_native_bank_verification_and_real_g4(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = route("補齊 Cucumber 測試，不要修改產品程式碼", project_root=tmp)
            self.assertEqual(value["decision"]["playbook"], "verification")
            self.assertEqual(value["execution_strategy"]["local_bank_playbook"], "verification")
            self.assertIsNone(value["execution_strategy"]["upstream_playbook"])
            self.assertFalse(value["execution_strategy"]["execution_authorized"])
            self.assertEqual(value["mode"]["owner"], "session-main-agent")
            self.assertTrue(any(s["gate"] == "G4" for s in value["stages"]))

    def test_optional_full_upstream_catalog_overrides_do_not_grant_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in source_playbooks():
                value = propose("review task", tmp, upstream_playbook=name)
                self.assertEqual(value["upstream_playbook"], name)
                self.assertTrue(Path(value["upstream_source_path"]).is_file())
                self.assertFalse(value["execution_authorized"])
                self.assertTrue(value["human_approval_for_merge"])

    def test_rejects_unlisted_original_playbooks_and_bad_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ContractError):
                propose("fix bug", tmp, upstream_playbook="../evil")
            with self.assertRaises(ContractError):
                propose("fix bug", Path(tmp) / "missing")
            with self.assertRaises(ContractError):
                propose("", tmp)


if __name__ == "__main__":
    unittest.main()
