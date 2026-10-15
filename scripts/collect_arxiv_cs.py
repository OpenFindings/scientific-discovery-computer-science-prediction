#!/usr/bin/env python3
"""Collect a large, date-stratified arXiv CS metadata corpus (not PDF bulk)."""
from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ENDPOINT = "https://export.arxiv.org/api/query"
OUT = Path("data/arxiv_cs_corpus.jsonl")
CHECKPOINT = Path("data/arxiv_cs_checkpoint.json")
MANIFEST = Path("data/arxiv_cs_manifest.json")
MAX_PER_QUARTER = 2000
MAX_SAFE_OFFSET = 8000
ATOM = "http://www.w3.org/2005/Atom"
ARXIV = "http://arxiv.org/schemas/atom"
OPEN_SEARCH = "http://a9.com/-/spec/opensearch/1.1/"


def quarter_ranges():
    for year in range(2010, 2027):
        for quarter, start_month, end_month in ((1, 1, 3), (2, 4, 6), (3, 7, 9), (4, 10, 12)):
            start = date(year, start_month, 1)
            if quarter == 4 and year == 2026:
                end = date(2026, 10, 11)
            elif end_month == 12:
                end = date(year, 12, 31)
            else:
                end = date(year, end_month + 1, 1).fromordinal(date(year, end_month + 1, 1).toordinal() - 1)
            yield f"{year}-Q{quarter}", start, end


def text(node, path):
    element = node.find(path, {"a": ATOM, "arxiv": ARXIV})
    return element.text.strip() if element is not None and element.text else None


def compact(entry, period):
    raw_id = text(entry, "a:id") or ""
    match = re.search(r"arxiv.org/abs/([^?#]+)", raw_id)
    versioned_id = match.group(1) if match else None
    arxiv_id = re.sub(r"v\d+$", "", versioned_id or "")
    authors = [item.text.strip() for item in entry.findall("a:author/a:name", {"a": ATOM}) if item.text]
    categories = sorted({item.get("term") for item in entry.findall("a:category", {"a": ATOM}) if item.get("term")})
    primary = entry.find("arxiv:primary_category", {"arxiv": ARXIV})
    links = entry.findall("a:link", {"a": ATOM})
    pdf_url = next((link.get("href") for link in links if link.get("title") == "pdf"), None)
    abs_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None
    doi = text(entry, "arxiv:doi")
    return {
        "arxiv_id": arxiv_id, "versioned_id": versioned_id, "title": text(entry, "a:title"),
        "abstract": text(entry, "a:summary"), "authors": authors,
        "published": text(entry, "a:published"), "updated": text(entry, "a:updated"),
        "primary_category": primary.get("term") if primary is not None else None,
        "categories": categories, "journal_reference": text(entry, "arxiv:journal_ref"),
        "doi": doi, "abstract_url": abs_url, "pdf_url": pdf_url,
        "retrieved_via": {"source": "arXiv API", "category_query": "cs.*", "submitted_date_stratum": period},
    }


def fetch(params):
    url = ENDPOINT + "?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "ScientificDiscoveryOpenLiterature/1.0"})
    for attempt in range(8):
        try:
            with urlopen(request, timeout=120) as response:
                root = ET.parse(response).getroot()
                # Keep a polite delay between every API request, including recursive date windows.
                time.sleep(3.2)
                return root
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 7:
                raise
            retry_after = error.headers.get("Retry-After") if error.headers else None
            delay = int(retry_after) if retry_after and retry_after.isdigit() else min(3 * (attempt + 1), 60)
            time.sleep(delay)
        except (URLError, TimeoutError):
            if attempt == 7:
                raise
            time.sleep(min(3 * (attempt + 1), 60))
    raise RuntimeError("unreachable retry state")


def query_text(start, end):
    return f"cat:cs.* AND submittedDate:[{start:%Y%m%d}0000 TO {end:%Y%m%d}2359]"


def append_entries(entries, period, known):
    added = 0
    with OUT.open("a", encoding="utf-8") as stream:
        for entry in entries:
            record = compact(entry, period)
            if not record["arxiv_id"] or not record["title"] or record["arxiv_id"] in known:
                continue
            known.add(record["arxiv_id"])
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            added += 1
        stream.flush()
    return added


