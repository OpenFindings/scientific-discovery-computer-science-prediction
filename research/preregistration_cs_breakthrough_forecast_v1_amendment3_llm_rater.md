# Amendment 3 to the CS breakthrough forecast preregistration (v1): LLM reference rater

Frozen: 2026-10-17, **before any model call**. G3 (amendment 2) is complete and unchanged; this
adds one LLM as a *reference rater* on the same 120 papers. Its scores are not human judgement
and not independent validation: the model was trained on text written after these papers
appeared and may remember how famous they became. The research question is narrow: does the
LLM agree with the human labeler, and does the LLM separate the citation strata when the human
did not?

## Rater (frozen)

- Provider/model: OpenAI Chat Completions, pinned snapshot `gpt-4.1-2025-04-14`.
  Reason: it accepts an explicit temperature (the GPT-5/o-series reasoning models accept only
  the default temperature), and it supports strict JSON-schema output. `ANTHROPIC_API_KEY` is not
  present in this container's environment, so no Anthropic model is used.
- `temperature=0`, `max_tokens=300`, `seed=20261017`, strict JSON schema
  `{rationale: string (≤50 words), label: 0|1|2|3, recognized: bool, first_author_surname: string|null}`.
  The schema order puts the rationale before the label and the recognition fields after it.
- One request per paper, no conversation history, papers in the labeling page's order.
- **3 runs** over all 120 papers. Run 1 is primary for every analysis; runs 2–3 only measure
  test-retest stability (A4). Failed calls are retried at most twice; a paper still missing after
  that is reported as missing, not imputed.
- Code: `scripts/run_cs_llm_rater.py` (sha256 at freeze
  `78aa35d3479491652abfa52418776ac27990c8378a1304a692577734fa5b946c`). Raw responses, token usage
  and `system_fingerprint` are appended to `results/cs_forecast_v1/llm_rater_raw.jsonl`.

## Input (frozen)

Only publication year, title and abstract, taken byte-for-byte from the `ITEMS` array in
`labeling/cs_breakthrough_labeling.html` (sha256 `63b05c11…7fa31`) — what the human saw, minus
the arXiv id and link. No citation counts, no strata, no arXiv id, no author names. 11 items have
the placeholder abstract "(no abstract in OpenAlex)", as on the human page.

### System prompt (verbatim)

```
You are an expert computer-science reviewer helping assess the contribution of research papers. Judge each paper's contribution as it would be seen about 3 years after its publication year, using this rubric:

3 - Breakthrough: opened a new direction, or became a widely adopted method, benchmark, system or result within ~3 years.
2 - Significant: a solid contribution that others clearly built on, but not field-changing.
1 - Incremental: a modest or narrow contribution with little visible uptake.
0 - Can't judge: outside your expertise, or not enough information.

You will see only the title, publication year and abstract. Do not try to recall or estimate citation counts; judge the contribution itself. Separately, say honestly whether you recognise this specific paper (that is, you remember it existing, not merely its topic). If you recognise it, give the first author's surname; otherwise give null. Do not guess an author if you do not recognise the paper.
```

### User message template

```
Publication year: {year}
Title: {title}

Abstract:
{abstract}
```

The rubric text matches the human page's rubric.

## Budget (frozen)

Hard cap **USD 5.00**. Before each call the script adds the worst-case cost of that call
(input estimated at 1 token per 3 characters, plus the full `max_tokens` output) to the running
spend and stops with exit code 2 if the total would exceed $5. Spend is computed from the API's
returned token usage at gpt-4.1 list price ($2.00 / 1M input, $8.00 / 1M output) multiplied by a
1.25 safety margin. Expected spend ≈ $1 (360 calls × ~800 input + ~120 output tokens). If the cap
stops the run, the analysis runs on what was rated and the shortfall is reported.

## Recognition

- **Self-reported:** the `recognized` field.
- **Verified (secondary):** after rating, first-author display names are fetched from OpenAlex
  (free; the `feature_work` id in the frozen snapshot). A recognition is verified when the
  model's surname equals the OpenAlex first author's last name token after ASCII/lower-case
  normalisation. Self-reported recognition is the primary split; verification shows how far the
  self-report can be trusted.

## Analyses (frozen; bootstrap 10,000 resamples of papers, seed 20261017)

Labels 0 are excluded from all tests and counted (the cross-tab includes them).

- **A1 (primary): LLM vs human.** Papers both raters scored 1–3. Quadratic-weighted Cohen's κ
  with bootstrap 95% CI; Spearman ρ with CI; exact agreement; within-one agreement; mean LLM −
  human. Repeated within the self-reported recognised and unrecognised subsets (descriptive).
- **A2: LLM vs citation label.** Same statistics as G3a/G3c applied to the LLM's run-1 labels on
  all rated papers: T vs R and M vs R Cliff's δ (CI), Mann–Whitney p, Fisher on ≥2 and =3.
  Repeated within recognised / unrecognised subsets, within the human-labeled subset (to compare
  like with like against G3), and excluding verified-recognition papers.
- **A3: recognition.** Recognition rate per stratum (self-reported and verified), Fisher T vs R
  and T vs M; LLM score of recognised vs unrecognised papers (Cliff's δ).
- **A4: stability.** Run-1 vs run-2 and run-3 exact label agreement and recognition agreement.

## Interpretation (frozen)

- A1: κ CI lower bound > 0.4 → moderate-or-better agreement with the human; κ CI upper bound
  < 0.2 → poor agreement; otherwise inconclusive. Agreement does not make either rater correct.
- A2: T-vs-R δ CI lower bound > 0 → the LLM's ratings track the citation label. If that holds
  overall but the unrecognised-subset δ CI includes 0, and recognition is more common in T than
  in R, the pattern is consistent with the model remembering later fame (hindsight leakage), not
  with judging the abstract. A positive δ in the unrecognised subset is weaker leakage evidence,
  not none: the model still knows how the field developed after each paper.
- Disagreement between A2 and G3a (LLM separates T from R, the human does not) is reported as
  such; it does not override G3, and it is not evidence that the citation label measures value.
- No outcome here changes G1/G2/G3/G4 verdicts or counts as independent validation.

## Limitations stated in advance

One model, one prompt, no prompt tuning. Recognition self-report may be unreliable in both
directions. The model's knowledge postdates every paper's 3-year window, so its ratings are
hindsight-contaminated even when it reports not recognising a paper. 84 human labels, 82 on the
1–3 scale, limit A1 power.
