import argparse
from pathlib import Path
from research_platform.execution_study import run_execution_study

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--managed-outer-sandbox", action="store_true",
                        help="explicitly use the already-enforced parent sandbox when nested OS sandboxing is blocked")
    options = parser.parse_args()
    report = run_execution_study(Path("results/paper5_execution_falsification_pilot.json"),
                                 allow_managed_outer_sandbox=options.managed_outer_sandbox)
    for name, summary in report["summaries"].items():
        print(f"{name}: correct={summary['correct_resolutions']}/{summary['n_questions']} "
              f"unsupported={summary['unsupported_conclusions']} "
              f"mean_actions={summary['mean_actions']:.2f}")
