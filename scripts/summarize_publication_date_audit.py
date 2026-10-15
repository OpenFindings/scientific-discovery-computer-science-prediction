#!/usr/bin/env python3
"""Summarize the stratified venue-year audit, preserving unresolved cases."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data/publication_date_audit_sample.jsonl"
SAMPLE_PROFILE = ROOT / "data/publication_date_audit_sample_profile.json"
ADJUDICATIONS = ROOT / "data/publication_date_adjudications.jsonl"
OUTPUT = ROOT / "data/publication_date_audit_summary.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def estimate(bands: list[str], population: dict[str, int], values: dict[str, list[int]]) -> dict:
    total = sum(population.values())
    point = 0.0
    variance = 0.0
    details = {}
    for band in bands:
        vals = values[band]
        n = len(vals)
        p = sum(vals) / n
        weight = population[band] / total
        sample_variance = sum((value - p) ** 2 for value in vals) / (n - 1) if n > 1 else 0.0
        fpc = max(0.0, 1 - n / population[band])
        point += weight * p
        variance += weight**2 * fpc * sample_variance / n
        details[band] = {
            "population_N": population[band],
            "sample_n": n,
            "disagreements": sum(vals),
            "sample_rate": p,
            "population_weight": weight,
        }
    standard_error = variance**0.5
    return {
        "weighted_estimate": point,
        "design_standard_error": standard_error,
        "normal_approx_95_percent_interval": [max(0.0, point - 1.96 * standard_error), min(1.0, point + 1.96 * standard_error)],
        "by_period": details,
    }


def main() -> None:
    sample = read_jsonl(SAMPLE)
    adjudications = read_jsonl(ADJUDICATIONS)
    profile = json.loads(SAMPLE_PROFILE.read_text(encoding="utf-8"))
    bands = list(profile["eligible_by_period"])
    population = profile["eligible_by_period"]
    rows_by_band = {band: [row for row in sample if row["period"] == band] for band in bands}
    records = {row["arxiv_id"]: row for row in adjudications}
    missing_sample_ids = {row["arxiv_id"] for row in sample} - set(records)
    extra_ids = set(records) - {row["arxiv_id"] for row in sample}
    if missing_sample_ids or extra_ids or any(len(rows_by_band[band]) != 8 for band in bands):
        raise ValueError(f"sample/ledger mismatch: missing={missing_sample_ids}, extra={extra_ids}")

    mismatch_values = {band: [] for band in bands}
    unresolved_ids = []
    for band in bands:
        for item in rows_by_band[band]:
            result = records[item["arxiv_id"]]
            if result["venue_year"] is None:
                unresolved_ids.append(item["arxiv_id"])
                mismatch_values[band].append(0)
            else:
                mismatch_values[band].append(int(item["arxiv_year"] != result["venue_year"]))

    lower = estimate(bands, population, mismatch_values)
    upper_values = {band: list(vals) for band, vals in mismatch_values.items()}
    for band in bands:
        for index, item in enumerate(rows_by_band[band]):
            if item["arxiv_id"] in unresolved_ids:
                upper_values[band][index] = 1
    upper = estimate(bands, population, upper_values)
    output = {
        "sample_size": len(sample),
        "population_size_in_eligible_frame": sum(population.values()),
        "eligible_frame_scope": profile["eligibility_rule"],
        "date_comparison": "arXiv submission calendar year versus the source-adjudicated venue/reference year; venue-year ambiguity is separately flagged",
        "known_venue_years": len(sample) - len(unresolved_ids),
        "unresolved_arxiv_ids": unresolved_ids,
        "recorded_venue_year_mismatch_estimate_unresolved_as_match": lower,
        "sensitivity_if_unresolved_is_mismatch": upper,
        "limitations": [
            "This is only the DOI+venue-reference eligible subset of the lexical candidate pool, not all 198,690 candidates or all CS research.",
            "Only 8 records per period were sampled, so design uncertainty is wide.",
            "The point estimate depends on using the adjudicated reference/issue year; online-first and proceedings-event conventions can differ.",
            "A normal-approximation interval is descriptive for this small sample and does not capture source-adjudication errors or screening omissions.",
            "The SHA-256 rank creates a fixed pseudo-random sample; results are conditional on this frozen draw.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sample_size": output["sample_size"],
        "known_venue_years": output["known_venue_years"],
        "unresolved": unresolved_ids,
        "weighted_rate_issue_reference_year": lower["weighted_estimate"],
        "weighted_rate_if_unresolved_disagrees": upper["weighted_estimate"],
        "approx_95_interval": lower["normal_approx_95_percent_interval"],
        "output": str(OUTPUT.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
