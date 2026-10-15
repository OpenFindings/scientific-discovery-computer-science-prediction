# Initial open-paper collection and question candidates

Collection date: 2026-10-11. The initial batch contains source-linked candidate
questions from open arXiv records across AI/agents, software engineering and
security, computer systems, robotics, algorithms, and efficiency.

The inventory is in `data/research_questions.jsonl`. It currently contains 26
question candidates and paper links. Bibliographic metadata for all 29 unique
arXiv records is in `data/literature_sources.jsonl`. Each record stores a falsifiable question,
the evidence basis from the cited paper, a proposed experiment, source IDs, and
an evidence-status note. The sources are open to read; this does not imply that
all paper text or derived datasets have a permissive reuse license.

The candidate questions were prepared from paper records and accessible
abstract/full-text excerpts. They are a collection stage, not completed
full-text extraction. Before a candidate enters the historical forecasting
registry, a researcher still needs to inspect the relevant paper sections,
record exact page/section locators and paper version, check related and
contradictory studies, resolve duplicates, assign question clusters, and code
pre-cutoff features without using future evidence. No outcome labels or model
scores have been attached to this batch.

Run `python3 scripts/audit_question_candidates.py` to validate record shape,
unique IDs, and source URL domains. The transfer runner reports the candidate
inventory but does not forecast until records are fully coded in
`data/questions.jsonl`.

The latest local audit found 26 unique question IDs, 32 source-link occurrences,
29 distinct arXiv IDs, 29 matching metadata records, and zero outcome labels.
Titles, authors, dates, current arXiv version IDs, and abstract/PDF URLs were
retrieved from arXiv's public metadata API on 2026-10-11. Venue status is
explicitly marked unverified unless confirmed from the paper front matter.
Licenses and exact section/page locators still need to be recorded for the
remaining candidates during full-text review. Five source papers have received a
section-level spot audit; checked sections and the claims used for extraction
are documented in `docs/fulltext_audit.md`. Six question records carry those
locators because two separate questions come from the same OK-Robot paper.

## Coverage represented in this batch

- Agent memory, security, long-horizon inference, desktop agents, and
  multi-agent coordination.
- Repository-level issue repair, code-change assurance, LLM-generated tests,
  code hallucinations, vulnerability repair, dependency reachability, and
  secure agents.
- Continual learning, inference energy, and model efficiency.
- Robot memory, error recovery, and simulation-to-reality transfer.
- Compiler fuzzing, database testing, deep-learning compiler testing, and
  algorithmic reasoning.

This is a broad initial seed set, not yet a representative sample of computer
science. It is also weighted toward topics with easy-to-access arXiv papers.

## Full arXiv CS metadata harvest (2010–2026)

The 29-record arXiv seed remains a hand-curated, question-linked set, but it is
no longer the corpus. `data/arxiv_cs_corpus.jsonl` contains **937,531 unique
arXiv records** from the public `cat:cs.*` query, dated 2010-01-01 through
2026-10-11. The collector recorded 937,538 available results across all 68
calendar-quarter cells and retrieved all of them; seven result slots did not
add a new retained canonical record (duplicate IDs or invalid/missing metadata).
The corpus contains titles, abstracts, authors, publication/update dates, current
version IDs, primary and cross-list categories, DOI/journal references when
available, and abstract/PDF links. Audit coverage is 100% for abstracts and PDF
links. The raw JSONL is about 1.6 GB; the detailed per-quarter ledger is in
`data/arxiv_cs_manifest.json`.

Of the unique records, 816,895 have a `cs.*` primary category; 120,636 have a
non-CS primary category but are cross-listed into computer science. Keep those
groups distinguishable in analyses. Primary-category volumes are especially
large for Computer Vision (cs.CV), Machine Learning (cs.LG), NLP (cs.CL), AI
(cs.AI), Robotics (cs.RO), Security (cs.CR), and Software Engineering
(cs.SE). This is a comprehensive arXiv-CS discovery corpus, **not all CS
literature**: conference/journal-only papers absent from arXiv are missing,
preprints and published versions are not yet adjudicated as duplicates, and
venue/peer-review status has not been fully verified.

Use `scripts/collect_arxiv_cs.py` to resume or update the quarter-by-quarter
harvest, and `scripts/audit_arxiv_cs_corpus.py` to check IDs, date coverage,
abstract/PDF links, categories, and page-completion counts. The collector
respects arXiv's three-second request pacing and its 2,000-result page / 30,000
result query constraints, splitting large date ranges into smaller windows.
Exact query counts, retrieved counts, duplicate handling, and checkpoints are
recorded in the manifest and `data/arxiv_cs_checkpoint.json`.

The descriptive first-pass profile is saved at `data/arxiv_cs_profile.json`.
It groups records into 58,146 (2010–2014), 162,261 (2015–2019), 425,453
(2020–2024), and 291,671 (2025–2026, with 2026 observed only through October
11). The largest primary arXiv categories are cs.CV (162,835), cs.LG
(147,463), cs.CL (88,924), cs.AI (47,200), cs.RO (45,028), and cs.CR
(35,738). Broad keyword screens flag, among other overlapping groups,
109,387 abstracts/titles containing foundation-model/LLM terms and 2,114
containing software-testing terms. These lexical counts are only navigation
signals: keyword definitions, abstract phrasing, and cross-listing affect
them; they are not estimates of research value, open questions, or attention.

## Complementary OpenAlex discovery sample

`data/openalex_cs_corpus.jsonl` is a separate, smaller sample produced by
`scripts/collect_openalex_cs.py`: up to 200 relevance-ranked OA works for each
of 18 topic queries and four time strata. Its first run collected 9,747 raw
records (9,746 with titles) before the provider returned HTTP 429, covering 13
topics and leaving a resumable checkpoint. It is not added to the arXiv count;
the sources overlap and require DOI/title deduplication before combined
analysis. OpenAlex records add venues, OA/license information, topics, and
collection-time citation/reference metadata.

Neither metadata corpus means every full text has been downloaded or read.
Open-access links and arXiv PDF URLs support full-text retrieval for screening,
but claims used in extracted research questions still need source-level review,
exact version and page/section locators, contradictory-study search, and
licensing checks. OpenAlex citation counts captured today must never be treated
as historically frozen features. The 29 seed questions remain the only
question-linked, manually prepared batch; the new 937k-paper corpus has not yet
been fully question-extracted or forecast-scored.

Next ingestion should add complementary conference/journal sources such as
DBLP, Crossref, OpenReview, ACL Anthology, and Semantic Scholar where API access
permits, then estimate venue coverage and overlap rather than implying the
arXiv corpus is a complete census of computer science.
