#!/usr/bin/env python3
"""Evidence-based value markers (amendment 5): prompts, ingest, audit, verify, analyze.

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment5_value_markers.md.
Searching is done by fresh subagents; this script never calls a model.

    python3 scripts/run_cs_value_markers.py prompt <batch>
    python3 scripts/run_cs_value_markers.py ingest <batch> <transcript.jsonl> <prompt_file>
    python3 scripts/run_cs_value_markers.py verify
    python3 scripts/run_cs_value_markers.py analyze
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cs_forecast.evidence_verify import fetch, normalize  # noqa: E402

RES = ROOT / "results/cs_forecast_v1"
RAW = RES / "value_markers_raw.jsonl"
VER = RES / "value_markers_verified.json"
BATCH = 20
SEED, REPS = 20261017, 10000
NAMES = {"T": "citation_top_decile", "R": "random_citation_negative",
         "M": "model_high_citation_negative"}
EXCLUDED_HOSTS = ("scholar.google", "semanticscholar.org", "openalex.org", "researchgate.net",
                  "paperswithcode.com", "arxiv.org/abs", "dblp.org", "dblp.uni-trier.de")
FORBIDDEN = ("/home/user", "labeling_key", "cs_forecast", "results/")

_spec = importlib.util.spec_from_file_location("gpt", ROOT / "scripts/run_cs_llm_rater.py")
gpt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gpt)

INSTRUCTIONS = """You are gathering verifiable documentary evidence of the lasting value of research papers.
For each paper below, search the web for these markers (evidence of any date up to today):

M1 award: a best, outstanding or distinguished paper award, or a test-of-time award, shown on an official venue, society or organiser page.
M2 reference work: the paper's method or result is explained in the body of a textbook, a university course page or lecture notes, or a Wikipedia article. A bare bibliography entry is not enough.
M3 adoption: the method, system, dataset or benchmark is implemented in or shipped with a widely used third-party library, framework or tool whose documentation names it, or is a standard benchmark of a public leaderboard. The authors' own repositories and pages do not count.
M4 survey recognition: a later survey or review by different authors presents it as a key or representative method of a named category.

Rules:
- Do not use citation counts or citation-index pages (Google Scholar, Semantic Scholar, OpenAlex, ResearchGate, Papers with Code), the paper itself, arXiv or DBLP listings, or pages by the paper's authors.
- Do not read, list or modify any local file, and do not run commands on local files. Use web search and web fetching only (fetching pages with curl is fine).
- Every claimed marker needs a URL and a verbatim quote of at most 40 words copied exactly from that page. Each cited page must itself name the paper by title or arXiv id somewhere on it (for example in its references).
- Be conservative. If you find no qualifying evidence for a paper, return an empty marker list. Absence is a valid answer.

Reply with only a JSON array (no prose, no code fence), one object per paper, in order:
{"item": <item number>, "markers": [{"type": "M1|M2|M3|M4", "url": "<url>", "quote": "<verbatim quote>"}], "notes": "<at most 40 words>"}

