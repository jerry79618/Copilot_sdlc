import unittest

from sdlc.contracts import load_json
from sdlc.workflow import plan


class DeterministicRoutingEval(unittest.TestCase):
    def test_known_routing_contracts(self):
        cases = load_json("evals/routing-cases.json")
        for case in cases:
            with self.subTest(case=case["task"]):
                route = plan(load_json(case["task"]))
                self.assertEqual(route["intent"], case["expected_intent"])
                self.assertIn(case["expected_stage"], route["workflow"])


if __name__ == "__main__":
    unittest.main()
