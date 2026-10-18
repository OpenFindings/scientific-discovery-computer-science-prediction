import importlib.util, json, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from pathlib import Path
ROOT=str(Path(__file__).resolve().parents[2])
s=importlib.util.spec_from_file_location("f",ROOT+"/scripts/run_cs_direction_features_v2.py"); f=importlib.util.module_from_spec(s); s.loader.exec_module(f)
d=f.d; df=f.panel(); sel=list(json.load(open(ROOT+"/results/cs_direction_features_v2/discovery.json"))["selected"])
cols=d.MOMENTUM+sel
# per-origin rank normalisation (removes level drift across years)
R=df.copy()
for c in cols: R[c]=R.groupby("origin")[c].rank(pct=True)
def run(D, cs, label):
    out=[]
    for t in f.CONF:
        tr=D[(D.origin<=t-5)&D.G.notna()]; te=D[(D.origin==t)&D.G.notna()]
        p=d.model("ridge").fit(tr[cs],tr.G).predict(te[cs]); out.append(spearmanr(p,te.G).statistic)
    print(label, round(float(np.mean(out)),3), [round(x,3) for x in out])
run(df,d.MOMENTUM,"raw M0"); run(df,cols,"raw M1")
run(R,d.MOMENTUM,"rank M0"); run(R,cols,"rank M1")
# training-weight drift: coefficient of share_dl when trained on early vs late origins
for lo,hi in [(2006,2010),(2011,2014)]:
    tr=df[(df.origin>=lo)&(df.origin<=hi)&df.G.notna()]
    m=d.model("ridge").fit(tr[cols],tr.G); print(lo,hi,dict(zip(cols,np.round(m.named_steps["m"].coef_,3))))
