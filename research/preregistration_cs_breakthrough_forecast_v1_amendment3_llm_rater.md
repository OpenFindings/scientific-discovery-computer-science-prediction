# Amendment 3 to the CS breakthrough forecast preregistration (v1): LLM reference rater

Frozen: 2026-10-17, **before any LLM call**. G3 (amendment 2) is already run and its verdicts
(G3a inconclusive, G3c no evidence) are final. This amendment adds LLM ratings of the same 120
sampled papers as a **reference rater**. The LLM is not a second human, not an independent
validation of the citation label, and nothing here can change the G3 verdicts.

Script: `scripts/llm_rate_cs_papers.py` (calls) and `scripts/analyze_cs_llm_rater.py` (analysis).
`tests/test_cs_llm_rater.py` checks that the prompt in the script is byte-identical to the one
below.

## Inputs (blinding)

- Items: the 120 items embedded in `labeling/cs_breakthrough_labeling.html`, in that page's
  order. Each call gets one paper only: **title, publication year, abstract**, exactly as the
  human saw them (including the literal `(no abstract in OpenAlex)` placeholder).
- Not sent: arXiv id, URL, citation counts, any OpenAlex field, stratum, model score, human label.
  The script reads nothing from `results/cs_forecast_v1/labeling_key.json` or the human label
  file; only the analysis script joins them, after all calls finish.
- One paper per request, no conversation history, so ratings cannot anchor on each other.

## Raters and parameters

| Rater | Model | API | Sampling | Other |
|---|---|---|---|---|
| R1 (primary) | `claude-opus-5-5` | Anthropic Messages | Temperature is **not settable** on this model (the API rejects `temperature`/`top_p`); provider default sampling. Thinking is always on (adaptive); `output_config.effort = "low"`. | `max_tokens` 2000; no refusal fallback (a fallback would silently change the rater) |
| R2 (secondary) | `gpt-4.1` | OpenAI Chat Completions | `temperature = 0`, `seed = 20261017` | `max_tokens` 400; `response_format = json_object` |

Run order: R1 pass 1 on all 120 → R2 on all 120 → R1 pass 2 on all 120 (test–retest, since R1
cannot be made deterministic). If a named model is unavailable (404 / model not found), that
rater is **skipped, not substituted**; a substitute needs a new amendment before its calls.

## Prompt (frozen, verbatim)

System message:

```text
You are an expert computer-science reviewer acting as one rater in a research study. You will see one arXiv paper's title, publication year and abstract. Judge the paper's contribution as it would be seen about 3 years after its publication year, using the rubric below. You are not given citation counts; do not try to estimate them.

Rubric:
3 - Breakthrough: opened a new direction, or became a widely adopted method, benchmark, system or result within ~3 years.
2 - Significant: a solid contribution that others clearly built on, but not field-changing.
1 - Incremental: a modest or narrow contribution with little visible uptake.
0 - Can't judge: outside your expertise, or not enough information.

Also report whether you recognize this specific paper, meaning you know something about it beyond the text shown (for example its authors, venue, or later reception). Answer honestly; "false" is an acceptable and expected answer for most papers.

Reply with only a JSON object and no other text, in this form:
{"recognized": true or false, "recall": "if recognized, one sentence on what you know about this paper beyond the text shown; otherwise an empty string", "label": 0, 1, 2 or 3, "rationale": "one or two sentences"}
```

User message:

```text
Title: {title}
Publication year: {year}
Abstract: {abstract}
```

The rubric wording is the human page's rubric (`scripts/build_labeling_html.py`) with "–"
written as "-".

## Parsing and missing data

- The reply must parse as a JSON object (the first `{...}` span is extracted if there is
  surrounding text) with `label` ∈ {0,1,2,3} and boolean `recognized`. Otherwise one retry; if
  that also fails, or the reply is a refusal / empty, the item is **missing** for that rater and
  pass. Missing counts are reported per stratum.
