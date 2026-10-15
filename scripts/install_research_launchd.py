#!/usr/bin/env python3
"""Create or remove the bounded macOS launchd job for the research supervisor.

This tool only manages a per-user LaunchAgent. It never changes credentials or
starts a worker by itself; launchd invokes one finite supervisor activation at
the configured interval. Use --print to inspect the plist before installation.
"""
from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import subprocess
from pathlib import Path


LABEL = "com.nonameisready.scientific-discovery.supervisor"


def build_plist(root: Path, python: str | None = None, codex: str | None = None, interval: int = 900) -> dict:
    root = root.resolve()
    python = python or shutil.which("python3.12") or shutil.which("python3") or "/usr/bin/python3"
    codex = codex or shutil.which("codex") or "codex"
    log_dir = root / "research" / "logs"
    return {
        "Label": LABEL,
        "ProgramArguments": [python, str(root / "scripts" / "research_supervisor.py"), "--start", "--max-rounds", "1"],
        "WorkingDirectory": str(root),
        "EnvironmentVariables": {
            "PATH": ":".join(filter(None, [str(Path(codex).parent) if Path(codex).is_absolute() else None,
                                               "/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"])),
            "RESEARCH_SUPERVISOR_CODEX_BIN": codex,
            "PYTHONPATH": str(root / "src"),
        },
        "RunAtLoad": True,
        "StartInterval": max(300, int(interval)),
        "ThrottleInterval": 300,
        "ProcessType": "Background",
        "LowPriorityIO": True,
        "StandardOutPath": str(log_dir / "launchd.out.log"),
        "StandardErrorPath": str(log_dir / "launchd.err.log"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--interval-seconds", type=int, default=900)
    parser.add_argument("--print", action="store_true", dest="print_plist")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--plist-path", type=Path)
    args = parser.parse_args()
    if sum(bool(x) for x in (args.print_plist, args.install, args.uninstall)) != 1:
        parser.error("choose exactly one of --print, --install, or --uninstall")
    if os.uname().sysname != "Darwin":
        parser.error("launchd installation is supported only on macOS")
    plist_path = (args.plist_path or Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist").expanduser()
    if args.uninstall:
        uid = str(os.getuid())
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{LABEL}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if plist_path.exists():
            plist_path.unlink()
        print(f"uninstalled {LABEL} ({plist_path})")
        return 0
    payload = build_plist(args.repo_root, interval=args.interval_seconds)
    if args.print_plist:
        print(plistlib.dumps(payload).decode())
        return 0
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_bytes(plistlib.dumps(payload))
    uid = str(os.getuid())
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{LABEL}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(plist_path)], check=True)
    print(f"installed and bootstrapped {LABEL} ({plist_path}); one bounded activation every {max(300, args.interval_seconds)}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
