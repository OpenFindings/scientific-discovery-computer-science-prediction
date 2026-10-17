# Amendment 5 to the CS breakthrough forecast preregistration (v1): evidence-based value markers

Frozen: 2026-10-17, **before any evidence search on the 120 sample papers**. G3 (human), and the
GPT and Claude reference raters (amendments 3–4), all rated *impressions* of value. Amendment 4
showed an LLM's impression is dominated by remembered fame. This amendment replaces impressions
with an alternative, **non-citation value standard built from verifiable documentary evidence**,
gathered by AI agents and checked mechanically.

## Question

Does the top-decile citation label (and does the Paper 3 model, among citation negatives) agree
with independent documentary markers of lasting value?

## Markers (frozen; evidence of any date up to retrieval)

- **M1 award:** best / outstanding / distinguished paper or test-of-time award, on an official
  venue, society or organiser page.
- **M2 reference work:** the method or result is explained in the body of a textbook, a university
  course page or lecture notes, or a Wikipedia article (a bare bibliography entry is not enough).
- **M3 adoption:** the method, system, dataset or benchmark is implemented in or shipped with a
  widely used third-party library, framework or tool whose documentation names it, or is a
  standard benchmark of a public leaderboard. Authors' own repositories and pages do not count.
- **M4 survey recognition (secondary only):** a later survey or review by different authors
  presents it as a key or representative method of a named category.

Excluded evidence: citation counts and citation-index pages (Google Scholar, Semantic Scholar,
OpenAlex, ResearchGate, Papers with Code citation lists), the paper itself, arXiv/DBLP listings,
and pages by the paper's authors.

## Procedure (frozen)

- **Searchers:** 6 fresh Claude subagents with web access, 20 papers each, in labeling-page order
  (strata are mixed by that page's seeded shuffle). Each receives only arXiv id, year and title,
  via one prompt file it is told to read once (`scripts/run_cs_value_markers.py prompt <batch>`).
  It is told not to use citation counts and not to read or modify any local file. Strata, labels
  and citation data are not given.
- **Output:** a JSON array; per paper, a list of claimed markers `{type, url, quote ≤ 40 words}`
  plus short notes. Replies are stored verbatim (`results/cs_forecast_v1/value_markers_raw.jsonl`),
  taken from each subagent transcript's hand-back.
- **Isolation audit:** tool calls are extracted from each transcript. A batch is discarded and
  re-run once with a fresh subagent if any tool input references the repository
  (`/home/user`), `labeling_key`, `cs_forecast` or `results/`, or if any Read targets a file other
  than its prompt file.
- **Mechanical verification** (`src/cs_forecast/evidence_verify.py`): the orchestrator fetches
  each URL (HTML → text; PDF via pdftotext) and a claim is **verified** only if (a) the
  normalised quote is a substring of the normalised page text, and (b) the page text contains
  the paper's arXiv id or a run of at least 5 consecutive words of its title (the whole title if
  shorter), and (c) the URL's host is not an excluded source. Otherwise it is `quote_not_found`,
  `paper_not_named`, `excluded_source` or `fetch_failed`, all counted as not verified. The
  orchestrator does not judge whether the evidence fits the marker definition; the searcher's
  claimed type is used. This is a stated limitation.

## Outcome

- **V (primary):** at least one verified M1–M3 marker. **V4 (secondary):** at least one verified
  M1–M4 marker. **K:** number of distinct verified marker types among M1–M3 (0–3).

## Analyses (frozen; bootstrap 10,000 resamples within strata, seed 20261017)

- **B1:** V rate in T (citation top-decile) vs R (random citation-negative): risk difference with
  bootstrap 95% CI, Fisher exact two-sided p.
- **B2:** V rate in M (Paper 3 model-favoured citation-negative) vs R, same statistics.
- **B3:** human 1–3 labels, GPT run-1 and Claude run-1 labels, compared between V=1 and V=0
  papers: Cliff's δ with bootstrap CI (descriptive; does each rater's score track the marker?).
- **B4:** B1 and B2 repeated with V4, and with K (Cliff's δ); per-marker-type counts by stratum;
  verification-status counts.

## Interpretation (frozen)

- B1 RD lower bound > 0 → the citation label agrees with the documentary value standard. RD upper
  bound < 0.10 → it does not. Otherwise inconclusive.
- B2 RD lower bound > 0 → the structure model finds documented value that citations miss
  (support for H1 as a value forecast despite G2). Otherwise no such evidence.
- The markers are themselves influenced by popularity (popular work gets libraries and Wikipedia
  pages), so agreement in B1 does not show that citations measure *intrinsic* value; it shows the
  two public signals coincide. Evidence-of-absence is weak: a paper with no verified marker may
  still be valuable, and search recall is imperfect and may be higher for famous papers.

## Budget and stop rule

No paid API. At most 6 searcher subagents plus one re-run per discarded batch. Pilot (2 papers
outside the sample: arXiv 1312.6114 and 1604.03410) was run before freezing to test feasibility
and the verifier; it is not part of the results.

Code sha256 at freeze: `scripts/run_cs_value_markers.py` `2a71c90d298fa514386e905a2d65690a60efcb83b672bbbccbaf4ea56aa58ff8`; `src/cs_forecast/evidence_verify.py` `48eefe6374bc6be853ce95270b0848b75cdea58bad8b94b8be703206fcf28f58`.
