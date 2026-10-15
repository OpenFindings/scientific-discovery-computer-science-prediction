# Research supervisor operations

The campaign has one canonical shared queue and two derived, isolated lane
checkpoints:

- `research/tracks/forecasting/{state,task_queue}.json` for Paper 3 work;
- `research/tracks/experiments/{state,task_queue}.json` for Paper 4 and executable experiments;
- `research/supervisor_state.json` for the supervisor lifecycle and quota state.

The shared `research/state.json` and `research/task_queue.json` remain the
source of truth. Workers never write those files; the supervisor merges a
declared artifact and updates both lane checkpoints.

## Safe local commands

```sh
PYTHONPATH=src /opt/homebrew/bin/python3.12 scripts/research_check.py
PYTHONPATH=src /opt/homebrew/bin/python3.12 scripts/research_status.py
PYTHONPATH=src /opt/homebrew/bin/python3.12 scripts/research_supervisor.py --dry-run
scripts/research_supervisor.py --start --max-rounds 1
scripts/research_stop.sh
scripts/research_resume.sh
```

`--start` is the explicit authorization boundary for a bounded worker run.
`--stop` persists `STOPPED_BY_USER`; launchd invocations then exit without
starting a worker. `--resume` clears that flag, and the next scheduled
activation performs a normal eligibility check.

## Quota behavior

The supervisor first parses structured CLI events for a rate-limit/usage-limit
code and only then uses a small bounded text fallback. Authentication,
network, and ordinary worker failures are kept separate and do not enter the
quota state. A quota failure persists `QUOTA_PAUSED` plus `next_check_at`,
preserves the task and artifact, and uses increasing sparse checks. There is
no undocumented reset API or hardcoded five-hour assumption; an official reset
timestamp is recorded only if the supported CLI result supplies one.

The local daily and per-track limits are conservative safety limits in
`research/state.json`. Their worker-time counter is an upper-bound estimate,
not a claim about the service's account quota.

## macOS launchd

Inspect the job before installing it:

```sh
PYTHONPATH=src /opt/homebrew/bin/python3.12 scripts/install_research_launchd.py --print
```

Install or remove the per-user LaunchAgent only when the user wants persistent
operation:

```sh
PYTHONPATH=src /opt/homebrew/bin/python3.12 scripts/install_research_launchd.py --install
PYTHONPATH=src /opt/homebrew/bin/python3.12 scripts/install_research_launchd.py --uninstall
```

The job runs one worker maximum per activation, waits at least five minutes
between checks, writes logs under `research/logs/`, and honors the persisted
STOP and quota states. It does not rotate credentials, change accounts, or
start a cloud service.

Codex Goals are a separate thread-scoped continuation mechanism. The local
supervisor complements that mechanism with repository-owned scientific state;
it cannot claim to observe or predict a reset that the CLI does not report.
