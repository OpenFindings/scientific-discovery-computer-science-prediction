from pathlib import Path
from research_platform.execution_study import run_execution_study

if __name__ == "__main__":
    report = run_execution_study(Path("results/paper5_execution_falsification_pilot.json"))
    for name, summary in report["summaries"].items():
        print(f"{name}: correct={summary['correct_resolutions']}/{summary['n_questions']} "
              f"unsupported={summary['unsupported_conclusions']} "
              f"mean_actions={summary['mean_actions']:.2f}")
