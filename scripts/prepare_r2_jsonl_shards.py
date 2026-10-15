#!/usr/bin/env python3
"""Split a JSONL corpus into independently gzip-compressed, checksummed shards.

This supports resumable object-store uploads where a single-object client has a
size limit. Each shard ends on a complete input record and can be decompressed
independently; concatenating the decoded shards in numeric order reconstructs
the original JSONL stream exactly.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--records-per-shard", type=int, default=100_000)
    args = parser.parse_args()

    if args.records_per_shard < 1:
        parser.error("--records-per-shard must be positive")
    if not args.input.is_file():
        parser.error(f"input file not found: {args.input}")

    # Refuse to overwrite existing outputs: a partial previous run must be
    # inspected or placed aside explicitly rather than silently replaced.
    args.output_dir.mkdir(parents=True, exist_ok=False)

    source_hash = hashlib.sha256()
    source_bytes = 0
    total_records = 0
    shards: list[dict[str, object]] = []
    source = args.input.open("rb")
    try:
        while True:
            shard_number = len(shards) + 1
            shard_name = f"part-{shard_number:03d}.jsonl.gz"
            shard_path = args.output_dir / shard_name
            record_count = 0
            with shard_path.open("wb") as raw_out:
                with gzip.GzipFile(fileobj=raw_out, mode="wb", compresslevel=6, mtime=0) as compressed:
                    while record_count < args.records_per_shard:
                        line = source.readline()
                        if not line:
                            break
                        source_hash.update(line)
                        source_bytes += len(line)
                        if not line.endswith(b"\n"):
                            raise ValueError(f"input contains a non-newline-terminated record at line {total_records + 1}")
                        compressed.write(line)
                        record_count += 1
                        total_records += 1
            if record_count == 0:
                shard_path.unlink()
                break
            shards.append({
                "key_suffix": shard_name,
                "records": record_count,
                "compressed_bytes": shard_path.stat().st_size,
                "compressed_sha256": sha256_file(shard_path),
            })
    finally:
        source.close()

    manifest = {
        "format": "jsonl-gzip-independent-shards-v1",
        "source_filename": args.input.name,
        "source_bytes": source_bytes,
        "source_sha256": source_hash.hexdigest(),
        "records": total_records,
        "records_per_shard_target": args.records_per_shard,
        "shards": shards,
        "reconstruction": "gzip-decompress each shard in numeric key order and concatenate the resulting byte streams",
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "records": total_records,
        "source_bytes": source_bytes,
        "source_sha256": source_hash.hexdigest(),
        "shards": [{k: s[k] for k in ("key_suffix", "records", "compressed_bytes")} for s in shards],
        "manifest": str(manifest_path),
    }, indent=2))


if __name__ == "__main__":
    main()