def collect_bounded_range(start, end, period, known):
    """Fetch a date range, recursively splitting it to avoid unstable deep offsets."""
    query = query_text(start, end)
    root = fetch({"search_query": query, "start": 0, "max_results": MAX_PER_QUARTER,
                  "sortBy": "submittedDate", "sortOrder": "descending"})
    entries = root.findall("a:entry", {"a": ATOM})
    total = int(root.findtext(f"{{{OPEN_SEARCH}}}totalResults") or len(entries))
    added = append_entries(entries, period, known)
    offset = len(entries)
    if offset >= total:
        return total, added
    if total > MAX_SAFE_OFFSET:
        if start >= end:
            raise RuntimeError(f"single-day range exceeds safe offset: {start} ({total} results)")
        midpoint = start.fromordinal((start.toordinal() + end.toordinal()) // 2)
        left_total, left_added = collect_bounded_range(start, midpoint, period, known)
        right_start = midpoint.fromordinal(midpoint.toordinal() + 1)
        right_total, right_added = collect_bounded_range(right_start, end, period, known)
        return left_total + right_total, added + left_added + right_added
    while offset < total:
        page = fetch({"search_query": query, "start": offset, "max_results": MAX_PER_QUARTER,
                      "sortBy": "submittedDate", "sortOrder": "descending"})
        page_entries = page.findall("a:entry", {"a": ATOM})
        if not page_entries:
            break
        added += append_entries(page_entries, period, known)
        offset += len(page_entries)
    return total, added


def main():
    checkpoint = json.loads(CHECKPOINT.read_text()) if CHECKPOINT.exists() else {"completed": {}}
    if OUT.exists():
        completed = checkpoint.get("completed", {})
        known = set()
        with OUT.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    record = json.loads(line)
                    if record.get("arxiv_id"):
                        known.add(record["arxiv_id"])
    else:
        # A checkpoint without its ignored raw corpus cannot certify local rows.
        completed = {}
        known = set()
    cell_results = dict(completed)
    requests = 0
    for period, start, end in quarter_ranges():
        prior = cell_results.get(period, {})
        available = int(prior.get("api_results_available", 0))
        offset = int(prior.get("api_results_returned", 0))
        if period in completed and offset >= available:
            continue
        query = query_text(start, end)
        quarter_added = 0
        if offset >= MAX_SAFE_OFFSET and offset < available:
            total, quarter_added = collect_bounded_range(start, end, period, known)
            cell_results[period] = {"api_results_available": available, "api_results_returned": available,
                                    "new_unique_records": int(prior.get("new_unique_records", 0)) + quarter_added,
                                    "page_size": MAX_PER_QUARTER, "retrieval_strategy": "recursive date windows"}
            CHECKPOINT.write_text(json.dumps({"completed": cell_results}, ensure_ascii=False, indent=2) + "\n")
            print(f"{period}: date-window fallback covered {total} query results; "
                  f"{quarter_added} new, {len(known):7d} unique", flush=True)
            continue
        while True:
            if offset >= MAX_SAFE_OFFSET and offset < available:
                total, added_by_windows = collect_bounded_range(start, end, period, known)
                quarter_added += added_by_windows
                offset = available
                cell_results[period] = {"api_results_available": available, "api_results_returned": offset,
                                        "new_unique_records": int(prior.get("new_unique_records", 0)) + quarter_added,
                                        "page_size": MAX_PER_QUARTER, "retrieval_strategy": "recursive date windows"}
                CHECKPOINT.write_text(json.dumps({"completed": cell_results}, ensure_ascii=False, indent=2) + "\n")
                print(f"{period}: date-window fallback covered {total} query results; "
                      f"{added_by_windows} new this fallback, {len(known):7d} unique", flush=True)
                break
            root = fetch({"search_query": query, "start": offset, "max_results": MAX_PER_QUARTER,
                          "sortBy": "submittedDate", "sortOrder": "descending"})
            requests += 1
            entries = root.findall("a:entry", {"a": ATOM})
            total_text = root.findtext(f"{{{OPEN_SEARCH}}}totalResults")
            if total_text is not None:
                available = int(total_text)
            added = 0
            with OUT.open("a", encoding="utf-8") as stream:
                for entry in entries:
                    record = compact(entry, period)
                    if not record["arxiv_id"] or not record["title"] or record["arxiv_id"] in known:
                        continue
                    known.add(record["arxiv_id"])
                    stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                    added += 1
                stream.flush()
            quarter_added += added
            offset += len(entries)
            cell_results[period] = {"api_results_available": available, "api_results_returned": offset,
                                    "new_unique_records": int(prior.get("new_unique_records", 0)) + quarter_added,
                                    "page_size": MAX_PER_QUARTER}
            CHECKPOINT.write_text(json.dumps({"completed": cell_results}, ensure_ascii=False, indent=2) + "\n")
            print(f"{period}: {offset:5d} returned / {available:7d} available; "
                  f"{added:4d} new this page, {len(known):7d} unique", flush=True)
            if not entries or offset >= available:
                break

    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "arXiv export API", "provider_docs": "https://info.arxiv.org/help/api/user-manual.html",
        "search": "cat:cs.* AND submittedDate within each calendar quarter",
        "date_range": "2010-01-01 through 2026-10-11", "max_results_per_api_page": MAX_PER_QUARTER,
        "unique_papers": len(known), "quarter_cells": cell_results,
        "limitations": [
            "This corpus covers arXiv CS-category submissions, not all CS publication venues.",
            "Queries are paginated in date-bounded quarters; any provider omissions or unstable result counts remain possible.",
            "Records include abstracts and links, not downloaded full text; source versions and licenses must be checked before reuse.",
            "Cross-listed papers may appear under multiple arXiv category codes but are deduplicated by base arXiv ID.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"unique_papers": len(known), "quarters": len(cell_results),
                      "api_requests_this_run": requests, "output": str(OUT),
                      "manifest": str(MANIFEST)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
