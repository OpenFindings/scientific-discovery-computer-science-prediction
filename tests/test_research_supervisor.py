import fcntl
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "scripts/research_supervisor.py"
CHECK = ROOT / "scripts/research_check.py"


class ResearchSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "research").mkdir()
        (self.root / "AGENTS.md").write_text("test mission\n")
        state = {"schema_version": 1, "campaign_id": "test", "campaign_status": "active",
                 "current_research_round": 0, "completed_tasks": [], "blocked_tasks": [],
                 "pending_tasks": ["T1"], "budget_consumption": {"configured_max_rounds": 2,
                 "configured_max_worker_invocations": 2, "configured_max_wall_seconds": 1200,
                 "configured_max_artifact_mib": 1, "minimum_disk_free_mib": 0,
                 "paid_worker_invocations": 0}}
        queue = {"schema_version": 1, "tasks": [{"task_id": "T1", "objective": "test task",
                 "dependencies": [], "expected_information_gain": 1, "cost_estimate": 1,
                 "priority": 1, "status": "pending", "max_attempts": 2,
                 "success_criteria": ["artifact exists"], "artifact": "results/T1.json"}]}
        (self.root / "research/state.json").write_text(json.dumps(state))
        (self.root / "research/task_queue.json").write_text(json.dumps(queue))
        (self.root / "research/experiment_ledger.jsonl").write_text("")
        fake = self.root / "fake-codex"
        fake.write_text("#!/usr/bin/env python3\nimport os,sys,json\nfrom pathlib import Path\n"
                        "mode=os.environ.get('FAKE_CODEX_MODE','success')\n"
                        "if mode=='limit': print('usage limit reached',file=sys.stderr); raise SystemExit(1)\n"
                        "if mode=='fail': raise SystemExit(9)\n"
                        "prompt=sys.stdin.read(); rel=[x.removeprefix('Write only: ') for x in prompt.splitlines() if x.startswith('Write only: ')][0]\n"
                        "p=Path(rel); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps({'result':'negative','evidence_tier':4}))\n"
                        "raise SystemExit(0)\n")
        fake.chmod(0o755)
        self.fake = fake

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, mode="success", args=("--start", "--max-rounds", "1")):
        env = os.environ.copy()
        env["RESEARCH_SUPERVISOR_CODEX_BIN"] = str(self.fake)
        env["FAKE_CODEX_MODE"] = mode
        return subprocess.run([sys.executable, str(SUPERVISOR), "--repo-root", str(self.root), *args],
                              text=True, capture_output=True, env=env, timeout=20)

    def state(self):
        return json.loads((self.root / "research/state.json").read_text())

    def queue(self):
        return json.loads((self.root / "research/task_queue.json").read_text())

    def test_dry_run_does_not_invoke_worker_or_mutate_state(self):
        before = (self.root / "research/state.json").read_bytes()
        result = self.invoke(args=("--dry-run",))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"worker_invocations": 0', result.stdout)
        self.assertEqual(before, (self.root / "research/state.json").read_bytes())
        self.assertFalse((self.root / "results/T1.json").exists())

    def test_bounded_worker_persists_negative_result(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.queue()["tasks"][0]["status"], "completed")
        self.assertEqual(self.state()["completed_tasks"], ["T1"])
        artifact = json.loads((self.root / "results/T1.json").read_text())
        self.assertEqual(artifact["result"], "negative")

    def test_failed_worker_retries_are_bounded(self):
        queue = self.queue()
        queue["tasks"][0]["max_attempts"] = 1
        (self.root / "research/task_queue.json").write_text(json.dumps(queue))
        result = self.invoke("fail")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.queue()["tasks"][0]["status"], "blocked")
        self.assertEqual(self.state()["blocked_tasks"], ["T1"])

    def test_quota_signal_pauses_and_preserves_task(self):
        result = self.invoke("limit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.state()["campaign_status"], "paused_quota_or_rate_limit")
        self.assertEqual(self.queue()["tasks"][0]["status"], "pending")
        self.assertEqual(self.state()["completed_tasks"], [])

    def test_interrupted_worker_is_recovered_without_losing_task(self):
        queue = self.queue()
        task = queue["tasks"][0]
        task["status"], task["attempts"], task["worker_pid"] = "running", 1, 99999999
        (self.root / "research/task_queue.json").write_text(json.dumps(queue))
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(x) for x in (self.root / "research/supervisor_events.jsonl").read_text().splitlines()]
        self.assertTrue(any(r.get("event") == "recovered_interrupted_worker" for r in rows))
        self.assertEqual(self.queue()["tasks"][0]["status"], "completed")

    def test_lock_blocks_second_supervisor(self):
        with (self.root / "research/.supervisor.lock").open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.invoke()
        self.assertEqual(result.returncode, 3)

    def test_check_accepts_negative_experiment_ledger_record(self):
        row = {"experiment_id": "EXP-NEG-1", "result": "null effect", "falsification_outcome": "hypothesis weakened"}
        with (self.root / "research/experiment_ledger.jsonl").open("a") as f:
            f.write(json.dumps(row) + "\n")
        # Run the actual checker against an isolated copy of its expected files.
        copy = self.root / "scripts/research_check.py"
        copy.parent.mkdir(exist_ok=True)
        copy.write_text(CHECK.read_text().replace("ROOT = Path(__file__).resolve().parents[1]", f"ROOT = Path({str(self.root)!r})"))
        result = subprocess.run([sys.executable, str(copy)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ledger_records": 1', result.stdout)


if __name__ == "__main__":
    unittest.main()
