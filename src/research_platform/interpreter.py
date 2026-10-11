from __future__ import annotations

from .executor import ExecutionResult


def interpret_test_result(result: ExecutionResult, *, source_version: str) -> dict:
    """Deterministic interpretation. Raw output remains the authoritative observation."""
    if result.timed_out:
        outcome = "timeout"
    elif result.exit_code == 0:
        outcome = "pass"
    else:
        outcome = "fail"
    return {"outcome": outcome, "exit_code": result.exit_code, "timed_out": result.timed_out,
            "stdout": result.stdout, "stderr": result.stderr, "source_version": source_version}

