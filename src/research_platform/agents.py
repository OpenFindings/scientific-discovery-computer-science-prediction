"""Model-policy interface for evidence-guided and adversarial research agents.

The model selects registered action identifiers only. Commands, observations,
interpretations, and Bayesian updates remain controlled by the research runtime.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .belief import entropy, update_beliefs
from .executor import SafeExecutor
from .models import Action, Evidence, EvidenceKind


class ModelPolicy(Protocol):
    def select_action(self, context: dict[str, Any]) -> str:
        """Return one registered action ID from context['available_actions']."""

    def select_falsification_action(self, context: dict[str, Any]) -> str:
        """Return one available registered action intended to challenge the leader."""


@dataclass(frozen=True)
class AgentRun:
    question_id: str
    beliefs: dict[str, float]
    resolved: bool
    trace: tuple[dict[str, Any], ...]


class ResearchAgent:
    """Execute validated experiments selected by a pluggable model policy."""

    def __init__(self, policy: ModelPolicy, executor: SafeExecutor):
        self.policy = policy
        self.executor = executor

    def run(self, *, question_id: str, objective: str, hypotheses: dict[str, str],
            beliefs: dict[str, float], actions: list[Action], commands: dict[str, list[str]],
            workspace: str | Path, max_actions: int = 3, use_falsifier: bool = True,
            resolution_threshold: float = .80, minimum_probe_families: int = 2,
            source_version: str = "unversioned") -> AgentRun:
        action_by_id = {action.id: action for action in actions}
        if len(action_by_id) != len(actions) or set(action_by_id) != set(commands):
            raise ValueError("each registered action must have exactly one fixed command")
        available = list(action_by_id)
        current = dict(beliefs)
        history: list[dict[str, Any]] = []
        root = Path(workspace).resolve(strict=True)

        for step in range(max_actions):
            if not available:
                break
            context = {"question_id": question_id, "objective": objective,
                       "hypotheses": hypotheses, "beliefs": current.copy(),
                       "evidence": [entry["evidence_summary"] for entry in history],
                       "available_actions": available.copy(), "step": step + 1}
            if use_falsifier and history:
                context["leading_hypothesis"] = max(current, key=current.get)
                action_id = self.policy.select_falsification_action(context)
                role = "falsifier"
            else:
                action_id = self.policy.select_action(context)
                role = "planner"
            if action_id not in available:
                raise ValueError(f"model selected an unavailable action ID: {action_id}")

            action = action_by_id[action_id]
            before = current.copy()
            execution = self.executor.run(action_id, commands[action_id], str(root), str(root))
            if execution.timed_out:
                outcome: dict[str, Any] = {"outcome": "timeout"}
            elif execution.exit_code != 0:
                outcome = {"outcome": "execution_error", "exit_code": execution.exit_code}
            else:
                try:
                    outcome = json.loads(execution.stdout.strip().splitlines()[-1])
                    if not isinstance(outcome, dict) or "outcome" not in outcome:
                        raise ValueError("observation must be an object with an outcome")
                except (json.JSONDecodeError, IndexError, ValueError) as exc:
                    raise ValueError(f"registered action returned an invalid observation: {exc}") from exc

            evidence = Evidence(
                id=f"{question_id}:{step + 1}:{action_id}", action_id=action_id,
                kind=EvidenceKind.TEST_RESULT, observation=outcome,
                source="registered-experiment", source_version=source_version,
                timestamp=datetime.now(timezone.utc).isoformat(),
                independent_group=question_id,
                uncertainty=0.0 if outcome["outcome"] not in {"timeout", "execution_error"} else 1.0,
            )
            update_skipped = outcome["outcome"] in {"timeout", "execution_error"}
            if not update_skipped:
                current = update_beliefs(current, action, evidence)
            counterevidence = bool(role == "falsifier" and
                                   current.get(max(before, key=before.get), 0.0)
                                   < before[max(before, key=before.get)])
            history.append({
                "action_id": action_id, "role": role, "observation": outcome,
                "evidence_summary": {"action_id": action_id, "outcome": outcome["outcome"]},
                "beliefs_before": before, "beliefs_after": current.copy(),
                "entropy_after": entropy(current), "counterevidence": counterevidence,
                "belief_update_skipped": update_skipped,
                "command": list(execution.command), "stdout": execution.stdout,
                "stderr": execution.stderr, "exit_code": execution.exit_code,
                "timed_out": execution.timed_out, "sandbox_backend": execution.sandbox_backend,
                "duration_seconds": execution.duration_seconds,
            })
            available.remove(action_id)
            if (max(current.values()) >= resolution_threshold
                    and len(history) >= minimum_probe_families
                    and not counterevidence):
                break

        resolved = (bool(history) and max(current.values()) >= resolution_threshold
                    and len({entry["action_id"] for entry in history}) >= minimum_probe_families)
        return AgentRun(question_id, current, resolved, tuple(history))
