# Preregistration: literature-derived direction features beyond momentum (v2)

Frozen: 2026-10-18, **before any of the new feature counts are retrieved**. It extends
`research/preregistration_cs_direction_forecast_v1.md`, which found that five-year topic growth is
almost entirely predicted by momentum. The question here: do signals that the literature proposes
as drivers or early indicators of emerging topics add anything beyond momentum? If so, the
assistant's 2030 judgements could be grounded in a validated model rather than opinion.

## Literature basis for candidate features

- **Technology fusion with a general-purpose method:** the share of a topic's works carrying a
  machine-learning or deep-learning keyword. Motivated by keyword-burst and emergence indicators
  ([Guo, Weingart & Börner 2011, Scientometrics](https://link.springer.com/article/10.1007/s11192-011-0433-7);
  [Salatino et al., early detection of research trends](https://arxiv.org/pdf/1912.08928)).
- **Industry involvement:** the share of works with a company-affiliated author. Motivated by
  Ahmed, Wahed & Thompson 2023 (Science, "The growing influence of industry in AI research").
- **Preprint culture and speed:** the share of works with an arXiv location.
- **Geographic composition:** the share of works with authors in CN and in US. National research
  systems grow at different rates and favour different topics.
- **Venue type:** the conference share. In CS, conference-driven topics move faster.
- **Emergence-model attributes** (novelty, growth, coherence, impact;
  [Xu et al. 2017](https://arxiv.org/pdf/1707.03599)): growth and breadth were already tested in
  v1 as momentum, breadth and diffusion.
- **Not testable with this design:** newcomer entry (Guo et al.) needs author-level data, and
  concept-pair link prediction ([Gu & Krenn 2024](https://www.alphaxiv.org/abs/2402.08640)) works
  at a different unit. Both are listed as limitations.
- **Excluded on purpose:** citation features. OpenAlex `cited_by_count` is current, not
  point-in-time, so using it would be leakage.

## Data (frozen)

Same 302 CS topics and years 2000–2025 as v1. For each topic, primary-topic works per year with
each extra filter (`group_by=publication_year`):

| Code | Filter |
|---|---|
| `ml` | `keywords.id:machine-learning` |
| `dl` | `keywords.id:deep-learning` |
| `llm` | `keywords.id:large-language-models` (descriptive only: about 0 before 2020) |
| `company` | `authorships.institutions.type:company` |
| `arxiv` | `locations.source.id:S4306400194` |
| `cn` | `authorships.countries:CN` |
| `us` | `authorships.countries:US` |
| `conf` | `primary_location.source.type:conference` |

**Known biases:**
- Keywords are assigned by a present-day classifier from each work's own text. That uses no future
  outcome, but the classifier is modern.
- An arXiv location can be added after publication, for example when an old paper becomes popular.
  This is a small possible leak, and the arXiv result is flagged for it.
- The v1 hindsight topic list still applies.

## Candidate features (14, frozen)

For `k` in `ml, dl, company, arxiv, cn, us, conf`, two features are computed: `share_k = C_k,t / P_t`
and `d3share_k = share_k,t − share_k,t−3`.

## Stage 1: discovery (origins 2011–2015, targets 2016–2020)

- For each candidate, within each origin, regress both the feature and `G` on the momentum set
  (`g1, g3, g5, accel`) by OLS. Take the Spearman correlation of the two residuals (a partial
  correlation beyond momentum) and average over the five origins.
- Topic-cluster bootstrap with 2,000 replicates, seed 20261017.
- **Selection rule:** the 95% CI excludes 0, **and** the sign agrees in at least 4 of the 5
  origins. Bonferroni-adjusted intervals (14 tests) are reported next to it.
- If nothing is selected, stop. Report a null and skip stage 2.

## Stage 2: confirmation (held out; origins 2016–2019, targets 2021–2024; run once)

- **Models:**
  - `M0`: ridge regression (v1 specification) on momentum features.
  - `M1`: `M0` plus the selected features.
  - For reference: v1 `ridge_all` and `ridge_all` plus the selected features, and raw `g3`.
- Each model is trained on origins ≤ *t*−5, from 2006.
- **Metrics:** mean per-origin Spearman with `G`; pooled AUROC for top-decile `G`. Paired topic
  bootstrap, 2,000 replicates.
- **C1 (primary):** `M1 − M0` mean-Spearman difference has a lower bound > 0.
- **C2:** `M1 − M0` AUROC difference has a lower bound > 0.
- **C3:** each selected feature's partial correlation on the confirmation origins has a 95% CI
  excluding 0 in the discovery sign.

## Stage 3: registration

- **If C1 passes:** train `M1` on origins ≤ 2020 and register a 2025 → 2030 ranking
  (`prospective_2030_M1.csv` with sha256), evaluated on or after 2031-06-01 against the same
  target as v1. It is also compared against the registered v1 ranking.
- **If C1 fails:** register no new model. Write the 2025 feature table, including LLM share, as
  descriptive only, and state that the judgement list stays unvalidated.

## Budget

At most 3,000 OpenAlex requests (about 2,416 expected; free key, $1/day). No paid calls.

Code sha256 at freeze: `scripts/run_cs_direction_features_v2.py`
`b3aab110fd970d45ca577c2ce3c919bd916bdecd23959ed38a1ebb019b9987d0`.
