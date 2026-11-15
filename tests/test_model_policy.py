import copy
import unittest
from sdlc.contracts import ContractError, load_json
from sdlc.credit_estimate import calculate
from sdlc.model_policy import policy, resolve, check_agents
from sdlc.mode import make_worklist


class ModelPolicyTests(unittest.TestCase):
    def setUp(self):
        self.low = load_json("contracts/examples/verification.json")
        self.low["risk"] = "low"
        self.medium = load_json("contracts/examples/verification.json")
        self.high = load_json("contracts/examples/banking-high-risk.json")

    def test_low_default_is_less_expensive(self):
        routed = resolve(self.low)
        self.assertEqual(routed["effective_risk"], "low")
        self.assertEqual([e["agent"] for e in routed["dispatch"]],
                         ["orchestrator", "developer", "tester", "reviewer"])
        self.assertFalse(routed["human_approval_required"])

    def test_medium_uses_high_developer_but_standard_review(self):
        routed = resolve(self.medium)
        self.assertEqual(routed["effective_risk"], "medium")
        self.assertIn("developer-high", [e["agent"] for e in routed["dispatch"]])
        self.assertNotIn("banking-reviewer", [e["agent"] for e in routed["dispatch"]])

    def test_sensitive_flag_escalates_even_if_low_is_declared(self):
        flagged = dict(self.low, impact_flags=["money_movement"])
        routed = resolve(flagged)
        self.assertTrue(routed["escalated"])
        self.assertEqual(routed["effective_risk"], "high")
        self.assertTrue(routed["human_approval_required"])
        self.assertEqual(set(routed["review_owners"]),
                         {"banking-reviewer", "cross-reviewer"})

    def test_unknown_flag_fails_closed(self):
        with self.assertRaises(ContractError):
            resolve(dict(self.low, impact_flags=["made_up"]))

    def test_high_risk_needs_two_reviewers_and_human_approval(self):
        result = resolve(self.high)
        self.assertTrue(result["human_approval_required"])
        self.assertIn("G6-human-approval", result["quality_gates"])
        self.assertEqual(len(result["review_owners"]), 2)
        self.assertFalse(result["external_deployment_allowed"])

    def test_existing_mode_worklist_includes_model_routing(self):
        worklist = make_worklist(self.high)
        self.assertEqual(worklist["model_routing"]["effective_risk"], "high")
        self.assertTrue(worklist["approval_required"])

    def test_all_agents_declare_locked_models_matching_policy(self):
        self.assertEqual(check_agents()["status"], "PASS")

    def test_price_table_matches_selected_roles(self):
        p = policy()
        for profile in p["profiles"].values():
            for agent in profile["agents"]:
                self.assertIn(p["agent_models"][agent], p["prices_usd_per_million_tokens"])


class CreditEstimateTests(unittest.TestCase):
    def test_scenario_cost_increases_with_scope(self):
        small, medium, large = [calculate(name)["estimated_ai_credits"]
                                for name in ("small", "medium", "large")]
        self.assertLess(small, medium)
        self.assertLess(medium, large)

    def test_double_tokens_doubles_cost(self):
        output = calculate("small")
        self.assertAlmostEqual(output["sensitivity_credits"]["double_token_budget"],
                               output["estimated_ai_credits"] * 2)

    def test_retry_costs_are_explicit(self):
        base = calculate("medium")
        retried = calculate("medium", retries=1)
        self.assertAlmostEqual(base["estimated_ai_credits"] * 2,
                               retried["estimated_ai_credits"])

    def test_invalid_retry_budget_is_rejected(self):
        with self.assertRaises(ContractError):
            calculate("large", retries=-1)

    def test_no_hidden_model_alias_or_unknown_case(self):
        with self.assertRaises(ContractError):
            calculate("unknown")


if __name__ == "__main__":
    unittest.main()
