#!/usr/bin/env python3
"""Resumeable, rate-limited retrieval of PDFs in the frozen stratified frame.

This only fetches explicitly sampled arXiv records. It does not crawl the full
198,690-paper candidate pool. Successful and failed attempts are checkpointed
to a JSONL manifest so the work can be resumed and audited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "data/fulltext_stratified_sample.jsonl"
LEDGER_GLOB = "fulltext_review_ledger_batch*.jsonl"
DEFAULT_OUTPUT = ROOT / "data/fulltexts/arxiv"
DEFAULT_MANIFEST = ROOT / "data/fulltext_download_manifest.jsonl"
USER_AGENT = "ScientificDiscoveryLiteratureAudit/1.0 (academic full-text retrieval)"


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def reviewed_ids() -> set[str]:
    result: set[str] = set()
    for path in sorted((ROOT / "data").glob(LEDGER_GLOB)):
        for row in read_jsonl(path):
            if row.get("arxiv_id"):
                result.add(str(row["arxiv_id"]))
    return result


def read_attempts(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    attempts = {}
    for row in read_jsonl(path):
        key = row.get("versioned_id") or row.get("arxiv_id")
        if key:
            attempts[str(key)] = row
    return attempts


def safe_name(versioned_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", versioned_id)


def fetch_pdf(url: str, destination: Path, retries: int = 4) -> tuple[int, str]:
    last_error = "unknown error"
    for attempt in range(retries):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
        try:
            with urlopen(request, timeout=90) as response:
                content_type = response.headers.get("Content-Type", "")
                fd, temporary = tempfile.mkstemp(prefix=".arxiv-", suffix=".part", dir=destination.parent)
                size = 0
                digest = hashlib.sha256()
                try:
                    with os.fdopen(fd, "wb") as output:
                        while True:
                            chunk = response.read(1024 * 1024)
                            if not chunk:
                                break
                            output.write(chunk)
                            digest.update(chunk)
                            size += len(chunk)
                        output.flush()
                        os.fsync(output.fileno())
                    with open(temporary, "rb") as check:
                        if size < 1024 or check.read(5) != b"%PDF-":
                            raise ValueError(f"response was not a valid PDF (content-type={content_type!r}, bytes={size})")
                    os.replace(temporary, destination)
                except BaseException:
                    try:
                        os.unlink(temporary)
                    except FileNotFoundError:
                        pass
                    raise
                return size, digest.hexdigest()
        except HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code not in (408, 429, 500, 502, 503, 504):
                break
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt + 1 < retries:
            time.sleep(min(60, 3 * (2**attempt)))
    raise RuntimeError(last_error)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("uniform_random", "lexical_priority", "both"), default="uniform_random")
    parser.add_argument("--only-unreviewed", action="store_true", help="skip any arXiv ID already in a full-text review ledger")
    parser.add_argument("--id", dest="requested_ids", action="append", default=[], help="fetch only this arXiv ID; repeat for multiple IDs")
    parser.add_argument("--version", help="fetch a specific historical arXiv version (for example v1); requires exactly one --id")
    parser.add_argument("--limit", type=int, help="limit the number of new attempts (for smoke tests)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--min-interval", type=float, default=3.1, help="minimum delay between first requests")
    args = parser.parse_args()

    frame = read_jsonl(FRAME)
    attempts = read_attempts(args.manifest)
    done_ids = reviewed_ids() if args.only_unreviewed else set()
    requested_ids = {item.split("v", 1)[0] for item in args.requested_ids}
    if args.version and (len(requested_ids) != 1 or not re.fullmatch(r"v\d+", args.version)):
        raise ValueError("--version requires exactly one --id and a version such as v1")
    arms = {"uniform_random", "lexical_priority"} if args.arm == "both" else {args.arm}
    unique: dict[str, dict] = {}
    for row in frame:
        if row.get("sampling_arm") not in arms:
            continue
        versioned_id = str(row.get("versioned_id") or row["arxiv_id"])
        existing = unique.get(versioned_id)
        if existing:
            existing["frame_memberships"].append({
                "topic": row.get("sampling_topic"),
                "period": row.get("sampling_period"),
                "arm": row.get("sampling_arm"),
            })
        else:
            unique[versioned_id] = {
                **row,
                "frame_memberships": [{
                    "topic": row.get("sampling_topic"),
                    "period": row.get("sampling_period"),
                    "arm": row.get("sampling_arm"),
                }],
            }

    queue = []
    found_ids: set[str] = set()
    for versioned_id, row in sorted(unique.items()):
        if requested_ids and row["arxiv_id"] not in requested_ids:
            continue
        if requested_ids:
            found_ids.add(str(row["arxiv_id"]))
        if args.version and row["arxiv_id"] in requested_ids:
            versioned_id = f"{row['arxiv_id']}{args.version}"
        if row["arxiv_id"] in done_ids:
            continue
        previous = attempts.get(versioned_id, {})
        target = args.output_dir / f"{safe_name(versioned_id)}.pdf"
        if target.exists() and previous.get("status") == "downloaded":
            continue
        queue.append((versioned_id, row, target))
    if missing_ids := requested_ids - found_ids:
        raise ValueError(f"requested IDs are not present in the selected frame/arm: {', '.join(sorted(missing_ids))}")
    if args.limit is not None:
        queue = queue[: max(0, args.limit)]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"queued": len(queue), "arm": args.arm, "only_unreviewed": args.only_unreviewed}, ensure_ascii=False), flush=True)
    last_request = 0.0
    successes = 0
    failures = 0
    with args.manifest.open("a", encoding="utf-8") as manifest:
        for index, (versioned_id, row, target) in enumerate(queue, 1):
            wait = args.min_interval - (time.monotonic() - last_request)
            if last_request and wait > 0:
                time.sleep(wait)
            url = f"https://arxiv.org/pdf/{versioned_id}"
            last_request = time.monotonic()
            entry = {
                "versioned_id": versioned_id,
                "arxiv_id": row["arxiv_id"],
                "title": row.get("title"),
                "source_url": url,
                "sampling_memberships": row["frame_memberships"],
                "retrieved_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            try:
                size, digest = fetch_pdf(url, target)
                entry.update({"status": "downloaded", "path": str(target.relative_to(ROOT)), "bytes": size, "sha256": digest})
                successes += 1
                print(json.dumps({"i": index, "n": len(queue), "id": versioned_id, "status": "downloaded", "bytes": size}, ensure_ascii=False), flush=True)
            except Exception as exc:  # persist item-level failures and continue the sample
                entry.update({"status": "failed", "error": f"{type(exc).__name__}: {exc}"})
                failures += 1
                print(json.dumps({"i": index, "n": len(queue), "id": versioned_id, "status": "failed", "error": str(exc)}, ensure_ascii=False), flush=True)
            manifest.write(json.dumps(entry, ensure_ascii=False) + "\n")
            manifest.flush()
            os.fsync(manifest.fileno())
    print(json.dumps({"attempted": len(queue), "downloaded": successes, "failed": failures, "manifest": str(args.manifest.relative_to(ROOT)) if args.manifest.is_relative_to(ROOT) else str(args.manifest)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
