#!/usr/bin/env python3
"""Build a self-contained, blinded HTML labeling page for check A5 (label validity, H3).

Sample (Paper 4 check A5, fixed seed): up to 40 citation top-decile papers, 40 random
non-top-decile papers, and 40 non-top-decile papers the Paper 3 model ranked highest (where
H1 and H3 disagree). Strata are shuffled together and hidden from the labeler; the key is
written separately to results/cs_forecast_v1/labeling_key.json.

    python3 scripts/build_labeling_html.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/cs_forecast_v1"
SEED = 20261014
PER_STRATUM = 40


def main() -> None:
    snap = {json.loads(l)["paper_id"]: json.loads(l)
            for l in open(ROOT / "data/cs_forecast/snapshot_v1.jsonl")}
    pred = pd.read_csv(RES / "predictions_primary.csv", dtype={"paper_id": str})
    feats = pd.read_csv(RES / "features.csv", dtype={"paper_id": str})
    df = feats[["paper_id", "year", "y_breakthrough"]].merge(
        pred[["paper_id", "paper3_cs_logistic"]], on="paper_id", how="left")
    rng = np.random.default_rng(SEED)
    pos = df[df.y_breakthrough == 1]
    neg = df[df.y_breakthrough == 0]
    s_pos = pos.sample(min(PER_STRATUM, len(pos)), random_state=SEED)
    s_high = (neg[neg.paper3_cs_logistic.notna()]
              .sort_values("paper3_cs_logistic", ascending=False).head(PER_STRATUM))
    rest = neg.drop(s_high.index)
    s_rand = rest.sample(min(PER_STRATUM, len(rest)), random_state=SEED)
    key = ([(p, "citation_top_decile") for p in s_pos.paper_id]
           + [(p, "model_high_citation_negative") for p in s_high.paper_id]
           + [(p, "random_citation_negative") for p in s_rand.paper_id])
    order = rng.permutation(len(key))
    items = []
    for i in order:
        pid = key[i][0]
        s = snap[pid]
        items.append({"id": pid, "year": s["year"], "title": s["title"],
                      "abstract": s.get("abstract") or "(no abstract in OpenAlex)",
                      "url": f"https://arxiv.org/abs/{pid}"})
    (RES / "labeling_key.json").write_text(json.dumps(
        {"seed": SEED, "strata": {pid: st for pid, st in key}}, indent=1) + "\n")
    html = TEMPLATE.replace("__ITEMS__", json.dumps(items))
    out = ROOT / "labeling/cs_breakthrough_labeling.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f"{len(items)} items -> {out}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CS Breakthrough Labeling</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--fg:#1d1d1b;--muted:#6b6b66;--line:#e2e2dc;--accent:#2f5bd3;
--sel:#e8eefc;--ok:#1f7a4d}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161616;--card:#1f1f1f;
--fg:#ececea;--muted:#a0a09a;--line:#333;--accent:#7f9cf5;--sel:#26304a;--ok:#5cc391}}
:root[data-theme="dark"]{--bg:#161616;--card:#1f1f1f;--fg:#ececea;--muted:#a0a09a;--line:#333;
--accent:#7f9cf5;--sel:#26304a;--ok:#5cc391}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:860px;margin:0 auto;padding:20px 16px 80px}
h1{font-size:20px;margin:0 0 4px}.muted{color:var(--muted)}
.bar{height:6px;background:var(--line);border-radius:3px;margin:12px 0}
.bar>div{height:100%;background:var(--ok);border-radius:3px;width:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;margin-top:14px}
.title{font-size:18px;font-weight:600;margin:4px 0 8px}
.abs{white-space:pre-wrap;color:var(--fg);max-height:260px;overflow:auto;border-top:1px solid var(--line);padding-top:8px}
.opts{display:grid;gap:8px;margin-top:14px}
.opt{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--line);border-radius:8px;padding:10px;cursor:pointer;background:var(--card);color:var(--fg);text-align:left;font:inherit}
.opt.on{border-color:var(--accent);background:var(--sel)}
.k{font-weight:700;min-width:18px;color:var(--accent)}
textarea{width:100%;min-height:54px;margin-top:10px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px;font:inherit}
.nav{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
button.b{padding:8px 14px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer;font:inherit}
button.p{background:var(--accent);border-color:var(--accent);color:#fff}
details{margin-top:10px}a{color:var(--accent)}
</style></head><body><main>
<h1>CS breakthrough labeling</h1>
<div class="muted">Judge each paper's <b>contribution</b>, as seen about 3 years after its
publication year. You may read the paper or search the web, but please <b>do not look up
citation counts</b>: they are what this labeling is checking. Labels save in this browser
automatically. When you're done, click <b>Export labels</b> and send the downloaded JSON file
back.</div>
<details><summary>Rubric</summary><ul>
<li><b>3 – Breakthrough</b>: opened a new direction, or became a widely adopted method,
benchmark, system or result within ~3 years.</li>
<li><b>2 – Significant</b>: a solid contribution that others clearly built on, but not
field-changing.</li>
<li><b>1 – Incremental</b>: a modest or narrow contribution with little visible
uptake.</li>
<li><b>0 – Can't judge</b>: outside your expertise, or not enough information.</li></ul>
Keys: 0–3 choose a label · ← → move between papers.</details>
<div class="bar"><div id="prog"></div></div><div id="count" class="muted"></div>
<div class="card" id="card"></div>
<div class="nav"><button class="b" id="prev">← Prev</button><button class="b" id="next">Next →</button>
<button class="b" id="jump">Next unlabeled</button><span style="flex:1"></span>
<button class="b p" id="exp">Export labels</button><label class="b" style="cursor:pointer">Import
<input type="file" id="imp" accept=".json" hidden></label></div>
</main><script>
const ITEMS=__ITEMS__;const KEY="cs-breakthrough-labels-v1";
const OPTS=[[3,"Breakthrough","Opened a direction or widely adopted"],[2,"Significant","Clearly built on, not field-changing"],
[1,"Incremental","Modest or narrow, little uptake"],[0,"Can't judge","Outside expertise / insufficient info"]];
let L={};try{L=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
let i=0;const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(L))}catch(e){}};
function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function render(){const it=ITEMS[i],cur=L[it.id]||{};
document.getElementById("card").innerHTML=`<div class="muted">${i+1} / ${ITEMS.length} · published ${it.year}
· <a href="${esc(it.url)}" target="_blank" rel="noopener">arXiv ${esc(it.id)}</a></div>
<div class="title">${esc(it.title)}</div><div class="abs">${esc(it.abstract)}</div>
<div class="opts">${OPTS.map(([v,n,d])=>`<button class="opt ${cur.label===v?"on":""}" data-v="${v}">
<span class="k">${v}</span><span><b>${n}</b><br><span class="muted">${d}</span></span></button>`).join("")}</div>
<textarea id="note" placeholder="Optional note (e.g., what it led to)">${esc(cur.note||"")}</textarea>`;
document.querySelectorAll(".opt").forEach(b=>b.onclick=()=>setLabel(+b.dataset.v));
document.getElementById("note").oninput=e=>{L[it.id]={...(L[it.id]||{}),note:e.target.value};save()};
const n=ITEMS.filter(x=>L[x.id]&&L[x.id].label!==undefined).length;
document.getElementById("prog").style.width=(100*n/ITEMS.length)+"%";
document.getElementById("count").textContent=`${n} of ${ITEMS.length} labeled`;}
function setLabel(v){const it=ITEMS[i];L[it.id]={...(L[it.id]||{}),label:v,at:new Date().toISOString()};save();
if(i<ITEMS.length-1)i++;render()}
document.getElementById("prev").onclick=()=>{if(i>0)i--;render()};
document.getElementById("next").onclick=()=>{if(i<ITEMS.length-1)i++;render()};
document.getElementById("jump").onclick=()=>{const j=ITEMS.findIndex(x=>!L[x.id]||L[x.id].label===undefined);if(j>=0)i=j;render()};
document.addEventListener("keydown",e=>{if(e.target.tagName==="TEXTAREA")return;
if("0123".includes(e.key))setLabel(+e.key);if(e.key==="ArrowRight"&&i<ITEMS.length-1){i++;render()}
if(e.key==="ArrowLeft"&&i>0){i--;render()}});
document.getElementById("exp").onclick=()=>{const blob=new Blob([JSON.stringify({schema:"cs-breakthrough-labels-v1",
exported:new Date().toISOString(),labels:L},null,1)],{type:"application/json"});const a=document.createElement("a");
a.href=URL.createObjectURL(blob);a.download="cs_breakthrough_labels.json";a.click()};
document.getElementById("imp").onchange=async e=>{const f=e.target.files[0];if(!f)return;
try{const d=JSON.parse(await f.text());L={...L,...(d.labels||d)};save();render()}catch(err){alert("Could not read file")}};
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
