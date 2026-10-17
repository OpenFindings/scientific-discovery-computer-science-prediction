#!/usr/bin/env python3
"""Claude reference rater (amendment 4): build prompts, ingest replies, analyze.

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment4_claude_rater.md.
Rating itself is done by fresh Claude subagents; this script never calls a model.

    python3 scripts/run_cs_claude_rater.py prompt <run> <batch>       # print exact prompt
    python3 scripts/run_cs_claude_rater.py ingest <run> <batch> <reply_file> <tool_uses>
    python3 scripts/run_cs_claude_rater.py analyze
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/cs_forecast_v1"
RAW = RES / "claude_rater_raw.jsonl"
BATCH, RUNS = 40, 2

_spec = importlib.util.spec_from_file_location("gpt", ROOT / "scripts/run_cs_llm_rater.py")
gpt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gpt)

WRAPPER = """

You are rating a batch of 40 papers. Rate each paper independently on its own merits.
Do not use any tools: do not read files, run commands or search the web. Use only the text below.
Reply with only a JSON array (no prose, no code fence) of 40 objects, one per item, in order:
{"item": <item number>, "rationale": "<at most 50 words>", "label": <0|1|2|3>,
 "recognized": <true|false>, "first_author_surname": "<surname>" or null}
"""


def batch_items(b: int) -> list[tuple[int, dict]]:
    items = gpt.load_items()
    return [(i + 1, items[i]) for i in range((b - 1) * BATCH, b * BATCH)]


def prompt(run: int, b: int) -> str:
    parts = [gpt.SYSTEM.rstrip() + WRAPPER]
    for n, it in batch_items(b):
        parts.append(f"\n=== Item {n} ===\n" + gpt.USER_TEMPLATE.format(
            year=it["year"], title=it["title"], abstract=it["abstract"]))
    return "".join(parts)


def parse(text: str, b: int) -> list[dict] | None:
    t = text.strip()
    t = t[t.find("["): t.rfind("]") + 1] if "[" in t else t
    try:
        arr = json.loads(t)
    except json.JSONDecodeError:
        return None
    want = [n for n, _ in batch_items(b)]
    if [o.get("item") for o in arr] != want:
        return None
    ok = all(o.get("label") in (0, 1, 2, 3) and isinstance(o.get("recognized"), bool)
             for o in arr)
    return arr if ok else None


def ingest(run: int, b: int, reply_file: str, tool_uses: int) -> None:
    text = Path(reply_file).read_text()
    arr = parse(text, b)
    rec = {"run": run, "batch": b, "at": datetime.now(timezone.utc).isoformat(),
           "tool_uses": tool_uses, "parsed_ok": arr is not None and tool_uses <= 1,
           "reply": text}
    with open(RAW, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps({"run": run, "batch": b, "parsed_ok": rec["parsed_ok"],
                      "n": len(arr) if arr else 0}))


def primary_by_run() -> dict[int, dict[str, dict]]:
    items = gpt.load_items()
    out = {r: {} for r in range(1, RUNS + 1)}
    for line in RAW.read_text().splitlines():
        rec = json.loads(line)
        if not rec["parsed_ok"]:
            continue
        for o in parse(rec["reply"], rec["batch"]):
            out[rec["run"]][items[o["item"] - 1]["id"]] = o
    return out


def analyze() -> None:
    by_run = primary_by_run()
    # reuse amendment 3's analysis on Claude replies: swap its data sources, keep its functions
    gpt.RUNS = RUNS
    gpt.MODEL = "claude (subagent; identifier reported in chat, not stored)"
    gpt.TEMPERATURE = None
    gpt.raw_records = lambda: [{"run": r, "paper_id": pid, "parsed": p, "usage": {}}
                               for r, d in by_run.items() for pid, p in d.items()]
    gpt.cost = lambda usage: 0.0
    orig_write = Path.write_text
    redirect = {RES / "llm_rater_labels.json": RES / "claude_rater_labels.json",
                RES / "llm_rater_analysis.json": RES / "claude_rater_analysis.json"}

    def write_text(self, data, *a, **k):
        return orig_write(redirect.get(self, self), data, *a, **k)

    Path.write_text = write_text
    try:
        gpt.analyze()
    finally:
        Path.write_text = orig_write
    out = json.loads((RES / "claude_rater_analysis.json").read_text())
    out["amendment"] = "research/preregistration_cs_breakthrough_forecast_v1_amendment4_claude_rater.md"
    out["batching"] = "3 batches of 40 per run, fresh subagent per batch"
    out["discarded_batches"] = [
        {k: json.loads(l)[k] for k in ("run", "batch", "tool_uses")}
        for l in RAW.read_text().splitlines() if not json.loads(l)["parsed_ok"]]

    # A5: Claude vs GPT (run 1 each)
    g = {r["paper_id"]: r["llm_label"] for r in json.loads(
        (RES / "llm_rater_labels.json").read_text())["rows"]}
    c = {pid: p["label"] for pid, p in by_run[1].items()}
    pairs = [(c[p], g[p]) for p in c if p in g and c[p] in (1, 2, 3) and g[p] in (1, 2, 3)]
    a5 = gpt.agreement([a for a, _ in pairs], [b for _, b in pairs],
                       np.random.default_rng(gpt.SEED))
    a5["mean_claude_minus_gpt"] = a5.pop("mean_llm_minus_human")
    lo = a5.get("kappa_ci95", [float("nan")])[0]
    out["A5_claude_vs_gpt"] = {"all": a5, "verdict": "models_agree_moderately_or_better"
                               if lo > 0.4 else "not_established"}
    orig_write(RES / "claude_rater_analysis.json", json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("rated_primary", "missing_primary",
                                          "discarded_batches")}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prompt":
        print(prompt(int(sys.argv[2]), int(sys.argv[3])))
    elif cmd == "ingest":
        ingest(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]))
    else:
        analyze()
