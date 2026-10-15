#!/usr/bin/env python3
"""Create a non-destructive inventory of tracked changes and untracked files.

The manifest is intentionally about the current Git working tree, not every
file in the repository.  It records hashes for integrity and a conservative
storage recommendation; it never uploads, deletes, stages, or changes files.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "worktree_reconciliation_manifest.json"


def git_status() -> dict[str, str]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z"], cwd=ROOT
    )
    records = raw.decode("utf-8", "surrogateescape").split("\0")
    result: dict[str, str] = {}
    i = 0
    while i < len(records):
        record = records[i]
        if not record:
            i += 1
            continue
        code, path = record[:2], record[3:]
        # Porcelain v1 uses a second path for renames/copies. Preserve both.
        if code[0] in "RC" or code[1] in "RC":
            if i + 1 < len(records) and records[i + 1]:
                path = f"{path} -> {records[i + 1]}"
                i += 1
        result[path] = code
        i += 1
    return result


def classify(path: str, size: int, status: str) -> tuple[str, str, str]:
    lower = path.lower()
    name = Path(path).name.lower()
    if any(x in lower for x in ("credential", "secret", ".env", ".pem", ".key")):
        return "credential_or_sensitive_name", "retain_local_restricted", "sensitive-name safety rule"
    if lower.startswith(".wrangler/") or lower.startswith("research/logs/"):
        return "temporary_or_runtime_log", "retain_local_only", "local runtime/cache path"
    if lower.startswith("research/worker_runs/") or name in {"container.id"}:
        return "temporary_or_runtime_log", "retain_local_only", "supervisor/worker execution trace"
    if lower == "research/.supervisor.lock" or name.endswith((".log", ".db", ".db-journal")):
        return "temporary_or_runtime_log", "retain_local_only", "runtime database/lock/log"
    if lower.startswith("data/fulltexts/") or lower.endswith((".pdf", ".zip", ".tar", ".gz")) and lower.startswith("data/"):
        return "restricted_or_large_dataset", "retain_local_and_authorized_object_storage_only", "raw/full-text or compressed corpus data"
    if lower.endswith((".jsonl", ".jsonl.gz")) and lower.startswith("data/") and size > 1_000_000:
        return "large_research_dataset", "retain_local_or_authorized_object_storage_only", "large derived corpus/ledger"
    if lower.startswith("results/") and (size > 1_000_000 or "/logs/" in lower):
        return "experiment_output_or_raw_trace", "retain_local_only", "large/raw experiment output"
    if lower.startswith("results/"):
        if name.endswith((".json", ".md", ".txt")) and size <= 1_000_000:
            return "experiment_output_or_reproducibility_record", "version_if_explicitly_safe", "small derived result or audit record"
        return "experiment_output_or_raw_trace", "retain_local_only", "raw or intermediate experiment output"
    if lower.startswith("papers/"):
        return "manuscript_or_reproducibility_record", "version", "research manuscript/materials"
    if lower.startswith(("scripts/", "src/", "tests/", "configs/")) or lower in {"dashboard.py"}:
        return "source_code_or_configuration", "version", "reproducible project source"
    if lower.startswith(("docs/", "reports/")) or lower in {"research/state.json", "research/task_queue.json", "research/supervisor_state.json", "research/supervisor_events.jsonl", "research/tracks/experiments/state.json", "research/tracks/experiments/task_queue.json", "research/tracks/forecasting/state.json", "research/tracks/forecasting/task_queue.json", "research_status.md", ".gitignore"}:
        return "documentation_or_research_record", "version", "small reproducible/audit record"
    if lower.startswith("data/"):
        return "research_manifest_or_derived_record", "version_if_small_else_retain_local", "data manifest or derived research record"
    return "unclassified", "manual_review", "conservative fallback"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    statuses = git_status()
    entries = []
    for rel, status in sorted(statuses.items()):
        if " -> " in rel:
            candidates = rel.split(" -> ")
            path = Path(candidates[-1])
        else:
            path = Path(rel)
        absolute = ROOT / path
        paths = [path]
        if absolute.is_dir():
            paths = [candidate.relative_to(ROOT) for candidate in absolute.rglob("*") if candidate.is_file()]
        for path in paths:
            rel = path.as_posix()
            absolute = ROOT / path
            item = {
                "path": rel,
                "git_status": status,
                "exists": absolute.exists(),
                "size_bytes": absolute.stat().st_size if absolute.is_file() else None,
                "sha256": sha256(absolute) if absolute.is_file() else None,
            }
            category, disposition, provenance = classify(
                rel, item["size_bytes"] or 0, status
            )
            item.update(
                category=category,
                recommended_disposition=disposition,
                provenance_basis=provenance,
            )
            entries.append(item)
    output = {
        "schema_version": 1,
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "workspace": str(ROOT),
        "comparison_clone": "/Users/amao/scientific-discovery-computer-science",
        "scope": "all tracked modifications and untracked paths reported by git status --porcelain=v1",
        "notes": [
            "No files were staged, deleted, uploaded, or modified by this inventory.",
            "Raw/full-text data and runtime traces are explicitly excluded from versioning recommendations.",
            "Authorized object-storage disposition is conditional on the existing ai4cs/R2 receipts and must not be inferred for files without a receipt.",
        ],
        "entries": entries,
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
