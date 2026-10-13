#!/usr/bin/env python3
"""Read R2 objects remotely and verify receipt length/SHA-256 (never local emulation)."""
import argparse, datetime as dt, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFESTS=["data/fulltext_r2_upload_manifest.jsonl","data/r2_recovered_batches_2026-10-13.jsonl"]

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bucket",default="ai4cs")
    ap.add_argument("--manifest",action="append",default=[])
    ap.add_argument("--wrangler",type=Path,default=None)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args(); cli=str(args.wrangler or shutil.which("wrangler") or "/Users/amao/.npm/_npx/32026684e21afda6/node_modules/.bin/wrangler")
    if not Path(cli).is_file(): raise SystemExit("Wrangler CLI not found")
    manifests=args.manifest or DEFAULT_MANIFESTS; records=[]; seen=set()
    for name in manifests:
        p=ROOT/name
        if not p.is_file(): continue
        for line in p.read_text().splitlines():
            if not line.strip(): continue
            row=json.loads(line)
            if row.get("key") in seen: continue
            seen.add(row.get("key")); records.append(row)
    results=[]
    with tempfile.TemporaryDirectory(prefix="r2-verify-",dir="/private/tmp") as td:
        dest=Path(td)/"object.bin"
        for row in records:
            if not row.get("key") or not isinstance(row.get("bytes"),int) or not row.get("sha256"):
                results.append({"key":row.get("key"),"status":"invalid_receipt"}); continue
            dest.unlink(missing_ok=True)
            proc=subprocess.run([cli,"r2","object","get",f"{args.bucket}/{row['key']}","--remote","--file",str(dest)],
                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
            if proc.returncode or not dest.is_file():
                results.append({"key":row["key"],"status":"remote_read_failed"}); continue
            size=dest.stat().st_size; digest=hashlib.sha256(dest.read_bytes()).hexdigest()
            results.append({"key":row["key"],"expected_bytes":row["bytes"],"actual_bytes":size,
                            "expected_sha256":row["sha256"],"actual_sha256":digest,
                            "status":"verified" if size==row["bytes"] and digest==row["sha256"] else "mismatch"})
    summary={"checked_at_utc":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
             "bucket":args.bucket,"mode":"remote_only","objects_checked":len(results),
             "verified":sum(x["status"]=="verified" for x in results),"failures":[x for x in results if x["status"]!="verified"],
             "results":results}
    rendered=json.dumps(summary,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        output=(ROOT/args.output).resolve()
        if ROOT not in output.parents: raise SystemExit("output must remain inside repository")
        output.parent.mkdir(parents=True,exist_ok=True); output.write_text(rendered)
    print(json.dumps({k:v for k,v in summary.items() if k!="results"},ensure_ascii=False,indent=2))
    return 0 if not summary["failures"] else 1

if __name__=="__main__": raise SystemExit(main())
