"""Mechanical check that an evidence quote appears on the cited page (amendment 5)."""

from __future__ import annotations

import html
import re
import subprocess
import unicodedata

UA = "Mozilla/5.0 (OpenFindings research verification)"


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", html.unescape(s or "")).lower()
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                                   "–": "-", "—": "-", " ": " "}))
    return re.sub(r"\s+", " ", re.sub(r"[^\w'\"\-]+", " ", s)).strip()


def page_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"<[^>]+>", " ", raw)


def fetch(url: str, timeout: int = 60) -> tuple[int, str]:
    """Return (http_status, text). PDFs are converted with pdftotext when available."""
    p = subprocess.run(["curl", "-sS", "-L", "-m", str(timeout), "-A", UA, "-w", "\n%{http_code}",
                        "-o", "-", url], capture_output=True)
    body, _, code = p.stdout.rpartition(b"\n")
    status = int(code or 0)
    if body[:5] == b"%PDF-":
        q = subprocess.run(["pdftotext", "-", "-"], input=body, capture_output=True)
        return status, q.stdout.decode("utf-8", "replace")
    return status, page_text(body.decode("utf-8", "replace"))


def verify(url: str, quote: str) -> dict:
    try:
        status, text = fetch(url)
    except Exception as e:  # network failure
        return {"status": "fetch_failed", "detail": type(e).__name__}
    if status >= 400 or not text.strip():
        return {"status": "fetch_failed", "http": status}
    found = normalize(quote) in normalize(text)
    return {"status": "verified" if found else "quote_not_found", "http": status}
