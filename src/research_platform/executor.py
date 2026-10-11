from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Optional, Set


@dataclass(frozen=True)
class ExecutionResult:
    action_id: str
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool


class SafeExecutor:
    """Small allow-listed executor; generated commands are never passed through a shell."""

    def __init__(self, allowed_programs: Optional[Set[str]] = None, timeout_seconds: float = 10.0):
        self.allowed_programs = allowed_programs or {"python", "python3"}
        self.timeout_seconds = timeout_seconds

    def run(self, action_id: str, command: list[str], cwd: str) -> ExecutionResult:
        if not command or command[0] not in self.allowed_programs:
            raise PermissionError(f"program is not allow-listed: {command[0] if command else None}")
        started = time.monotonic()
        try:
            completed = subprocess.run(command, cwd=cwd, shell=False, capture_output=True,
                                       text=True, timeout=self.timeout_seconds, check=False)
            return ExecutionResult(action_id, tuple(command), completed.returncode,
                                   completed.stdout, completed.stderr, time.monotonic() - started, False)
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(action_id, tuple(command), -1, exc.stdout or "",
                                   exc.stderr or "", time.monotonic() - started, True)
