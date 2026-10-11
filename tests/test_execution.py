import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from research_platform.execution_study import ACTIONS, HYPOTHESES, TASKS, _run_condition
from research_platform.agents import ResearchAgent
from research_platform.executor import SafeExecutor
from research_platform.models import Action
from research_platform.planner import PlannerWeights, utility_breakdown


class ExecutionTests(unittest.TestCase):
    def test_executor_runs_registered_python_inside_managed_sandbox(self):
        with TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            executor = SafeExecutor(allow_managed_outer_sandbox=True)
            script = tmp_path / "probe.py"
            script.write_text("print('ok')")
            result = executor.run("probe", ["python3", str(script)], str(tmp_path), str(tmp_path))
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.stdout.strip(), "ok")
            self.assertIn(result.sandbox_backend,
                          {"macos-sandbox-exec", "managed-outer-sandbox-fallback"})

    def test_falsification_surfaces_confounded_first_result(self):
        task = next(task for task in TASKS if task.id == "case-confounded")
        executor = SafeExecutor(timeout_seconds=5, cpu_seconds=3, allow_managed_outer_sandbox=True)
        result = _run_condition(task.id, task.source, "adversarial-falsification", executor)
        self.assertEqual(result["history"][0]["observed"]["outcome"], "boundary-signature")
        self.assertTrue(result["history"][1]["counterevidence"])
        self.assertFalse(result["resolved"])
        self.assertIsNone(result["provisional_prediction"])

    def test_executor_rejects_workdir_outside_action_root(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "sandbox"
            root.mkdir()
            executor = SafeExecutor(allow_managed_outer_sandbox=True)
            with self.assertRaises(PermissionError):
                executor.run("escape", ["python3", "-c", "print('no')"],
                             directory, str(root))

    def test_paper4_default_utility_and_provenance_novelty(self):
        weights = PlannerWeights()
        beliefs = {hypothesis.id: hypothesis.prior for hypothesis in HYPOTHESES}
        self.assertEqual((weights.information_gain, weights.novelty,
                          weights.tractability, weights.cost), (10.0, 1.0, 1.0, 1.0))
        self.assertEqual(utility_breakdown(ACTIONS[0], beliefs, weights)["novelty"], 1.0)
        self.assertEqual(utility_breakdown(ACTIONS[1], beliefs, weights,
                                           {"subject-artifact"})["novelty"], 0.0)

    def test_model_policy_can_only_select_registered_action_ids(self):
        class Policy:
            def select_action(self, context):
                return "registered-probe"

            def select_falsification_action(self, context):
                return "registered-probe"

        action = Action("registered-probe", "fixed probe", ("H1",), 1.0,
                        expected_outcomes={"pass": {"H1": .9, "H2": .1},
                                           "fail": {"H1": .1, "H2": .9}})
        with TemporaryDirectory() as directory:
            agent = ResearchAgent(Policy(), SafeExecutor(allow_managed_outer_sandbox=True))
            result = agent.run(
                question_id="q", objective="test registered action", hypotheses={"H1": "one", "H2": "two"},
                beliefs={"H1": .5, "H2": .5}, actions=[action],
                commands={"registered-probe": ["python3", "-c", "print('{\"outcome\": \"pass\"}')"]},
                workspace=directory, max_actions=1, use_falsifier=False,
                minimum_probe_families=1,
            )
        self.assertTrue(result.resolved)
        self.assertEqual(result.trace[0]["role"], "planner")

    def test_model_policy_cannot_submit_raw_commands(self):
        class Policy:
            def select_action(self, context):
                return "python3 -c print(1)"

            def select_falsification_action(self, context):
                return "python3 -c print(1)"

        action = Action("registered-probe", "fixed probe", ("H1",), 1.0,
                        expected_outcomes={"pass": {"H1": .9, "H2": .1}})
        with TemporaryDirectory() as directory:
            agent = ResearchAgent(Policy(), SafeExecutor(allow_managed_outer_sandbox=True))
            with self.assertRaisesRegex(ValueError, "unavailable action ID"):
                agent.run(question_id="q", objective="test", hypotheses={"H1": "one"},
                          beliefs={"H1": 1.0}, actions=[action],
                          commands={"registered-probe": ["python3", "-c", "print('ok')"]},
                          workspace=directory, max_actions=1, use_falsifier=False)


if __name__ == "__main__":
    unittest.main()
