#!/usr/bin/env python3
"""LLM reference-rater calls for the 120 G3 papers (amendment 3).

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment3_llm_rater.md.
Each request sees one paper's title, year and abstract only. Never reads the stratum key or
the human labels. Every call is appended to data/cs_forecast/llm_ratings_raw.jsonl; the run
resumes and stops before any call that could push total spend over the US$5 cap.

    python3 scripts/llm_rate_cs_papers.py --dry-run
    python3 scripts/llm_rate_cs_papers.py
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "labeling/cs_breakthrough_labeling.html"
RAW = ROOT / "data/cs_forecast/llm_ratings_raw.jsonl"
CAP_USD = 5.00
SEED = 20261017

SYSTEM_PROMPT = """You are an expert computer-science reviewer acting as one rater in a research study. You will see one arXiv paper's title, publication year and abstract. Judge the paper's contribution as it would be seen about 3 years after its publication year, using the rubric below. You are not given citation counts; do not try to estimate them.

Rubric:
3 - Breakthrough: opened a new direction, or became a widely adopted method, benchmark, system or result within ~3 years.
2 - Significant: a solid contribution that others clearly built on, but not field-changing.
1 - Incremental: a modest or narrow contribution with little visible uptake.
0 - Can't judge: outside your expertise, or not enough information.

Also report whether you recognize this specific paper, meaning you know something about it beyond the text shown (for example its authors, venue, or later reception). Answer honestly; "false" is an acceptable and expected answer for most papers.

