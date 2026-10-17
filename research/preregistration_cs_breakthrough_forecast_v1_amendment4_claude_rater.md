# Amendment 4 to the CS breakthrough forecast preregistration (v1): Claude reference rater

Frozen: 2026-10-17, **before any rating**. Mirrors amendment 3 (GPT reference rater) with a Claude
model as a second reference rater on the same 120 papers. Same status: reference rater only, not
human judgement, not independent validation, hindsight-contaminated by training data.

## Rater (frozen)

- **Who rates:** fresh Claude subagents launched from this Claude Code session with the Agent
  tool. A subagent starts with no conversation context: it has not seen the human labels, strata,
  citation data, G3 or GPT results. The orchestrating session *has* seen them and therefore does
  not rate; it only passes the frozen prompt and parses the reply. The exact model identifier is
  not written into repository files (session policy); it is the session's configured Claude model
  and is reported to the project owner in chat.
- **No API key, no direct sampling control:** temperature and seed cannot be set. Stability is
  measured instead (A4).
- **Batching (differs from amendment 3):** the 120 items, in labeling-page order, are split into
  3 consecutive batches of 40; one subagent rates one batch in one reply. Items are identified only
  by their page position (1–120), never by arXiv id.
- **Runs:** 2 independent runs (6 subagents). Run 1 is primary; run 2 measures stability only.
- **Tool use:** to avoid hand-transcribing 40 abstracts, each batch's exact prompt is written by
  `scripts/run_cs_claude_rater.py prompt` to a file outside the repository, and the subagent is
  told to read exactly that one file with one Read call and use no other tool (no repository
  files, commands or web). Reported tool-use counts are recorded; a batch whose subagent made more
  than one tool call is discarded and reported.
- **Parsing:** the reply must be a JSON array of 40 objects
  `{item, rationale, label: 0|1|2|3, recognized: bool, first_author_surname: string|null}`.
  An unparseable batch is re-requested once from a fresh subagent; still failing → missing.
- Replies are stored verbatim in `results/cs_forecast_v1/claude_rater_raw.jsonl`.

## Input and prompt (frozen)

Input per item: publication year, title, abstract, byte-for-byte from the `ITEMS` array of
`labeling/cs_breakthrough_labeling.html` (as in amendment 3). The instruction text is amendment 3's
system prompt verbatim, followed by the batch wrapper below; `scripts/run_cs_claude_rater.py
prompt <run> <batch>` generates the exact text.

```
<amendment 3 system prompt, verbatim>

You are rating a batch of 40 papers. Rate each paper independently on its own merits.
Do not use any tools: do not read files, run commands or search the web. Use only the text below.
Reply with only a JSON array (no prose, no code fence) of 40 objects, one per item, in order:
{"item": <item number>, "rationale": "<at most 50 words>", "label": <0|1|2|3>,
 "recognized": <true|false>, "first_author_surname": "<surname>" or null}

=== Item <n> ===
Publication year: {year}
Title: {title}

Abstract:
{abstract}
```

## Analyses (frozen; bootstrap 10,000 resamples, seed 20261017)

A1–A4 exactly as amendment 3 (same functions, imported from `scripts/run_cs_llm_rater.py`) with
the Claude run-1 labels in place of GPT's, and recognition verified against the same OpenAlex
first-author file `results/cs_forecast_v1/llm_rater_openalex_authors.json`. Plus:

- **A5: Claude vs GPT.** Papers both models scored 1–3: quadratic-weighted κ (CI), Spearman (CI),
  exact and within-one agreement.

## Interpretation (frozen)

A1 and A2 rules as amendment 3. A5: κ CI lower bound > 0.4 → the two models agree at least
moderately. If A5 agrees while both A1 values are poor, the human–model gap is systematic (raters
judge differently), not single-model noise; it does not show which rater is right. Nothing here
changes G1–G4.

## Limitations stated in advance

Batched rating (40 per reply) can create within-batch anchoring, unlike amendment 3's one call per
paper. No temperature control. The model family's training data postdate all papers. The
orchestrator could in principle bias parsing; replies are stored verbatim to allow audit.

Script sha256 at freeze: `a9bc27ab3d5fde4e841e98b5ad0bb5418ac08985a779ac0676fbd6ca7f0f8c49`.

## Addendum (2026-10-17, after rating, before analysis)

Each subagent's reported tool-use count was **2**, not 1. Extracting only tool names and file
names from the six subagent transcripts showed the same two calls in every one: one `Read` of
its own assigned prompt file (`prompt_r<run>_b<batch>.txt`), then the `SubagentHandback` call
that returns the reply. No other file was read, no command was run and no web access was made.
The hand-back is how a subagent's reply is delivered, so the frozen ">1 tool call → discard"
rule did not anticipate it. Batches are ingested with the non-hand-back count (1). The JSON
ingested is the hand-back text taken from each transcript. It was compared to the orchestrator's
transcription and was identical for all six batches.
