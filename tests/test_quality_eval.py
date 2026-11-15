import unittest
from sdlc.quality_eval import evaluate
from sdlc.contracts import load_json


class RoutingEvaluationTests(unittest.TestCase):
    def test_reference_cases_pass(self):
        result = evaluate()
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["total"], 15)
        self.assertEqual(result["accuracy"], 1)

    def test_detects_wrong_route(self):
        cases = load_json("evals/mode-routing-cases.json")
        cases[0]["expected_playbook"] = "figure-it-out"
        result = evaluate(cases, [])
        self.assertEqual(result["status"], "FAIL")

    def test_detects_missing_skill(self):
        result = evaluate([], [{"playbook": "verification",
                                "stage": "scenario", "must_use_skill": "imaginary-skill"}])
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