Reply with only a JSON object and no other text, in this form:
{"recognized": true or false, "recall": "if recognized, one sentence on what you know about this paper beyond the text shown; otherwise an empty string", "label": 0, 1, 2 or 3, "rationale": "one or two sentences"}"""

USER_TEMPLATE = "Title: {title}\nPublication year: {year}\nAbstract: {abstract}"

# US$ per token (input, output). gpt-4.1 is a deliberate upper bound (amendment 3).
PRICES = {"claude-opus-5-5": (4.00e-6, 20.00e-6), "gpt-4.1": (5.00e-6, 20.00e-6)}
# (rater, model, pass) in frozen run order.
PLAN = [("R1", "claude-opus-5-5", 1), ("R2", "gpt-4.1", 1), ("R1", "claude-opus-5-5", 2)]
MAX_TOKENS = {"claude-opus-5-5": 2000, "gpt-4.1": 400}


class ModelUnavailable(Exception):
    pass


def load_items() -> list[dict]:
    text = HTML.read_text()
    m = re.search(r"const ITEMS=(\[.*?\]);const KEY=", text, re.S)
    items = json.loads(m.group(1))
    # Only these fields reach the prompt; id is kept locally for bookkeeping.
    return [{"id": it["id"], "title": it["title"], "year": it["year"],
             "abstract": it["abstract"]} for it in items]


def user_message(item: dict) -> str:
    return USER_TEMPLATE.format(title=item["title"], year=item["year"], abstract=item["abstract"])


def parse_reply(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or d.get("label") not in (0, 1, 2, 3) \
            or isinstance(d.get("label"), bool) or not isinstance(d.get("recognized"), bool):
        return None
    return {"label": d["label"], "recognized": d["recognized"],
            "recall": str(d.get("recall", "")), "rationale": str(d.get("rationale", ""))}


def worst_case_cost(model: str, item: dict) -> float:
    pin, pout = PRICES[model]
    chars = len(SYSTEM_PROMPT) + len(user_message(item))
    return math.ceil(chars / 2) * pin + MAX_TOKENS[model] * pout


def call_anthropic(client, model: str, item: dict) -> tuple[str, int, int, str]:
    import anthropic
    try:
        r = client.messages.create(
            model=model, max_tokens=MAX_TOKENS[model], system=SYSTEM_PROMPT,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": user_message(item)}])
    except anthropic.NotFoundError as e:
        raise ModelUnavailable(str(e)) from e
    text = "".join(b.text for b in r.content if b.type == "text")
    return text, r.usage.input_tokens, r.usage.output_tokens, r.stop_reason


def call_openai(client, model: str, item: dict) -> tuple[str, int, int, str]:
    import openai
    try:
        r = client.chat.completions.create(
            model=model, max_tokens=MAX_TOKENS[model], temperature=0, seed=SEED,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": user_message(item)}])
    except openai.NotFoundError as e:
        raise ModelUnavailable(str(e)) from e
    c = r.choices[0]
    return (c.message.content or ""), r.usage.prompt_tokens, r.usage.completion_tokens, \
        c.finish_reason


def load_log() -> list[dict]:
    if not RAW.exists():
        return []
    return [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print cost bounds, make no calls")
    args = ap.parse_args()
    items = load_items()
    assert len(items) == 120, len(items)

    if args.dry_run:
        total = sum(worst_case_cost(m, it) for _, m, _ in PLAN for it in items)
        print(f"{len(items)} items, {len(PLAN)} passes; worst case if every call used max_tokens: "
              f"${total:.2f} (cap ${CAP_USD:.2f}; the cap stops the run before exceeding it)")
        for r, m, p in PLAN:
            print(f"  {r} {m} pass {p}: worst case ${sum(worst_case_cost(m, it) for it in items):.2f}")
        return 0

    log = load_log()
    spent = sum(e["cost_usd"] for e in log)
    done = {(e["rater"], e["pass"], e["id"]) for e in log if e["status"] in ("ok", "missing")}
    attempts = {}
    for e in log:
        k = (e["rater"], e["pass"], e["id"])
        attempts[k] = attempts.get(k, 0) + 1
    clients = {}
    skipped = set()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    with RAW.open("a") as out:
        for rater, model, pas in PLAN:
            if model in skipped:
                continue
            for item in items:
                key = (rater, pas, item["id"])
                if key in done:
                    continue
                while key not in done:
                    wc = worst_case_cost(model, item)
                    if spent + wc > CAP_USD:
                        print(f"stopped_by_cost_cap: spent ${spent:.4f}, next call worst case "
                              f"${wc:.4f}", file=sys.stderr)
                        return 3
                    if model not in clients:
                        if model.startswith("claude"):
                            import anthropic
                            # Pin the public endpoint; ignore any ANTHROPIC_BASE_URL override.
                            clients[model] = anthropic.Anthropic(
                                base_url="https://api.anthropic.com", max_retries=2)
                        else:
                            import openai
                            clients[model] = openai.OpenAI(max_retries=2)
                    fn = call_anthropic if model.startswith("claude") else call_openai
                    entry = {"rater": rater, "model": model, "pass": pas, "id": item["id"],
                             "attempt": attempts.get(key, 0) + 1,
                             "at": datetime.now(timezone.utc).isoformat()}
                    try:
                        text, tin, tout, stop = fn(clients[model], model, item)
                    except ModelUnavailable as e:
                        print(f"{model} unavailable, rater skipped (not substituted): {e}",
                              file=sys.stderr)
                        skipped.add(model)
                        entry.update(status="model_unavailable", error=str(e)[:500],
                                     cost_usd=0.0)
                        out.write(json.dumps(entry) + "\n")
                        out.flush()
                        break
                    except Exception as e:  # auth, network: no usage returned
                        entry.update(status="error", error=f"{type(e).__name__}: {e}"[:500],
                                     cost_usd=0.0)
                        out.write(json.dumps(entry) + "\n")
                        out.flush()
                        print(f"aborting on API error: {entry['error']}", file=sys.stderr)
                        return 2
                    pin, pout = PRICES[model]
                    cost = tin * pin + tout * pout
                    spent += cost
                    attempts[key] = entry["attempt"]
                    parsed = parse_reply(text) if stop != "refusal" else None
                    status = "ok" if parsed else ("missing" if entry["attempt"] >= 2 else "retry")
                    entry.update(status=status, input_tokens=tin, output_tokens=tout,
                                 stop_reason=stop, cost_usd=cost, reply=text, parsed=parsed,
                                 spent_total_usd=spent)
                    out.write(json.dumps(entry) + "\n")
                    out.flush()
                    if status != "retry":
                        done.add(key)
            print(f"{rater} {model} pass {pas} done; spent ${spent:.4f}")
    print(f"all passes finished; total spent ${spent:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
