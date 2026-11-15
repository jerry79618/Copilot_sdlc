import tempfile
import unittest
from pathlib import Path

from sdlc.contracts import ROOT
from sdlc.discovery import inspect, draft_map, map_health


class FeatureDiscoveryTests(unittest.TestCase):
    def make_project(self, root):
        source = root / "src" / "main" / "java" / "AccountController.java"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            '@RestController\n@RequestMapping("/accounts")\n'
            'public class AccountController {\n'
            '@GetMapping("/{id}") public String find() {return "";} \n'
            '@PostMapping("/open") public String open() {return "";}\n'
            '}\n', encoding="utf-8")
        feature = root / "src" / "test" / "resources" / "features" / "accounts.feature"
        feature.parent.mkdir(parents=True, exist_ok=True)
        feature.write_text('@feature_account\nFeature: Account\n  Scenario: Lookup\n'
                           '    Given a fixture\n', encoding="utf-8")
        return source

    def test_controller_and_gherkin_discovered(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root)
            data = inspect(root)
            self.assertEqual(len(data["java_controllers"]), 1)
            self.assertEqual(data["java_controllers"][0]["base_path_hint"], "/accounts")
            self.assertEqual(len(data["java_controllers"][0]["mappings"]), 2)
            self.assertEqual(data["gherkin_features"][0]["tagged_features"], ["account"])
            self.assertEqual(data["gherkin_features"][0]["scenarios"], 1)

    def test_draft_is_not_runtime_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root)
            text = draft_map(inspect(root)["java_controllers"][0])
            for heading in ("## Sub-features", "## How to get to it",
                            "## Driving it", "## Gotchas"):
                self.assertIn(heading, text)
            self.assertIn("NOT VERIFIED", text)
            self.assertIn("TODO:", text)

    def test_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "proj"
            root.mkdir()
            other = Path(temp) / "external.java"
            other.write_text('@RestController public class External {}', encoding="utf-8")
            (root / "external.java").symlink_to(other)
            self.assertEqual(inspect(root)["java_controllers"], [])

    def test_ignores_generated_target_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_project(root)
            generated = root / "target" / "DuplicateController.java"
            generated.parent.mkdir()
            generated.write_text(source.read_text(), encoding="utf-8")
            self.assertEqual(len(inspect(root)["java_controllers"]), 1)

    def test_existing_map_links_are_statically_valid(self):
        checks = map_health(ROOT)
        manual = next(r for r in checks if r["path"].endswith("manual-review.md"))
        self.assertEqual(manual["status"], "STATIC_LINKS_VALID")


if __name__ == "__main__":
    unittest.main()
