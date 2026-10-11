from __future__ import annotations

import os
import signal
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
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
    sandbox_backend: str


class SafeExecutor:
    """Run registered Python probes in an OS sandbox with no shell or network access.

    On macOS, sandbox-exec denies network access and writes outside the action's
    scratch directory. Other platforms fail closed until a supported sandbox
    backend is configured; subprocess cwd alone is not treated as isolation.
    """

    def __init__(self, allowed_programs: Optional[Set[str]] = None,
                 timeout_seconds: float = 10.0, output_limit_bytes: int = 64_000,
                 cpu_seconds: int = 5, memory_bytes: int = 512 * 1024 * 1024,
                 allow_managed_outer_sandbox: bool = False):
        self.allowed_programs = allowed_programs or {sys.executable, "python", "python3"}
        self.timeout_seconds = timeout_seconds
        self.output_limit_bytes = output_limit_bytes
        self.cpu_seconds = cpu_seconds
        self.memory_bytes = memory_bytes
        self.allow_managed_outer_sandbox = allow_managed_outer_sandbox

    @staticmethod
    def _sandbox_command(command: list[str], scratch: Path, root: Path) -> tuple[list[str], str]:
        if sys.platform != "darwin":
            raise RuntimeError("no supported OS sandbox backend is available on this platform")
        python = str(Path(command[0]).resolve())
        def quote(path: str) -> str:
            return path.replace("\\", "\\\\").replace('"', '\\"')

        scratch_path = quote(str(scratch.resolve()))
        root_path = quote(str(root.resolve()))
        python_path = quote(python)
        runtime_paths = sorted({str(Path(sys.prefix).resolve()), str(Path(sys.base_prefix).resolve())})
        read_rules = ["(subpath \"/System\")", "(subpath \"/usr/lib\")",
                      "(subpath \"/usr/share/locale\")", "(subpath \"/Library/Developer/CommandLineTools\")",
                      f'(subpath "{root_path}")']
        read_rules.extend(f'(subpath "{quote(path)}")' for path in runtime_paths)
        profile = " ".join((
            "(version 1)", "(deny default)", "(allow process-fork)",
            f'(allow process-exec (literal "{python_path}"))',
            f'(allow file-read* {" ".join(read_rules)})',
            f'(allow file-write* (subpath "{scratch_path}"))',
            "(deny network*)", "(allow sysctl-read)", "(allow mach-lookup)",
        ))
        return ["/usr/bin/sandbox-exec", "-p", profile, "--", command[0], *command[1:]], "macos-sandbox-exec"

    @staticmethod
    def _resource_limits(cpu_seconds: int, memory_bytes: int):
        def apply() -> None:
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
                resource.setrlimit(resource.RLIMIT_FSIZE, (2_000_000, 2_000_000))
                resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
                if hasattr(resource, "RLIMIT_AS"):
                    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            except (ImportError, OSError, ValueError):
                pass
        return apply

    def run(self, action_id: str, command: list[str], cwd: str,
            sandbox_root: Optional[str] = None) -> ExecutionResult:
        if not command or command[0] not in self.allowed_programs:
            raise PermissionError(f"program is not allow-listed: {command[0] if command else None}")
        workdir = Path(cwd).resolve(strict=True)
        root = Path(sandbox_root or cwd).resolve(strict=True)
        if workdir != root and root not in workdir.parents:
            raise PermissionError("working directory must be inside the declared sandbox root")
        if not workdir.is_dir():
            raise NotADirectoryError(workdir)
        # Scratch is the only writable path granted to the child process.
        scratch = root / ".action-scratch"
        if scratch.is_symlink():
            raise PermissionError("action scratch directory cannot be a symlink")
        scratch.mkdir(exist_ok=True)
        executable = command[0] if os.path.isabs(command[0]) else shutil.which(command[0])
        if executable is None:
            raise FileNotFoundError(f"allow-listed executable was not found: {command[0]}")
        normalized_command = [executable, *command[1:]]
        wrapped, backend = self._sandbox_command(normalized_command, scratch, root)
        environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
                       "HOME": str(scratch), "TMPDIR": str(scratch), "PYTHONDONTWRITEBYTECODE": "1"}
        started = time.monotonic()
        process = subprocess.Popen(wrapped, cwd=workdir, env=environment, shell=False,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True,
                                   preexec_fn=self._resource_limits(self.cpu_seconds, self.memory_bytes))
        timed_out = False
        try:
            stdout_bytes, stderr_bytes = process.communicate(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            stdout_bytes, stderr_bytes = process.communicate()
        if (not timed_out and process.returncode != 0 and self.allow_managed_outer_sandbox
                and b"sandbox_apply: Operation not permitted" in stderr_bytes):
            # The caller must be running inside an independently enforced managed sandbox.
            # This opt-in cannot be inferred in a normal standalone Python process.
            process = subprocess.Popen(normalized_command, cwd=workdir, env=environment, shell=False,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True,
                                       preexec_fn=self._resource_limits(self.cpu_seconds, self.memory_bytes))
            try:
                stdout_bytes, stderr_bytes = process.communicate(timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                stdout_bytes, stderr_bytes = process.communicate()
            backend = "managed-outer-sandbox-fallback"
        elapsed = time.monotonic() - started
        stdout_bytes = stdout_bytes[:self.output_limit_bytes]
        stderr_bytes = stderr_bytes[:self.output_limit_bytes]
        return ExecutionResult(action_id, tuple(normalized_command), process.returncode if not timed_out else -1,
                               stdout_bytes.decode("utf-8", "replace"),
                               stderr_bytes.decode("utf-8", "replace"), elapsed, timed_out, backend)
