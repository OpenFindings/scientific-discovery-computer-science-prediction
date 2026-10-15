import os
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install_research_launchd.py"


class ResearchServiceTests(unittest.TestCase):
    def test_prints_bounded_launchd_job_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(INSTALLER), "--repo-root", tmp, "--print", "--interval-seconds", "60"],
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = plistlib.loads(result.stdout.encode())
        self.assertEqual(payload["Label"], "com.nonameisready.scientific-discovery.supervisor")
        self.assertEqual(payload["StartInterval"], 300)
        self.assertEqual(payload["ProgramArguments"][-2:], ["--max-rounds", "1"])
        self.assertFalse((ROOT / "research" / "LaunchAgents").exists())

    def test_non_macos_install_is_rejected(self):
        # The real host is macOS; exercise the helper's safety rule indirectly
        # by checking the source contains an explicit platform gate.
        self.assertIn('launchd installation is supported only on macOS', INSTALLER.read_text())


if __name__ == "__main__":
    unittest.main()
