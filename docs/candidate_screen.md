# Year- and subfield-stratified candidate screen

Generated 2026-10-11 from the complete local arXiv-CS metadata harvest. The
screen is a reproducible retrieval queue for full-text review, not an evidence
review, forecast, or ranking of scientific value.

## Method

`scripts/screen_research_candidates.py` scanned all 937,531 corpus records and
applied 18 declared computer-science subfield definitions. A record first had
to carry at least one declared arXiv category for that subfield and match at
least one subject phrase in its title or abstract. Topics can overlap. A
transparent lexical priority score then added points for explicit open-gap,
limitation/future-work, contradictory/uncertain, empirical-comparison, and
falsifiable-outcome language. No citation counts, popularity measures, or
model-generated judgments were used. Up to eight records per exact submission
year × subfield cell were retained; 2026 is only observed through October 11.

The full overlapping hit counts are in
`data/research_candidate_screen_profile.json`. Candidate rows, including
versioned arXiv ID, title, abstract, dates,
categories, DOI/journal reference when available, score cues, and abstract/PDF
links, are in `data/research_candidate_screen.jsonl`.

## Coverage

The 229,190 topic hits are overlapping: one paper may match multiple subjects.
They reduce to 2,106 unique arXiv IDs in the balanced review queue (2,178
paper-topic rows). The table shows lexical-hit totals across four time strata
and retained paper-topic rows. The last stratum contains two years and is
right-censored in 2026.

| Subfield | 2010–14 hits | 2015–19 hits | 2020–24 hits | 2025–26 hits | Retained rows |
|---|---:|---:|---:|---:|---:|
| Foundation models | 1 | 60 | 27,012 | 62,176 | 70 |
| Reasoning and agents | 35 | 89 | 2,244 | 9,760 | 120 |
| Agent reliability/security | 17 | 55 | 373 | 2,283 | 107 |
| Agent memory/coordination | 66 | 206 | 1,304 | 4,193 | 133 |
| Continual/multimodal learning | 3 | 342 | 4,103 | 4,754 | 96 |
| Model efficiency | 5 | 249 | 2,009 | 2,478 | 98 |
| Software testing | 214 | 586 | 2,041 | 1,934 | 136 |
| Program repair/verification | 97 | 297 | 696 | 564 | 136 |
| AI-generated code | 38 | 77 | 1,310 | 2,735 | 125 |
| Software supply-chain security | 3 | 10 | 82 | 122 | 69 |
| Distributed/cloud systems | 746 | 1,868 | 3,495 | 1,593 | 136 |
| Databases | 657 | 1,002 | 1,673 | 1,253 | 136 |
| Compilers/programming languages | 471 | 1,081 | 2,505 | 1,812 | 136 |
| Energy-efficient computing | 139 | 370 | 1,069 | 672 | 136 |
| Security/privacy | 361 | 1,355 | 4,865 | 2,564 | 136 |
| Robotics/embodied AI | 509 | 3,860 | 15,524 | 12,875 | 136 |
| Algorithms/complexity | 4,084 | 7,113 | 9,525 | 4,530 | 136 |
| Optimization/causal/scientific discovery | 164 | 814 | 3,492 | 2,526 | 136 |

The annual counts, including the arXiv corpus denominator, are available in
`data/arxiv_cs_profile.json` and `data/research_candidate_screen_profile.json`.
The first candidate file has per-year topic caps, so larger recent publication
volumes do not automatically dominate the manual-review queue. **That cap was
only a manual-review convenience and was too restrictive to serve as the main
research pool.**

## Uncapped index (replacement for broad discovery)

After review, the 8-paper-per-year/topic cap has been removed from the broad
discovery path. `scripts/index_uncapped_candidates.py` scans the same 937,531
arXiv-CS metadata/abstract records and writes every match from the 18 declared
topic definitions, with a paper stored once and all matching topics attached.
It yielded **198,690 distinct papers** and 229,190 paper-topic assignments,
without a per-cell cap. The compressed index is
`data/research_candidates_uncapped.jsonl.gz`; its counts and exact rules are in
`data/research_candidates_uncapped_profile.json`.

| Year | Uncapped distinct matches |
|---|---:|
| 2010–2014 | 7,369 |
| 2015–2019 | 18,863 |
| 2020–2024 | 75,709 |
| 2025–2026 (to Oct. 11) | 96,749 |
| **Total** | **198,690** |

This broadens the candidate pool by about 94× versus the 2,106-unique-paper
capped queue. It is still a lexical index, not 198,690 full-text analyses:
the harvest contains arXiv metadata and abstracts, and the 18-topic phrases
can both miss papers and return irrelevant ones. Full-text review must now draw
from this uncapped pool using year/topic strata, with no hidden top-8 limit;
venue databases and citation-linked searches should supplement arXiv.

## Full-text review protocol

This pass has **not** established that a paper's question is still unresolved.
Before extraction, each selected paper must be checked against its exact
version and, where possible, published venue version. Reviewers will record:

1. exact research question/hypotheses and section/page or paragraph locator;
2. dataset, comparison, measurement, and the paper's actual result;
3. author-stated limitations/open questions separately from reviewer inference;
4. independent supporting and contradictory studies, with dates and exact
   claim locators;
5. whether the proposed question is falsifiable and what experiment could
   distinguish competing explanations;
6. version/venue/duplicate status and full-text availability.

Abstract keywords can overretrieve (for example, a general mention of LLMs in
a domain paper), and category boundaries can underretrieve. Consequently,
the lexical score is used only to order a stratified queue. A first purposive
full-text sample has been audited and recorded in `docs/fulltext_audit.md` and
`data/audited_research_questions.jsonl`; it is not yet balanced or
representative. Continue review by subfield and historical cutoff, and search
for independent evidence before labeling a question unresolved. Do not report
these counts as topic prevalence, unresolved-problem counts, or
research-opportunity scores.
