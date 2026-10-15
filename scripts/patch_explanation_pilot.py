#!/usr/bin/env python3
"""Run an artifact-only pilot for patch explanation review conditions.

The built-in fixtures test condition construction and blinding only. They are
not observations about developers and cannot produce a human review effect.
An external manifest may be supplied once real Defects4J materials are
available and independently verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[1]


def fixture_manifest() -> list[dict]:
    return [
        {
            "condition_id": "fixture-good",
            "patch_class": "correct",
            "patch_text": "return value == null ? 0 : value.length();",
            "explanation_text": "The patch treats a missing value as an empty collection before reading its length.",
            "behavioral_difference": "null input returns 0 instead of raising a null dereference.",
            "explanation_grounded": True,
            "source": "synthetic_engineering_fixture",
        },
        {
            "condition_id": "fixture-defective",
            "patch_class": "incorrect_plausible",
            "patch_text": "return value == null ? 1 : value.length();",
            "explanation_text": "The patch treats a missing value as an empty collection before reading its length.",
            "behavioral_difference": "null input returns 1, which changes the documented empty-value behavior.",
            "explanation_grounded": False,
            "source": "synthetic_engineering_fixture",
        },
    ]


def validate_materials(rows: list[dict], seed: int = 20261015) -> dict:
    required = {"condition_id", "patch_class", "patch_text", "explanation_text", "behavioral_difference", "explanation_grounded", "source"}
    errors: list[str] = []
    ids: set[str] = set()
    public_rows = 0
    for row in rows:
        missing = sorted(required - row.keys())
        if missing:
            errors.append(f"{row.get('condition_id', '<missing-id>')}: missing {missing}")
        cid = str(row.get("condition_id", ""))
        if not cid or cid in ids:
            errors.append(f"duplicate or empty condition_id: {cid!r}")
        ids.add(cid)
        if row.get("source") != "synthetic_engineering_fixture":
            public_rows += 1
        if not str(row.get("patch_text", "")).strip():
            errors.append(f"{cid}: empty patch")
        if not str(row.get("explanation_text", "")).strip():
            errors.append(f"{cid}: empty explanation")
        if not str(row.get("behavioral_difference", "")).strip():
            errors.append(f"{cid}: missing behavioral difference")

    rng = Random(seed)
    presentations = []
    for row in rows:
        arms = ["patch_only", "patch_plus_explanation"]
        rng.shuffle(arms)
        for arm in arms:
            presentation = {
                "presentation_id": hashlib.sha256(f"{seed}:{row.get('condition_id')}:{arm}".encode()).hexdigest()[:16],
                "condition_id": row.get("condition_id"),
                "arm": arm,
                "patch_text": row.get("patch_text"),
            }
            if arm == "patch_plus_explanation":
                presentation["explanation_text"] = row.get("explanation_text")
                presentation["behavioral_difference"] = row.get("behavioral_difference")
            presentations.append(presentation)
    leaked = any(key in presentation for presentation in presentations for key in ("patch_class", "explanation_grounded", "source"))
    return {
        "seed": seed,
        "rows": len(rows),
        "public_rows": public_rows,
        "synthetic_fixture_rows": len(rows) - public_rows,
        "presentation_rows": len(presentations),
        "unique_presentation_ids": len({p["presentation_id"] for p in presentations}),
        "blinding_checks": {"gold_label_absent": not leaked, "condition_ids_preserved": len(ids) == len(rows)},
        "errors": errors,
        "presentations": presentations,
    }


def environment_audit() -> dict:
    java = shutil.which("java")
    java_version_ok = False
    java_version_output = None
    if java:
        probe = subprocess.run([java, "-version"], text=True, capture_output=True, check=False)
        java_version_ok = probe.returncode == 0
        java_version_output = (probe.stderr or probe.stdout).splitlines()[:2]
    return {
        "platform": platform.platform(),
        "defects4j_cli": shutil.which("defects4j"),
        "java": java,
        "java_runtime_usable": java_version_ok,
        "java_version_probe": java_version_output,
        "javac": shutil.which("javac"),
        "docker": shutil.which("docker"),
        "public_benchmark": {
            "name": "Defects4J",
            "version_reference": "3.0.1",
            "active_bug_count_claimed_by_official_site": 854,
            "source_url": "https://defects4j.org/",
            "patch_index_url": "https://github.com/program-repair/defects4j-dissection/blob/master/defects4j-patch.md",
            "correctness_caveat": "Passing developer tests is not semantic correctness; correct/plausible labels require independent audit.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/patch_explanation_feasibility.json")
    args = parser.parse_args()
    if args.manifest:
        rows = json.loads(args.manifest.read_text())
        if not isinstance(rows, list):
            raise SystemExit("manifest must be a JSON list")
    else:
        rows = fixture_manifest()
    materials = validate_materials(rows)
    environment = environment_audit()
    real_execution_ready = bool(environment["defects4j_cli"] and environment["java_runtime_usable"])
    result = {
        "protocol": "research/patch_explanation_protocol_v1.md",
        "evidence_level": 4 if materials["public_rows"] else 0,
        "pilot_type": "artifact_and_feasibility_only",
        "human_outcomes_measured": False,
        "automated_judgments_are_human_substitutes": False,
        "materials": materials,
        "environment": environment,
        "real_benchmark_execution_ready": real_execution_ready,
        "decision": "go_for_material_protocol_no_go_for_real_benchmark_execution" if not real_execution_ready else "go_for_bounded_real_materials_pilot",
        "uncertainty": [
            "Fixture checks are synthetic engineering diagnostics, not developer evidence.",
            "Defects4J patch plausibility and semantic correctness still require version-pinned test execution and independent review.",
            "No claim about review accuracy, decision time, confidence calibration or automation bias is supported.",
        ],
        "next_falsifiable_action": "Acquire a version-pinned Defects4J checkout with Java 11 in an authorized local environment; verify a small correct/plausible subset and generate blinded conditions before any participant study.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("decision", "evidence_level", "real_benchmark_execution_ready", "human_outcomes_measured")}, indent=2))
    return 0 if not materials["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
