#!/usr/bin/env python3
"""Upload recovered, checksum-verified public PDFs to the private ai4cs R2 bucket."""
import argparse, datetime as dt, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES=("data/fulltext_recovery_manifest_batches8_15_30_34.jsonl","data/fulltext_recovery_manifest_batch34_sources.jsonl")

def atomic_jsonl(path:Path,rows:list[dict])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=path.parent,prefix=f".{path.name}.",delete=False) as f:
        tmp=Path(f.name)
        for row in rows: f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
        f.flush()
    tmp.replace(path)

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bucket",default="ai4cs")
    ap.add_argument("--wrangler",type=Path,default=None)
    ap.add_argument("--root",type=Path,default=ROOT)
    args=ap.parse_args(); root=args.root.resolve()
    cli=str(args.wrangler or shutil.which("wrangler") or "/Users/amao/.npm/_npx/32026684e21afda6/node_modules/.bin/wrangler")
    if not Path(cli).is_file(): raise SystemExit("Wrangler CLI not found; pass --wrangler explicitly")
    sources=[]
    for name in SOURCES:
        p=root/name
        if p.exists(): sources.extend(json.loads(x) for x in p.read_text().splitlines() if x.strip())
    downloads=[x for x in sources if x.get("status")=="downloaded"]
    old_path=root/"data/r2_recovered_batches_2026-10-13.jsonl"
    receipts={}
    if old_path.exists():
        for line in old_path.read_text().splitlines():
            if line.strip():
                row=json.loads(line); receipts[row["key"]]=row
    outcomes=[]
    with tempfile.TemporaryDirectory(prefix="r2-recover-",dir="/private/tmp") as tmpdir:
        tmp=Path(tmpdir)
        for row in downloads:
            local=(root/row["path"]).resolve()
            if root not in local.parents: raise SystemExit(f"unsafe local path {row['path']}")
            data_hash=hashlib.sha256(local.read_bytes()).hexdigest()
            if not local.is_file() or local.stat().st_size!=row["bytes"] or data_hash!=row["sha256"] or not local.read_bytes().startswith(b"%PDF-"):
                outcomes.append({"path":row["path"],"status":"local_integrity_failure"}); continue
            paper=row.get("arxiv_id") or f"source-line-{row['ledger_line']}"
            key=f"scientific-discovery/fulltexts/recovered-batches-2026-10-13/batch{row['batch']}/{paper}.pdf"
            if key in receipts:
                prior=receipts[key]
                if prior.get("sha256")==data_hash and prior.get("bytes")==row["bytes"]:
                    outcomes.append({"key":key,"status":"already_verified_from_receipt"}); continue
                outcomes.append({"key":key,"status":"receipt_conflict_refused"}); continue
            remote=tmp/"existing.pdf"
            probe=subprocess.run([cli,"r2","object","get",f"{args.bucket}/{key}","--remote","--file",str(remote)],capture_output=True,text=True,check=False)
            if probe.returncode==0:
                same=remote.is_file() and remote.stat().st_size==row["bytes"] and hashlib.sha256(remote.read_bytes()).hexdigest()==data_hash
                if not same:
                    outcomes.append({"key":key,"status":"existing_remote_object_differs_refused"}); continue
                method="preexisting_exact_match"
            elif "key does not exist" in (probe.stdout+probe.stderr).lower():
                put=subprocess.run([cli,"r2","object","put",f"{args.bucket}/{key}","--remote","--file",str(local),"--content-type","application/pdf"],capture_output=True,text=True,check=False)
                if put.returncode:
                    outcomes.append({"key":key,"status":"upload_failed","error":(put.stderr or put.stdout)[-500:]}); continue
                method="wrangler_r2_object_put_remote"
            else:
                outcomes.append({"key":key,"status":"remote_preflight_failed","error":(probe.stderr or probe.stdout)[-500:]}); continue
            receipt={"batch":row["batch"],"versioned_id":row.get("arxiv_id") or paper,"arxiv_id":row.get("arxiv_id"),
                    "title":row.get("title"),"source_url":row.get("source_url"),"key":key,"bytes":row["bytes"],
                    "sha256":data_hash,"status":"uploaded_and_source_checksum_verified","method":method,
                    "checked_at_utc":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")}
            receipts[key]=receipt; outcomes.append({"key":key,"status":receipt["status"]})
            atomic_jsonl(old_path,sorted(receipts.values(),key=lambda x:x["key"]))
            print(f"batch{row['batch']} {paper}: {receipt['status']}",flush=True)
    result={"bucket":args.bucket,"source_papers":len(downloads),"new_or_exact_verified_objects":sum(x["status"] in {"uploaded_and_source_checksum_verified","already_verified_from_receipt"} for x in outcomes),
            "failures":[x for x in outcomes if x["status"] not in {"uploaded_and_source_checksum_verified","already_verified_from_receipt"}],
            "receipts_manifest":str(old_path.relative_to(root)),"outcomes":outcomes}
    report=root/"reports/r2_batch_recovery_upload.json"; report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if result["failures"] else 0

if __name__=="__main__": raise SystemExit(main())
