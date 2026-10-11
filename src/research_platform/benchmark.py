from __future__ import annotations

from dataclasses import dataclass
from .models import Action, Hypothesis, ResearchQuestion


@dataclass(frozen=True)
class BenchmarkCase:
    question: ResearchQuestion
    truth: str


def controlled_cases() -> tuple[BenchmarkCase, ...]:
    """Tiny transparent benchmark: deterministic software failures with competing causes.

    This is a pilot benchmark, not a claim about SWE-bench or any external dataset.
    """
    cases = []
    for i, truth in enumerate(("null_guard", "off_by_one", "null_guard", "off_by_one"), 1):
        hypotheses = (Hypothesis("H-null", "missing null guard causes failure", .5),
                      Hypothesis("H-index", "off-by-one causes failure", .5))
        actions = (
            Action("test-null", "run null-input regression", ("H-null",), .4, .95,
                   {"pass": {"H-null": .1, "H-index": .9}, "fail": {"H-null": .9, "H-index": .1}}),
            Action("test-index", "run boundary-index regression", ("H-index",), .4, .95,
                   {"pass": {"H-null": .9, "H-index": .1}, "fail": {"H-null": .1, "H-index": .9}}),
        )
        question = ResearchQuestion(f"pilot-{i}", "software-engineering",
                                    "identify the causal failure mechanism", hypotheses, actions,
                                    {"max_actions": 2, "timeout_seconds": 2}, "hidden pilot manifest")
        cases.append(BenchmarkCase(question, truth))
    return tuple(cases)
