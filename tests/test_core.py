from pathlib import Path
import pytest
from research_platform.belief import normalize, update_beliefs
from research_platform.executor import SafeExecutor
from research_platform.models import Evidence, EvidenceKind
from research_platform.benchmark import controlled_cases
from research_platform.pilot import run_pilot


def test_belief_update_changes_mass_toward_supported_hypothesis():
    action = controlled_cases()[0].question.actions[0]
    evidence = Evidence("e", action.id, EvidenceKind.TEST_RESULT, {"outcome": "fail"}, "x", "1", "t", "x")
    beliefs = update_beliefs({"H-null": .5, "H-index": .5}, action, evidence)
    assert beliefs["H-null"] < beliefs["H-index"]


def test_executor_rejects_untrusted_program(tmp_path: Path):
    with pytest.raises(PermissionError):
        SafeExecutor().run("a", ["sh", "-c", "echo unsafe"], str(tmp_path))


def test_pilot_is_reproducible(tmp_path: Path):
    one = run_pilot(tmp_path / "one.json")
    two = run_pilot(tmp_path / "two.json")
    assert one == two
    assert one["resolved_rate"] == 1.0

