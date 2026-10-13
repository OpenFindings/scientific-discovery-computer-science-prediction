#!/usr/bin/env python3
"""Analyze a preregistered feedback-on/off replication by container CPU throughput."""
import argparse, json, math, re, statistics
from decimal import Decimal
from pathlib import Path

COMMIT="1405d4eb5b7af7a639717a47147bd89362558830"
RATE_RE=re.compile(r"^Success rate for query pairs: ([0-9.]+)$",re.MULTILINE)

def exact_sign_test(values):
    pos=sum(x>0 for x in values); neg=sum(x<0 for x in values); n=pos+neg
    if not n: return {"n_nonzero":0,"two_sided_exact_p":None,"one_sided_positive_exact_p":None}
    tail=sum(math.comb(n,k) for k in range(min(pos,neg)+1))/(2**n)
    return {"n_nonzero":n,"two_sided_exact_p":min(1.0,2*tail),
            "one_sided_positive_exact_p":sum(math.comb(n,k) for k in range(neg+1))/(2**n)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,default=Path("results/sqlancerpp_feedback_cpu_4121_4125"))
    ap.add_argument("--output",type=Path)
    args=ap.parse_args(); rows=[]; errors=[]
    for seed in range(4121,4126):
        run=args.input/str(seed); meta=json.loads((run/"metadata.json").read_text())
        if meta.get("source_commit")!=COMMIT: errors.append(f"{seed}: commit mismatch")
        if meta.get("database_cap")!=20 or meta.get("query_cap_per_database")!=200: errors.append(f"{seed}: cap mismatch")
        arms={x["condition"]:x for x in meta["conditions"]}; row={"seed":seed,"complete_pair":True}
        for name in ("feedback_off","feedback_on"):
            arm=arms[name]; log=(run/name/"stdout.log").read_text(); rates=[Decimal(x) for x in RATE_RE.findall(log)]
            cpu=arm.get("container_cpu_usage_seconds")
            count=sum(int(r*200) for r in rates) if len(rates)==20 and all(r*200==int(r*200) for r in rates) else None
            valid=(arm.get("exit_code")==0 and arm.get("databases")==20 and arm.get("database_versions_logged")==["3.40.0"]
                   and len(rates)==20 and count is not None and isinstance(cpu,(int,float)) and cpu>0
                   and (arm.get("container_cpu_stats") or {}).get("usage_usec") is not None)
            if not valid: errors.append(f"{seed} {name}: incomplete raw rates or cgroup CPU counter"); row["complete_pair"]=False
            row[name]={"derived_successful_query_pairs":count,"cpu_seconds":cpu,
                       "successful_pairs_per_cpu_second":count/cpu if valid else None,
                       "raw_rates":[str(r) for r in rates],"cpu_stats":arm.get("container_cpu_stats"),
                       "elapsed_wall_seconds":arm.get("elapsed_seconds"),"exit_code":arm.get("exit_code")}
        if row["complete_pair"]:
            row["throughput_difference_on_minus_off"]=row["feedback_on"]["successful_pairs_per_cpu_second"]-row["feedback_off"]["successful_pairs_per_cpu_second"]
        else: row["throughput_difference_on_minus_off"]=None
        rows.append(row)
    diffs=[x["throughput_difference_on_minus_off"] for x in rows if x["complete_pair"]]
    pos=sum(x>0 for x in diffs); neg=sum(x<0 for x in diffs)
    arm_summary={}
    for name in ("feedback_off","feedback_on"):
        complete_arms=[row[name] for row in rows if row["complete_pair"]]
        rates=[arm["successful_pairs_per_cpu_second"] for arm in complete_arms]
        cpus=[arm["cpu_seconds"] for arm in complete_arms]
        arm_summary[name]={"successful_pairs_per_cpu_second":rates,
                           "mean_successful_pairs_per_cpu_second":statistics.mean(rates) if rates else None,
                           "median_successful_pairs_per_cpu_second":statistics.median(rates) if rates else None,
                           "cpu_seconds":cpus}
    result={"experiment_id":"EXP-DBMS-FEEDBACK-CPU-THROUGHPUT-4121-4125","evidence_level":4,
            "interpretation":"CPU-normalized successful-query throughput only, not bug yield, Paper 3 forecast, Paper 4 utility or agent effectiveness.",
            "design_limitations":["Within each seed, feedback_off always ran before feedback_on; order/time effects are not excluded.",
                                  "Fixed database/query caps with post hoc CPU normalization; this is not a stopped-at-equal-CPU-budget experiment.",
                                  "The primary numerator counts successful query pairs, not independently confirmed distinct bugs."],
            "execution_order":"feedback_off_then_feedback_on_for_every_seed",
            "arm_summary":arm_summary,
            "pinned_commit":COMMIT,"seeds":[x["seed"] for x in rows],"complete_pairs":len(diffs),
            "differences_on_minus_off_successful_pairs_per_cpu_second":diffs,
            "summary":{"positive":pos,"zero":sum(x==0 for x in diffs),"negative":neg,
                       "mean":statistics.mean(diffs) if diffs else None,
                       "median":statistics.median(diffs) if diffs else None,
                       "exact_sign_test":exact_sign_test(diffs)},
            "confirmed_distinct_bugs":None,"errors":errors,"seed_results":rows,
            "decision":"A positive result can support only higher query-pair throughput in this pinned setup. Independently confirmed bug yield is still unknown."}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="seed_results"},indent=2,sort_keys=True))
    return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
