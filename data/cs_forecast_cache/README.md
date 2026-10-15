# OpenAlex response cache archive

`openalex_cache_20261015.tar.gz` — 2,060 raw OpenAlex API responses (CC0) cached by
`scripts/fetch_openalex_frame.py` on 2026-10-15 between 00:02 and 00:19 UTC, before the
API key's daily budget was exhausted (~800/1,006 frame papers through the per-paper step;
references and context steps not started). Kept so the fetch can resume without
re-spending budget if the container is reclaimed.

SHA-256: e706744e5917ac5d1b6d6b351f8d64fe06c59bcc5f9069d55bba2b538ea34196

Restore: `tar -xzf data/cs_forecast_cache/openalex_cache_20261015.tar.gz -C data/cs_forecast`

The responses include per-year citation counts (outcome data). None of it has been analyzed;
the preregistered outcome is computed only by `scripts/run_cs_forecast.py`. No API key is
stored (the key is sent as a header and is not part of cached URLs).
