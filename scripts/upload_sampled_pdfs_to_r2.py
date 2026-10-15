#!/usr/bin/env python3
"""Upload the frozen sampled arXiv PDFs to a private R2 bucket with a ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", default="ai4cs")
    parser.add_argument("--prefix", default="scientific-discovery/fulltexts/sampled-pdfs-2026-10-12")
    parser.add_argument("--source-manifest", type=Path, default=ROOT / "data/fulltext_download_manifest.jsonl")
    parser.add_argument("--upload-manifest", type=Path, default=ROOT / "data/fulltext_r2_upload_manifest.jsonl")
    parser.add_argument("--preuploaded", action="append", default=[], help="versioned arXiv ID uploaded successfully in a prior step")
    parser.add_argument("--id", dest="requested_ids", action="append", default=[], help="upload only this downloaded arXiv ID; repeat for multiple IDs")
    parser.add_argument("--verify-only", action="store_true", help="download every recorded R2 object temporarily and verify its SHA-256")
    args = parser.parse_args()

    all_sources = read_jsonl(args.source_manifest)
    requested_ids = {item.split("v", 1)[0] for item in args.requested_ids}
    sources = [row for row in all_sources if not requested_ids or str(row.get("arxiv_id")) in requested_ids]
    found_ids = {str(row.get("arxiv_id")) for row in sources}
    if missing_ids := requested_ids - found_ids:
        raise ValueError(f"requested IDs are not present in the source manifest: {', '.join(sorted(missing_ids))}")
    recorded: dict[str, dict[str, object]] = {}
    if args.upload_manifest.exists():
        for row in read_jsonl(args.upload_manifest):
            recorded[str(row["versioned_id"])] = row

    if args.verify_only:
        verify_records = recorded
        if requested_ids:
            verify_records = {
                versioned_id: row
                for versioned_id, row in recorded.items()
                if str(row.get("arxiv_id")) in requested_ids
            }
            verified_ids = {str(row.get("arxiv_id")) for row in verify_records.values()}
            if missing_ids := requested_ids - verified_ids:
                raise ValueError(f"requested IDs are not present in the upload ledger: {', '.join(sorted(missing_ids))}")
        verified = 0
        with tempfile.TemporaryDirectory(prefix="ai4cs-r2-verify-") as temp_dir:
            for versioned_id, row in verify_records.items():
                if row.get("status") != "uploaded":
                    continue
                local_copy = Path(temp_dir) / f"{versioned_id}.pdf"
                result = subprocess.run(
                    [
                        "npx", "--yes", "wrangler", "r2", "object", "get",
                        f"{args.bucket}/{row['key']}", "--file", str(local_copy), "--remote",
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(f"R2 download verification failed for {versioned_id}: {(result.stderr or result.stdout).strip()}")
                if sha256_file(local_copy) != row.get("sha256"):
                    raise ValueError(f"Remote checksum mismatch for {versioned_id}")
                verified += 1
                print(f"verified {versioned_id}")
        print(json.dumps({"verified": verified, "bucket": args.bucket, "manifest": str(args.upload_manifest)}, indent=2))
        return 0

    failed = 0
    uploaded = skipped = 0
    with args.upload_manifest.open("a", encoding="utf-8") as ledger:
        for source in sources:
            versioned_id = str(source["versioned_id"])
            if source.get("status") != "downloaded":
                continue
            pdf = ROOT / str(source["path"])
            digest = sha256_file(pdf)
            if digest != source.get("sha256"):
                raise ValueError(f"Source checksum mismatch for {versioned_id}")
            key = f"{args.prefix}/{versioned_id}.pdf"

            prior = recorded.get(versioned_id)
            if prior:
                if prior.get("sha256") != digest or prior.get("key") != key:
                    raise ValueError(f"Existing upload ledger conflicts for {versioned_id}")
                skipped += 1
                continue

            if versioned_id in args.preuploaded:
                row = {
                    "versioned_id": versioned_id,
                    "arxiv_id": source["arxiv_id"],
                    "title": source["title"],
                    "key": key,
                    "bytes": pdf.stat().st_size,
                    "sha256": digest,
                    "status": "uploaded",
                    "method": "wrangler_r2_object_put_success",
                }
                ledger.write(json.dumps(row, ensure_ascii=False) + "\n")
                ledger.flush()
                recorded[versioned_id] = row
                skipped += 1
                continue

            command = [
                "npx", "--yes", "wrangler", "r2", "object", "put",
                f"{args.bucket}/{key}", "--file", str(pdf),
                "--content-type", "application/pdf", "--remote",
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            row = {
                "versioned_id": versioned_id,
                "arxiv_id": source["arxiv_id"],
                "title": source["title"],
                "key": key,
                "bytes": pdf.stat().st_size,
                "sha256": digest,
                "status": "uploaded" if result.returncode == 0 else "failed",
                "method": "wrangler_r2_object_put",
            }
            ledger.write(json.dumps(row, ensure_ascii=False) + "\n")
            ledger.flush()
            recorded[versioned_id] = row
            if result.returncode == 0:
                uploaded += 1
                print(f"uploaded {versioned_id}")
            else:
                failed += 1
                print(f"FAILED {versioned_id}: {(result.stderr or result.stdout).strip()}")

    print(json.dumps({"uploaded_this_run": uploaded, "already_recorded": skipped, "failed": failed, "manifest": str(args.upload_manifest)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
