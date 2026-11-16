import copy
import json
import tempfile
import unittest
from pathlib import Path
from shutil import copy2
from unittest.mock import patch

from sdlc.contracts import ROOT, ContractError
from sdlc.entrypoint import doctor, route
from sdlc.mode import catalog, classify
from sdlc.pstack_bridge import (
    CONFIG, VENDOR, _bridge_config, _source, for_playbook,
    git_blob_sha, verify_sources,
)


class PstackIntegrationTests(unittest.TestCase):
    def test_vendored_files_match_original_upstream_blob_hashes(self):
        report = verify_sources()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["source_files"], 44)
        self.assertEqual(report["upstream_version"], "0.15.42")
        self.assertEqual(len(report["upstream_commit"]), 40)

    def test_all_local_playbooks_mapped_without_replacing_catalog(self):
        self.assertEqual(set(_bridge_config()["routes"]), set(catalog()))
        self.assertEqual(len(catalog()), 11)
        for key in catalog():
            ref = for_playbook(key)
            self.assertEqual(ref["mode"], "REFERENCE_ONLY")
            self.assertTrue(ref["principles"])
            for category in ("original_playbook", "principles", "skills"):
                for value in ref[category]:
                    self.assertEqual(value["source"], "Lauren Tan / pstack")
                    self.assertTrue(Path(value["path"]).is_file())
                    self.assertTrue(Path(value["path"]).resolve().is_relative_to(VENDOR.resolve()))

    def test_test_only_route_uses_verification_guidance(self):
        decision = classify("補齊 Cucumber 測試，不要修改產品程式碼")
        self.assertEqual(decision["playbook"], "verification")
        with tempfile.TemporaryDirectory() as d:
            result = route("補齊 Cucumber 測試，不要修改產品程式碼", project_root=d)
        ref = result["pstack_reference"]
        self.assertEqual(ref["mode"], "REFERENCE_ONLY")
        self.assertTrue(any("create-verification-skill" in x["path"] for x in ref["skills"]))
        self.assertEqual(result["decision"]["playbook"], "verification")

    def test_bank_workflow_is_authoritative_not_upstream(self):
        with tempfile.TemporaryDirectory() as d:
            result = route("修正申請查詢 bug", project_root=d)
        self.assertEqual(result["decision"]["playbook"], "bug-fix")
        self.assertTrue(any(s.get("gate") == "G4" for s in result["stages"]))
        self.assertTrue(any("bug-fix.md" in item["path"]
                            for item in result["pstack_reference"]["original_playbook"]))

    def test_upstream_automatic_ship_modes_not_active_routes(self):
        config = _bridge_config()
        self.assertIn("shipping", config["disabled_automatic_actions"])
        self.assertIn("automatic PR merge", config["disabled_automatic_actions"])
        self.assertNotIn("shipping", config["routes"])
        self.assertNotIn("babysit", config["routes"])
        self.assertEqual(config["mode"], "reference-only")

    def test_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            copied = Path(d)
            copy2(VENDOR / "LICENSE", copied / "LICENSE")
            copy2(VENDOR / "plugin.json", copied / "plugin.json")
            meta = {
                "schema_version": 1, "license": "MIT", "upstream_version": "0.15.42",
                "upstream_commit": "bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7",
                "files": {
                    "LICENSE": git_blob_sha(copied / "LICENSE"),
                    "plugin.json": git_blob_sha(copied / "plugin.json"),
                },
            }
            self.assertEqual(verify_sources(root=copied, manifest=meta)["status"], "PASS")
            (copied / "LICENSE").write_text("tampered")
            with self.assertRaises(ContractError):
                verify_sources(root=copied, manifest=meta)

    def test_source_escape_is_rejected(self):
        with self.assertRaises(ContractError):
            _source("../outside.md")
        with self.assertRaises(ContractError):
            _source("not-found/SKILL.md")

    def test_untracked_bridge_source_is_rejected(self):
        config = copy.deepcopy(_bridge_config())
        config["routes"]["feature"]["skills"].append("../something.md")
        with self.assertRaises(ContractError):
            _bridge_config(config)

    def test_doctor_reports_pstack_source_health_not_runtime_status(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / ".copilot"
            home.mkdir()
            result = doctor(ROOT, copilot_home=home)
            self.assertEqual(result["status"], "READY")
            self.assertEqual(result["pstack_vendor_health"]["status"], "PASS")
            self.assertTrue(any(
                x["effective_source"] == "NOT_RUNTIME_VERIFIED" for x in result["source_candidates"]
            ))


if __name__ == "__main__":
    unittest.main()