Papers:
"""


def items() -> list[dict]:
    return gpt.load_items()


def batch_items(b: int) -> list[tuple[int, dict]]:
    its = items()
    return [(i + 1, its[i]) for i in range((b - 1) * BATCH, b * BATCH)]


def prompt(b: int) -> str:
    lines = [INSTRUCTIONS]
    for n, it in batch_items(b):
        lines.append(f'Item {n}: arXiv {it["id"]}, {it["year"]}, "{it["title"]}"')
    return "\n".join(lines) + "\n"


def transcript_calls(path: str) -> list[tuple[str, dict]]:
    calls = []
    for line in open(path):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        c = (d.get("message") or {}).get("content")
        if isinstance(c, list):
            calls += [(x.get("name"), x.get("input", {})) for x in c
                      if isinstance(x, dict) and x.get("type") == "tool_use"]
    return calls


def ingest(b: int, transcript: str, prompt_file: str) -> None:
    calls = transcript_calls(transcript)
    reply = next((v for n, inp in calls if n == "SubagentHandback"
                  for v in inp.values() if isinstance(v, str) and "[" in v), "")
    violations = []
    for n, inp in calls:
        if n == "SubagentHandback":
            continue
        s = json.dumps(inp)
        if any(f in s for f in FORBIDDEN):
            violations.append({"tool": n, "input": s[:300]})
        if n == "Read" and inp.get("file_path") != prompt_file:
            violations.append({"tool": n, "input": s[:300]})
    names = {}
    for n, _ in calls:
        names[n] = names.get(n, 0) + 1
    try:
        arr = json.loads(reply[reply.find("["): reply.rfind("]") + 1])
        ok = [o.get("item") for o in arr] == [n for n, _ in batch_items(b)]
    except json.JSONDecodeError:
        arr, ok = None, False
    rec = {"batch": b, "at": datetime.now(timezone.utc).isoformat(), "tool_calls": names,
           "isolation_violations": violations, "parsed_ok": ok,
           "accepted": ok and not violations, "reply": reply}
    with open(RAW, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in ("batch", "tool_calls", "parsed_ok", "accepted")}
                     | {"violations": len(violations)}))


def accepted_claims() -> dict[str, list[dict]]:
    its = items()
    out = {}
    for line in RAW.read_text().splitlines():
        rec = json.loads(line)
        if not rec["accepted"]:
            continue
        arr = json.loads(rec["reply"][rec["reply"].find("["): rec["reply"].rfind("]") + 1])
        for o in arr:
            out[its[o["item"] - 1]["id"]] = o.get("markers") or []
    return out


def names_paper(text: str, pid: str, title: str) -> bool:
    t, words = normalize(text), normalize(title).split()
    if normalize(pid) in t:
        return True
    k = min(5, len(words))
    return any(" ".join(words[i:i + k]) in t for i in range(len(words) - k + 1))


def verify() -> None:
    claims, its = accepted_claims(), {it["id"]: it for it in items()}
    cache: dict[str, tuple[int, str]] = {}
    out = {}
    for pid, ms in claims.items():
        res = []
        for m in ms:
            url, quote = m.get("url", ""), m.get("quote", "")
            host = urlparse(url).netloc.lower() + urlparse(url).path.lower()
            if any(h in host for h in EXCLUDED_HOSTS):
                st = "excluded_source"
            else:
                if url not in cache:
                    try:
                        cache[url] = fetch(url)
                    except Exception:
                        cache[url] = (0, "")
                    time.sleep(1)
                code, text = cache[url]
                if code >= 400 or code == 0 or not text.strip():
                    st = "fetch_failed"
                elif normalize(quote) not in normalize(text):
                    st = "quote_not_found"
                elif not names_paper(text, pid, its[pid]["title"]):
                    st = "paper_not_named"
                else:
                    st = "verified"
            res.append({**m, "status": st})
        out[pid] = res
    VER.write_text(json.dumps({"verified_at": datetime.now(timezone.utc).isoformat(),
                               "papers": out}, indent=1) + "\n")
    from collections import Counter
    print(Counter(r["status"] for v in out.values() for r in v))


def rd(a: list[int], b: list[int], rng) -> dict:
    a, b = np.asarray(a), np.asarray(b)
    boot = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(REPS)]
    return {"n_a": int(len(a)), "n_b": int(len(b)), "rate_a": float(a.mean()),
            "rate_b": float(b.mean()), "risk_difference": float(a.mean() - b.mean()),
            "rd_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "fisher_p": float(fisher_exact([[a.sum(), len(a) - a.sum()],
                                            [b.sum(), len(b) - b.sum()]]).pvalue)}


def analyze() -> None:
    ver = json.loads(VER.read_text())["papers"]
    strata = json.loads((RES / "labeling_key.json").read_text())["strata"]
    inv = {v: k for k, v in NAMES.items()}
    human = {k: v["label"] for k, v in json.loads(
        (ROOT / "data/cs_forecast/human_labels_v1.json").read_text())["labels"].items()}
    gl = {r["paper_id"]: r["llm_label"] for r in json.loads(
        (RES / "llm_rater_labels.json").read_text())["rows"]}
    cl = {r["paper_id"]: r["llm_label"] for r in json.loads(
        (RES / "claude_rater_labels.json").read_text())["rows"]}
    rows = []
    for it in items():
        pid = it["id"]
        if pid not in ver:
            continue
        ok = {m["type"] for m in ver[pid] if m["status"] == "verified"}
        rows.append({"paper_id": pid, "stratum": inv[strata[pid]], "types": sorted(ok),
                     "V": int(bool(ok & {"M1", "M2", "M3"})), "V4": int(bool(ok)),
                     "K": len(ok & {"M1", "M2", "M3"})})
    rng = np.random.default_rng(SEED)
    g = lambda s, k: [r[k] for r in rows if r["stratum"] == s]  # noqa: E731
    b1, b2 = rd(g("T", "V"), g("R", "V"), rng), rd(g("M", "V"), g("R", "V"), rng)
    v1 = ("citation_label_agrees_with_documentary_value" if b1["rd_ci95"][0] > 0 else
          "citation_label_does_not_agree" if b1["rd_ci95"][1] < 0.10 else "inconclusive")
    v2 = ("structure_model_finds_value_citations_miss" if b2["rd_ci95"][0] > 0
          else "no_evidence")
    b3 = {}
    for name, lab in (("human", human), ("gpt", gl), ("claude", cl)):
        v1s = [lab[r["paper_id"]] for r in rows if r["V"] and lab.get(r["paper_id"]) in (1, 2, 3)]
        v0s = [lab[r["paper_id"]] for r in rows if not r["V"] and lab.get(r["paper_id"]) in (1, 2, 3)]
        b3[name] = gpt.compare(v1s, v0s, rng) if v1s and v0s else {"n_a": len(v1s), "n_b": len(v0s)}
    from collections import Counter
    status = Counter(m["status"] for v in ver.values() for m in v)
    types = {s: dict(Counter(t for r in rows if r["stratum"] == s for t in r["types"]))
             for s in NAMES}
    out = {"amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment5_value_markers.md",
           "n_papers": len(rows), "verification_status": dict(status),
           "verified_types_by_stratum": types,
           "B1_T_vs_R_V": b1, "B1_verdict": v1, "B2_M_vs_R_V": b2, "B2_verdict": v2,
           "B3_rater_scores_by_V": b3,
           "B4": {"T_vs_R_V4": rd(g("T", "V4"), g("R", "V4"), rng),
                  "M_vs_R_V4": rd(g("M", "V4"), g("R", "V4"), rng),
                  "T_vs_R_K": gpt.compare(g("T", "K"), g("R", "K"), rng),
                  "M_vs_R_K": gpt.compare(g("M", "K"), g("R", "K"), rng)},
           "rows": rows, "seed": SEED, "reps": REPS}
    (RES / "value_markers_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("n_papers", "verification_status", "B1_verdict",
                                          "B2_verdict")}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prompt":
        print(prompt(int(sys.argv[2])), end="")
    elif cmd == "ingest":
        ingest(int(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif cmd == "verify":
        verify()
    else:
        analyze()
