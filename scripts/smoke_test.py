from pathlib import Path
from tempfile import TemporaryDirectory

from research_platform.benchmark import controlled_cases
from research_platform.belief import update_beliefs
from research_platform.executor import SafeExecutor
from research_platform.models import Evidence, EvidenceKind
from research_platform.pilot import run_pilot

cases = controlled_cases()
action = cases[0].question.actions[0]
evidence = Evidence("e", action.id, EvidenceKind.TEST_RESULT, {"outcome": "fail"}, "x", "1", "t", "x")
assert update_beliefs({"H-null": .5, "H-index": .5}, action, evidence)["H-null"] < 1
with TemporaryDirectory() as tmp:
    try:
        SafeExecutor().run("x", ["sh", "-c", "echo unsafe"], tmp)
    except PermissionError:
        pass
    else:
        raise AssertionError("unsafe command was accepted")
    report = run_pilot(Path(tmp) / "report.json")
    assert report["resolved_rate"] == 1.0
print("smoke tests passed")

