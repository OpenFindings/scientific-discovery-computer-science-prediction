"""Frozen design and uncertainty checks for the DP158 boundary diagnostic."""

import json
import math
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_dp158_regime_boundary import DKW_RADIUS, analyze


class Dp158BoundaryTests(unittest.TestCase):
    def test_frozen_design_and_materiality(self):
        root = Path(__file__).resolve().parents[1] / "results/dp158_regime_boundary"
        result = analyze(root)
        self.assertEqual([row["q"] for row in result["rows"]], [0.1, 0.19, 0.3, 0.5])
        self.assertEqual([row["contrast_vs_q010"]["material_under_predeclared_rule"] for row in result["rows"]],
                         [False, True, True, True])
        self.assertGreater(result["rows"][1]["contrast_vs_q010"]["simultaneous_95pct_lower"], 0.01)
        self.assertAlmostEqual(DKW_RADIUS, math.sqrt(math.log(320) / 2_000_000))

    def test_rejects_seed_tampering(self):
        root = Path(__file__).resolve().parents[1] / "results/dp158_regime_boundary"
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory)
            for key in ("q010", "q019", "q030", "q050"):
                (copied / key).mkdir()
                raw = json.loads((root / key / "analysis.json").read_text())
                if key == "q030":
                    raw["parameters"]["rng_seeds"]["P"] = 1
                (copied / key / "analysis.json").write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, "rng_seeds"):
                analyze(copied)


if __name__ == "__main__":
    unittest.main()
