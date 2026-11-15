import copy
import unittest

from sdlc.contracts import ContractError, load_json
from sdlc.verification import verify


class RuntimeVerificationTests(unittest.TestCase):
    def setUp(self):
        self.task = load_json("contracts/examples/verification.json")

    def test_full_demo_journey_passes(self):
        result = verify(self.task)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["steps"]), 3)
        self.assertEqual(len(result["checks"]), 3)
        self.assertEqual(result["classification"], "DEMO_VERIFIED")

    def test_real_environment_is_blocked_not_claimed_pass(self):
        task = {**self.task, "environment": "staging"}
        result = verify(task)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["classification"], "EXTERNAL_ADAPTER_UNAVAILABLE")

    def test_missing_system_returns_blocked(self):
        task = {**self.task, "systems": ["risk", "application"]}
        result = verify(task)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["classification"], "CONFIGURATION")

    def test_restricted_task_cannot_change_code(self):
        task = {**self.task, "allow_code_changes": True}
        with self.assertRaises(ContractError):
            verify(task)


if __name__ == "__main__":
    unittest.main()
