#!/usr/bin/env python3
"""Render source-backed CS direction dossiers without unvalidated scores."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_ACTION = ("title", "procedure", "budget", "supports_if", "weakens_if", "prerequisite")


def load_findings(data_dir: Path) -> dict[str, dict]:
    findings: dict[str, dict] = {}
    for path in sorted(data_dir.glob("research_findings*.jsonl")):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            finding_id = record["finding_id"]
            if finding_id in findings:
                raise ValueError(f"duplicate finding {finding_id} in {path}:{number}")
            record["_source_path"] = str(path)
            findings[finding_id] = record
    return findings


def validate_decisions(decisions: list[dict], findings: dict[str, dict]) -> None:
    seen: set[str] = set()
    for decision in decisions:
        direction_id = decision.get("direction_id")
        if not direction_id or direction_id in seen:
            raise ValueError(f"missing or duplicate direction ID: {direction_id}")
        seen.add(direction_id)
        finding = findings.get(decision.get("finding_id"))
        if finding is None:
            raise ValueError(f"unknown finding for {direction_id}: {decision.get('finding_id')}")
        for field in ("stage", "reason_to_test", "stop_rule"):
            if not decision.get(field):
                raise ValueError(f"{direction_id} missing {field}")
        if len(decision.get("competing_hypotheses", [])) < 2:
            raise ValueError(f"{direction_id} needs at least two competing hypotheses")
        action = decision.get("next_action", {})
        for field in REQUIRED_ACTION:
            if not action.get(field):
                raise ValueError(f"{direction_id} action missing {field}")
        sources = finding.get("sources", [])
        urls = {source.get("url") for source in sources if source.get("url")}
        if len(urls) < 2 or any(not source.get("locators") for source in sources):
            raise ValueError(f"{direction_id} needs at least two located source records")
        if not finding.get("falsifiable_question") or not finding.get("primary_outcome"):
            raise ValueError(f"{direction_id} has no falsifiable question or outcome")
        if any(key in decision for key in ("paper3_probability", "paper4_utility", "opportunity_score")):
            raise ValueError(f"{direction_id} contains an unvalidated numeric score")


def render(decisions: list[dict], findings: dict[str, dict]) -> str:
    lines = [
        "# CS research directions: source-backed decision dossiers",
        "",
        "Generated from `data/direction_decisions.json` and source-located records in",
        "`data/research_findings*.jsonl`. These are decisions to run the next",
        "check, not validated Paper 3 forecasts or claims of global novelty.",
        "Paper 3 has no CS historical labels or calibrated model in this worktree;",
        "Paper 4's action values have not been validated on these questions.",
        "The source-method audit is in `docs/paper3_paper4_source_audit.md`.",
        "",
    ]
    for decision in decisions:
        finding = findings[decision["finding_id"]]
        action = decision["next_action"]
        lines.extend([
            f"## {decision['direction_id']}", "",
            f"**Stage:** {decision['stage']}.", "",
            f"**Question:** {finding['falsifiable_question']}", "",
            f"**Why test it:** {decision['reason_to_test']}", "",
            f"**Measured outcome:** {finding['primary_outcome']}", "",
        ])
        if decision.get("observed_feasibility"):
            lines.extend([f"**Observed feasibility:** {decision['observed_feasibility']}", ""])
        lines.extend(["**Competing explanations:**", ""])
        for hypothesis in decision["competing_hypotheses"]:
            lines.append(f"- {hypothesis}")
        lines.extend([
            "",
            "**Source trail:**", "",
        ])
        for source in finding["sources"]:
            lines.append(f"- [{source['title']}]({source['url']}): {source['locators'][0]}.")
        lines.extend([
            "", f"**Next action:** {action['title']}. {action['procedure']}", "",
            f"**Budget rule:** {action['budget']}", "",
            f"**Action is informative if:** {action['supports_if']}", "",
            f"**Evidence against the working explanation:** {action['weakens_if']}", "",
            f"**Prerequisite:** {action['prerequisite']}", "",
            f"**Stop rule:** {decision['stop_rule']}", "",
            f"**Evidence record:** `{finding['_source_path']}`. Source independence,",
            "artifact compatibility, and global novelty remain to be checked.", "",
        ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decisions", type=Path, default=Path("data/direction_decisions.json"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("docs/cs_direction_shortlist.md"))
    args = parser.parse_args()
    decisions = json.loads(args.decisions.read_text())
    findings = load_findings(args.data_dir)
    validate_decisions(decisions, findings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(decisions, findings) + "\n")
    print(json.dumps({"directions": len(decisions), "finding_records": len(findings),
                      "output": str(args.output), "status": "source_backed_unvalidated"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
