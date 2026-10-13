#!/usr/bin/env python3
"""Recover missing public arXiv PDFs referenced by local audit batches 8, 15, 30, 34."""
import argparse, datetime as dt, hashlib, json, re, tempfile, time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BATCHES = (8, 15, 30, 34)
MAX_PDF_BYTES = 100 * 1024 * 1024

def utcnow(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=f".{path.name}.", dir=path.parent, delete=False) as f:
        name = f.name; f.write(value); f.flush()
    Path(name).replace(path)

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args(); root = args.root.resolve()
    manifest = root / "data/fulltext_recovery_manifest_batches8_15_30_34.jsonl"
    report = root / "reports/fulltext_batch_recovery.json"
    existing_rows = {}
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            if line.strip():
                row = json.loads(line); existing_rows[(row["batch"], row.get("arxiv_id"))] = row
    rows, failures, missing_identifiers = [], [], []
    for batch in BATCHES:
        source = root / f"data/fulltext_review_ledger_batch{batch}.jsonl"
        if not source.exists():
            failures.append({"batch": batch, "error": "local review ledger missing"}); continue
        for line_number, line in enumerate(source.read_text().splitlines(), 1):
            if not line.strip(): continue
            audit = json.loads(line); arxiv_id = audit.get("arxiv_id")
            if not arxiv_id:
                missing_identifiers.append({"batch": batch, "line": line_number, "title": audit.get("title"),
                                            "source_url": audit.get("source_url"), "status": "cannot_recover_without_identifier"})
                continue
            if not re.fullmatch(r"\d{4}\.\d{4,5}", arxiv_id):
                failures.append({"batch": batch, "arxiv_id": arxiv_id, "error": "arXiv identifier failed safety validation"})
                continue
            saved = existing_rows.get((batch, arxiv_id))
            if saved and saved.get("status") in {"downloaded", "already_present"} and saved.get("path") and (root / saved["path"]).is_file():
                rows.append(saved); continue
            # Never overwrite another downloaded version of the same paper.
            already = sorted((root / "data/fulltexts").rglob(f"{arxiv_id}v*.pdf"))
            dest = root / "data/fulltexts/recovered_batches" / str(batch) / f"{arxiv_id}.pdf"
            if already:
                p = already[0]; data = p.read_bytes()
                row = {"batch": batch, "arxiv_id": arxiv_id, "title": audit.get("title"), "source_url": f"https://arxiv.org/pdf/{arxiv_id}",
                       "retrieved_at_utc": utcnow(), "status": "already_present", "path": str(p.relative_to(root)), "bytes": len(data),
                       "sha256": hashlib.sha256(data).hexdigest()}
                rows.append(row); existing_rows[(batch, arxiv_id)] = row; continue
            url = f"https://arxiv.org/pdf/{arxiv_id}"
            result = None
            for attempt in range(args.retries + 1):
                temp_name = None
                try:
                    request = Request(url, headers={"User-Agent": "ScientificDiscoveryResearch/1.0 (recovery audit; contact: repo owner)"})
                    with urlopen(request, timeout=args.timeout) as response:
                        content_type = response.headers.get("Content-Type", "")
                        with tempfile.NamedTemporaryFile(prefix=f"{arxiv_id}-", suffix=".pdf", dir="/private/tmp", delete=False) as temp:
                            temp_name = temp.name; digest = hashlib.sha256(); total = 0; first = b""
                            while chunk := response.read(1024 * 1024):
                                if not first: first = chunk[:16]
                                total += len(chunk)
                                if total > MAX_PDF_BYTES: raise ValueError("PDF exceeds 100 MiB limit")
                                digest.update(chunk); temp.write(chunk)
                        if not first.startswith(b"%PDF-"):
                            raise ValueError(f"response is not a PDF (content-type={content_type})")
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        if dest.exists(): raise FileExistsError(f"refusing to overwrite {dest}")
                        Path(temp_name).replace(dest); temp_name = None
                        result = {"batch": batch, "arxiv_id": arxiv_id, "title": audit.get("title"), "source_url": url,
                                  "resolved_url": response.geturl(), "retrieved_at_utc": utcnow(), "status": "downloaded",
                                  "path": str(dest.relative_to(root)), "bytes": total, "sha256": digest.hexdigest(),
                                  "content_type": content_type, "attempt": attempt + 1}
                        break
                except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                    result = {"batch": batch, "arxiv_id": arxiv_id, "title": audit.get("title"), "source_url": url,
                              "retrieved_at_utc": utcnow(), "status": "failed", "attempt": attempt + 1,
                              "error_type": type(exc).__name__, "error": str(exc)[:500]}
                    if temp_name:
                        Path(temp_name).unlink(missing_ok=True)
                    if attempt < args.retries: time.sleep(min(2 ** attempt, 8))
            rows.append(result); existing_rows[(batch, arxiv_id)] = result
            # Checkpoint each item so interruptions do not lose successful downloads.
            atomic_text(manifest, "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in existing_rows.values()))
            print(f"batch {batch} {arxiv_id}: {result['status']}", flush=True)
    ordered = sorted(existing_rows.values(), key=lambda x: (x["batch"], x.get("arxiv_id") or ""))
    atomic_text(manifest, "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in ordered))
    ok = [x for x in ordered if x.get("status") in {"downloaded", "already_present"}]
    failed = [x for x in ordered if x.get("status") == "failed"]
    summary = {"checked_at_utc": utcnow(), "batches": list(BATCHES), "identified_papers": len(ordered),
               "available_with_verified_pdf_and_sha256": len(ok), "failed_or_unavailable": len(failed),
               "unidentified_rows": missing_identifiers, "failures": failed, "manifest": str(manifest.relative_to(root)),
               "note": "Availability means public source retrieval and local PDF integrity only; it does not revalidate the existing paper audit or scientific claim."}
    atomic_text(report, json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if failed else 0

if __name__ == "__main__": raise SystemExit(main())
