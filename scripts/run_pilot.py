#!/usr/bin/env python3
from pathlib import Path
from research_platform.pilot import run_pilot

if __name__ == "__main__":
    report = run_pilot(Path("results/paper5_pilot.json"))
    print(f"variant={report['variant']} resolved_rate={report['resolved_rate']:.3f}")

