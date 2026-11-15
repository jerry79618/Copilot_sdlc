import unittest
from sdlc.contracts import load_json
from sdlc.mode import make_worklist, update_worklist
from sdlc.reflect import render


class ReflectionTests(unittest.TestCase):
    def test_generated_lesson_template_does_not_claim_verified(self):
        run = make_worklist(load_json("contracts/examples/verification.json"))
        update_worklist(run, "scope", "BLOCKED", reason="Need an approved fixture")
        output = render(run)
        self.assertIn("Need an approved fixture", output)
        self.assertIn("GENERATED DRAFT", output)
        self.assertIn("do NOT auto-edit", output)

    def test_corrupt_worklist_cannot_be_reflected(self):
        with self.assertRaises(ValueError):
            render({"id": "bad"})


if __name__ == "__main__":
    unittest.main()