- `recall` and `rationale` are stored for audit only and not scored. Recognition is the model's
  self-report and is not verified.

## Cost cap (hard)

- Total spend across all raters, passes, retries and failed calls ≤ **US$5.00**.
- Before every call the script requires `spent + worst_case_call ≤ 5.00`, where
  `worst_case_call = ceil(prompt_chars / 2) × input_price + max_tokens × output_price`; otherwise
  it stops and records `stopped_by_cost_cap`. After each call, `spent` increases by the actual
  billed usage (input + output tokens, thinking included in output) at the prices below.
- Prices used for the cap (US$ per 1M tokens, input / output):
  `claude-opus-5-5` 4.00 / 20.00 (Anthropic list price);
  `gpt-4.1` **5.00 / 20.00**, a deliberately high bound because the current OpenAI list price
  could not be verified offline, so the cap is conservative.
- Every call (including failures) is appended to `data/cs_forecast/llm_ratings_raw.jsonl` with
  model, pass, item id, usage, cost and the raw reply. The run is resumable and never re-calls a
  completed (rater, pass, item).

## Analyses (frozen)

Primary rater = R1 pass 1. Label 0 is excluded from ordinal statistics and counted. Bootstrap:
10,000 resamples, seed 20261017 (items resampled; within strata for stratum contrasts).

- **A1 – AI vs human agreement (main question).** Items rated 1–3 by both the human
  (`data/cs_forecast/human_labels_v1.json`) and R1: quadratic-weighted Cohen's κ with bootstrap
  95% CI, Spearman ρ, exact and within-one agreement, 3×3 confusion table, plus the cross-table
  of 0 labels. Reported for all overlapping items and **separately for R1-recognized and
  R1-unrecognized items**, with the bootstrap CI of the κ difference (recognized − unrecognized).
- **A2 – AI vs citation label.** Same statistics as amendment 2 G3a/G3c on R1 ratings of all
  120 items: Cliff's δ T vs R (**A2a**) and M vs R (**A2c**), Mann–Whitney p, share ≥2 and share
  =3 with Fisher p. Computed for (i) **unrecognized items (primary for A2)**, (ii) all items,
  (iii) recognized items.
- **A3 – recognition audit.** Share recognized by stratum (T/R/M), Fisher T vs R; mean R1 label
  recognized vs unrecognized; human–AI agreement on the human-labeled subset by recognition.
- **A4 – rater reliability.** Weighted κ R1 pass 1 vs pass 2 (test–retest) and R1 vs R2; R2
  repeats A1 and A2 as a secondary rater; recognition agreement R1 vs R2.

## Interpretation (frozen)

- κ bands (Landis–Koch, reported with CIs, not as tests): <0.20 slight, 0.20–0.40 fair,
  0.40–0.60 moderate, 0.60–0.80 substantial, >0.80 near-perfect.
- **A2a on unrecognized items:** δ lower bound > 0 → "text-only LLM judgement is associated with
  the citation label"; δ upper bound < 0.2 with lower bound ≤ 0 → "no more than a small
  association"; otherwise inconclusive. If unrecognized T or R has fewer than 10 rated items,
  A2(i) is descriptive only (no verdict).
- Any T-vs-R association **in recognized items** is read as possibly reflecting the model's
  memory of later fame, not as evidence of label validity.
- None of these outcomes changes G3a/G3c, and none is "independent validation": the LLM shares
  training data with the literature whose attention the label measures.

## Limitations stated in advance

- Self-reported recognition can be wrong in either direction; models may know a paper's
  reception without "recognizing" it, so the unrecognized subset still may carry hindsight.
- Recognition is likely correlated with stratum (famous papers are top-decile). The unrecognized
  T papers are then the less memorable top-decile ones, a selected subset; this biases A2(i)
  towards no difference.
- One prompt, one primary model, one pass for the main analysis; R1 sampling cannot be fixed.
- Human labels cover 84/120 items from one labeler, so A1 compares the LLM with one person.
