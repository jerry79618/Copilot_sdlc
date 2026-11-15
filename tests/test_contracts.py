import copy
import unittest

from sdlc.contracts import ContractError, load_json, order_steps, validate_scenario, validate_task
from sdlc.workflow import plan


class TaskContractTests(unittest.TestCase):
    def setUp(self):
        self.task = load_json("contracts/examples/verification.json")
        self.scenario = load_json("scenarios/manual-review.json")

    def test_valid_contract(self):
        self.assertEqual(validate_task(self.task)["intent"], "verification")

    def test_verification_disallows_code_modification(self):
        changed = {**self.task, "allow_code_changes": True}
        with self.assertRaises(ContractError):
            validate_task(changed)

    def test_development_routes_to_both_pipelines(self):
        task = load_json("contracts/examples/development.json")
        stages = plan(task)["workflow"]
        self.assertIn("implementation", stages)
        self.assertIn("integration-e2e", stages)

    def test_verification_route_has_readiness_gate(self):
        stages = plan(self.task)["workflow"]
        self.assertIn("readiness-gate", stages)
        self.assertNotIn("implementation", stages)

    def test_topological_order_handles_out_of_order_steps(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["steps"].reverse()
        validate_scenario(scenario)
        self.assertEqual([s["id"] for s in order_steps(scenario["steps"])],
                         ["risk_data", "submit", "sync_event"])

    def test_rejects_cyclic_graph(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["steps"][0]["depends_on"] = ["sync_event"]
        with self.assertRaises(ContractError):
            validate_scenario(scenario)

    def test_rejects_unknown_system(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["steps"][1]["system"] = "unknown"
        with self.assertRaises(ContractError):
            validate_scenario(scenario)

    def test_rejects_fixture_traversal(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["steps"][0]["fixture"] = "../../prod.json"
        with self.assertRaises(ContractError):
            validate_scenario(scenario)


if __name__ == "__main__":
    unittest.main()
