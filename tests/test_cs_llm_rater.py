"""Amendment 3 LLM-rater tests (no API calls; synthetic values are never reported as results)."""

import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rate = _load("llm_rate_cs_papers")
ana = _load("analyze_cs_llm_rater")
AMEND = ROOT / "research/preregistration_cs_breakthrough_forecast_v1_amendment3_llm_rater.md"


def test_prompt_matches_preregistration_verbatim():
    blocks = re.findall(r"```text\n(.*?)\n```", AMEND.read_text(), re.S)
    assert blocks[0] == rate.SYSTEM_PROMPT
    assert blocks[1] == rate.USER_TEMPLATE


def test_items_carry_only_title_year_abstract():
    items = rate.load_items()
    assert len(items) == 120 and len({i["id"] for i in items}) == 120
    msg = rate.user_message(items[0])
    assert items[0]["id"] not in msg and "arxiv.org" not in msg
    key = json.loads((ROOT / "results/cs_forecast_v1/labeling_key.json").read_text())["strata"]
    assert {i["id"] for i in items} == set(key)
    assert "citation" not in rate.user_message({"title": "t", "year": 2015, "abstract": "a"})


def test_parse_reply():
    ok = rate.parse_reply('Sure. {"recognized": false, "recall": "", "label": 2, "rationale": "x"}')
    assert ok == {"label": 2, "recognized": False, "recall": "", "rationale": "x"}
    assert rate.parse_reply('{"recognized": "no", "label": 2}') is None
    assert rate.parse_reply('{"recognized": true, "label": 4}') is None
    assert rate.parse_reply('{"recognized": true, "label": true}') is None
    assert rate.parse_reply("no json") is None


def test_worst_case_bounds_cap():
    items = rate.load_items()
    per_call = max(rate.worst_case_cost(m, it) for _, m, _ in rate.PLAN for it in items)
    assert per_call < 0.06  # a single call can never overshoot the cap by more than this


def test_cost_cap_stops_before_any_call(tmp_path, monkeypatch):
    raw = tmp_path / "raw.jsonl"
    raw.write_text(json.dumps({"rater": "R1", "model": "claude-opus-5-5", "pass": 1,
                               "id": "x", "status": "ok", "cost_usd": 4.99}) + "\n")
    monkeypatch.setattr(rate, "RAW", raw)
    monkeypatch.setattr(sys, "argv", ["llm_rate_cs_papers.py"])

    def boom(*a, **k):
        raise AssertionError("API must not be called over the cap")

    monkeypatch.setattr(rate, "call_anthropic", boom)
    monkeypatch.setattr(rate, "call_openai", boom)
    assert rate.main() == 3
    assert len(raw.read_text().splitlines()) == 1


def test_weighted_kappa():
    a = [1, 2, 3, 1, 2, 3]
    assert ana.weighted_kappa(a, a) == 1.0
    assert ana.weighted_kappa([1, 1, 3, 3], [3, 3, 1, 1]) < 0
    rng = np.random.default_rng(0)
    x = rng.integers(1, 4, 2000)
    y = rng.integers(1, 4, 2000)
    assert abs(ana.weighted_kappa(x, y)) < 0.08


def test_analysis_runs_end_to_end_on_synthetic_log(tmp_path, monkeypatch):
    res = tmp_path / "res"
    res.mkdir()
    key = (ROOT / "results/cs_forecast_v1/labeling_key.json").read_text()
    (res / "labeling_key.json").write_text(key)
    rng = np.random.default_rng(1)
    lines = []
    for rater, model, pas in rate.PLAN:
        for pid in json.loads(key)["strata"]:
            lines.append(json.dumps({"rater": rater, "model": model, "pass": pas, "id": pid,
                                     "status": "ok", "cost_usd": 0.001,
                                     "parsed": {"label": int(rng.integers(0, 4)),
                                                "recognized": bool(rng.random() < 0.3)}}))
    raw = tmp_path / "raw.jsonl"
    raw.write_text("\n".join(lines) + "\n")
    monkeypatch.setattr(ana, "RES", res)
    monkeypatch.setattr(ana, "RAW", raw)
    monkeypatch.setattr(ana, "REPS", 50)
    ana.main()
    out = json.loads((res / "llm_rater.json").read_text())
    assert out["R1_primary"]["n_rated"] == 120
    assert "weighted_kappa" in out["R1_primary"]["A1_human_agreement"]["all"]
    assert out["A4_reliability"]["R1_vs_R2"]["n_common"] == 120
