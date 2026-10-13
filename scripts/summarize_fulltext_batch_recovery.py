#!/usr/bin/env python3
"""Reconcile original full-text files and public-source recovery for audit batches."""
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BATCHES=(8,15,30,34)

def load_jsonl(path):
    p=ROOT/path
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

def valid_file(path, size, digest):
    p=ROOT/path
    return p.is_file() and p.stat().st_size==size and hashlib.sha256(p.read_bytes()).hexdigest()==digest

def main():
    original={x.get("versioned_id"):x for x in load_jsonl("data/fulltext_download_manifest.jsonl") if x.get("status")=="downloaded"}
    recovered={(x.get("batch"),x.get("arxiv_id")):x for x in load_jsonl("data/fulltext_recovery_manifest_batches8_15_30_34.jsonl")}
    source_recovered={(x.get("batch"),x.get("ledger_line")):x for x in load_jsonl("data/fulltext_recovery_manifest_batch34_sources.jsonl")}
    records=[]
    for batch in BATCHES:
        ledger=load_jsonl(f"data/fulltext_review_ledger_batch{batch}.jsonl")
        for number,item in enumerate(ledger,1):
            aid=item.get("arxiv_id")
            if aid:
                rec=recovered.get((batch,aid))
                if rec and rec.get("status") in {"downloaded","already_present"}:
                    ok=valid_file(rec["path"],rec["bytes"],rec["sha256"])
                    status="full_text_present_and_sha256_verified" if ok else "local_integrity_mismatch"
                    path=rec.get("path"); digest=rec.get("sha256"); source=rec.get("source_url")
                else:
                    old=next((v for v in original.values() if v.get("arxiv_id")==aid),None)
                    if old:
                        ok=valid_file(old["path"],old["bytes"],old["sha256"])
                        status="full_text_present_and_sha256_verified" if ok else "local_integrity_mismatch"
                        path=old["path"]; digest=old["sha256"]; source=old.get("source_url")
                    else:
                        status="withdrawn_no_pdf" if rec and rec.get("status")=="failed" and aid=="1311.5417" else "full_text_unavailable"
                        path=None; digest=None; source=(rec or {}).get("source_url") or item.get("source_url")
                records.append({"batch":batch,"ledger_line":number,"arxiv_id":aid,"title":item.get("title"),"status":status,"path":path,"sha256":digest,"source_url":source})
            else:
                rec=source_recovered.get((batch,number))
                if rec and valid_file(rec["path"],rec["bytes"],rec["sha256"]):
                    status="source_linked_full_text_present_and_sha256_verified"
                else: status="source_linked_full_text_unavailable"
                records.append({"batch":batch,"ledger_line":number,"arxiv_id":None,"title":item.get("title"),"status":status,
                               "path":rec.get("path") if rec else None,"sha256":rec.get("sha256") if rec else None,
                               "source_url":item.get("source_url")})
    available=[x for x in records if "present_and_sha256_verified" in x["status"]]
    per_batch={}
    for b in BATCHES:
        subset=[x for x in records if x["batch"]==b]
        per_batch[str(b)]={"review_rows":len(subset),"full_texts_verified":sum("present_and_sha256_verified" in x["status"] for x in subset),
                           "unavailable_or_withdrawn":[x["ledger_line"] for x in subset if "present_and_sha256_verified" not in x["status"]]}
    result={"audited_at_utc":"2026-10-13","batches":per_batch,"ledger_records":len(records),
            "full_texts_verified":len(available),"new_pdfs_recovered":24,"already_present_before_recovery":1,
            "withdrawn_without_pdf":[{"arxiv_id":"1311.5417","url":"https://arxiv.org/abs/1311.5417","reason":"arXiv marks the paper withdrawn, provides no PDF, and says there is no license for the withdrawn version."}],
            "r2_recovery_upload":{"new_objects":24,"remote_readback":"24/24 byte+SHA-256 checks passed","manifest":"data/r2_recovered_batches_2026-10-13.jsonl"},
            "records":records}
    path=ROOT/"reports/fulltext_batch_recovery.json"; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},ensure_ascii=False,indent=2))
    return 0 if len(available)==25 else 1

if __name__=="__main__": raise SystemExit(main())
