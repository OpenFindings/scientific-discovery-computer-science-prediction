#!/usr/bin/env python3
"""Recover batch-34 papers with canonical PMLR URLs but no arXiv identifier."""
import datetime as dt, hashlib, html.parser, json, tempfile
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOST = "proceedings.mlr.press"

class PdfLinks(html.parser.HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag.lower()=="a":
            for k,v in attrs:
                if k.lower()=="href" and v and ".pdf" in v.lower(): self.links.append(v)

def get(url: str, timeout: int = 40) -> tuple[bytes,str,str]:
    if urlparse(url).hostname != ALLOWED_HOST or urlparse(url).scheme != "https":
        raise ValueError("URL is outside the approved PMLR HTTPS host")
    req=Request(url,headers={"User-Agent":"ScientificDiscoveryResearch/1.0 (paper recovery)"})
    with urlopen(req,timeout=timeout) as response:
        data=response.read(100*1024*1024+1)
        if len(data)>100*1024*1024: raise ValueError("response exceeds 100 MiB")
        return data,response.headers.get("Content-Type",""),response.geturl()

def main():
    ledger=ROOT/"data/fulltext_review_ledger_batch34.jsonl"
    records=[json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
    missing=[(i,r) for i,r in enumerate(records,1) if not r.get("arxiv_id") and r.get("source_url")]
    out=[]
    for line,row in missing:
        source=row["source_url"]
        if urlparse(source).hostname != ALLOWED_HOST: raise SystemExit(f"unapproved source host on ledger line {line}")
        if source.lower().endswith(".pdf"):
            pdf_url=source if source.startswith("https://") else "https://"+source.split("//",1)[-1]
        else:
            page,_,_=get(source)
            parser=PdfLinks(); parser.feed(page.decode("utf-8","replace"))
            candidates=[urljoin(source,x) for x in parser.links if urlparse(urljoin(source,x)).hostname==ALLOWED_HOST]
            if not candidates: raise SystemExit(f"no canonical PDF link found on ledger line {line}")
            pdf_url=candidates[0]
            if pdf_url.startswith("http://"): pdf_url="https://"+pdf_url[len("http://"):]
        pdf,ctype,resolved=get(pdf_url)
        if not pdf.startswith(b"%PDF-"): raise SystemExit(f"non-PDF response for ledger line {line}: {ctype}")
        target=ROOT/f"data/fulltexts/recovered_batches/34/source-line-{line}.pdf"
        if target.exists(): raise SystemExit(f"refusing to overwrite {target}")
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir="/private/tmp",prefix="pmlr-paper-",suffix=".pdf",delete=False) as f:
            f.write(pdf); tmp=Path(f.name)
        tmp.replace(target)
        out.append({"batch":34,"ledger_line":line,"arxiv_id":None,"title":row.get("title"),"source_url":source,
                    "pdf_url":pdf_url,"resolved_url":resolved,"retrieved_at_utc":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
                    "status":"downloaded","path":str(target.relative_to(ROOT)),"bytes":len(pdf),"sha256":hashlib.sha256(pdf).hexdigest(),"content_type":ctype})
        print(f"batch34 source row {line}: downloaded and SHA-256 recorded",flush=True)
    manifest=ROOT/"data/fulltext_recovery_manifest_batch34_sources.jsonl"
    manifest.write_text("".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
    report=ROOT/"reports/fulltext_batch34_source_recovery.json"
    report.write_text(json.dumps({"papers":len(out),"records":out,"scope":"source-linked PMLR full text; does not independently validate the existing audit"},ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"recovered":len(out),"report":str(report.relative_to(ROOT))},indent=2))

if __name__=="__main__": main()
