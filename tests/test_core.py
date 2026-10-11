import tempfile
import unittest
from pathlib import Path

from research_platform.belief import update_beliefs
from research_platform.executor import SafeExecutor
from research_platform.models import Evidence, EvidenceKind
from research_platform.benchmark import controlled_cases
from research_platform.pilot import run_pilot


class CoreTests(unittest.TestCase):
    def test_belief_update_changes_mass_toward_supported_hypothesis(self):
        action = controlled_cases()[0].question.actions[0]
        evidence = Evidence("e", action.id, EvidenceKind.TEST_RESULT, {"outcome": "fail"},
                            "x", "1", "t", "x")
        beliefs = update_beliefs({"H-null": .5, "H-index": .5}, action, evidence)
        self.assertGreater(beliefs["H-null"], beliefs["H-index"])

    def test_executor_rejects_untrusted_program(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                SafeExecutor().run("a", ["sh", "-c", "echo unsafe"], directory)

    def test_pilot_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            first = run_pilot(Path(directory) / "one.json")
            second = run_pilot(Path(directory) / "two.json")
            self.assertEqual(first, second)
            self.assertEqual(first["resolved_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
