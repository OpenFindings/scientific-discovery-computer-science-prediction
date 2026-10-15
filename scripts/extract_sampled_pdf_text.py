#!/usr/bin/env python3
"""Extract auditable text and page counts from downloaded sampled PDFs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOWNLOADS = ROOT / "data/fulltext_download_manifest.jsonl"
DEFAULT_OUTPUT = ROOT / "data/fulltexts/text"
DEFAULT_MANIFEST = ROOT / "data/fulltext_extraction_manifest.jsonl"
POPPLER_BIN = Path("/Users/amao/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--downloads", type=Path, default=DEFAULT_DOWNLOADS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--id", dest="requested_ids", action="append", default=[], help="extract only this downloaded arXiv ID; repeat for multiple IDs")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    pdftotext = POPPLER_BIN / "pdftotext"
    pdfinfo = POPPLER_BIN / "pdfinfo"
    if not pdftotext.is_file() or not pdfinfo.is_file():
        raise SystemExit(f"Poppler utilities not found under {POPPLER_BIN}")

    previous = {}
    if args.manifest.exists():
        previous = {r["versioned_id"]: r for r in read_jsonl(args.manifest)}
    requested_ids = {item.split("v", 1)[0] for item in args.requested_ids}
    all_rows = [r for r in read_jsonl(args.downloads) if r.get("status") == "downloaded"]
    rows = [r for r in all_rows if not requested_ids or str(r.get("arxiv_id")) in requested_ids]
    found_ids = {str(r.get("arxiv_id")) for r in rows}
    if missing_ids := requested_ids - found_ids:
        raise ValueError(f"requested IDs are not present as downloaded PDFs: {', '.join(sorted(missing_ids))}")
    todo = [r for r in rows if r["versioned_id"] not in previous]
    if args.limit is not None:
        todo = todo[:max(0, args.limit)]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    successes = failures = 0
    with args.manifest.open("a", encoding="utf-8") as manifest:
        for i, row in enumerate(todo, 1):
            pdf = ROOT / row["path"]
            output = args.output_dir / f"{safe_name(row['versioned_id'])}.txt"
            try:
                extracted = subprocess.run(
                    [str(pdftotext), "-layout", str(pdf), "-"],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                ).stdout
                if len(extracted.strip()) < 200:
                    raise ValueError(f"extracted text is unexpectedly short ({len(extracted)} bytes)")
                info = subprocess.run(
                    [str(pdfinfo), str(pdf)], check=True, text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                ).stdout
                pages_line = next((line for line in info.splitlines() if line.startswith("Pages:")), None)
                pages = int(pages_line.split(":", 1)[1].strip()) if pages_line else None
                output.write_bytes(extracted)
                entry = {
                    "versioned_id": row["versioned_id"],
                    "arxiv_id": row["arxiv_id"],
                    "title": row.get("title"),
                    "pdf_path": row["path"],
                    "text_path": str(output.relative_to(ROOT)),
                    "pages": pages,
                    "text_bytes": len(extracted),
                    "text_sha256": hashlib.sha256(extracted).hexdigest(),
                    "extractor": str(pdftotext),
                    "status": "extracted",
                }
                successes += 1
            except Exception as exc:
                entry = {
                    "versioned_id": row["versioned_id"],
                    "arxiv_id": row.get("arxiv_id"),
                    "title": row.get("title"),
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
                failures += 1
            manifest.write(json.dumps(entry, ensure_ascii=False) + "\n")
            manifest.flush()
            print(json.dumps({"i": i, "n": len(todo), "id": row["versioned_id"], "status": entry["status"], "pages": entry.get("pages"), "text_bytes": entry.get("text_bytes")}, ensure_ascii=False), flush=True)
    print(json.dumps({"attempted": len(todo), "extracted": successes, "failed": failures, "manifest": str(args.manifest.relative_to(ROOT)) if args.manifest.is_relative_to(ROOT) else str(args.manifest)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
