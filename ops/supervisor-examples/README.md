# Optional supervisor service examples

These files are templates only. Neither has been copied into a service manager,
loaded, enabled, or started. Replace `/PATH/TO/REPOSITORY` only after an
explicit user decision. The launchd example does not run at load and is not
kept alive; the systemd example is a one-shot unit with no timer/install target.
Both call the bounded supervisor, which itself requires explicit `--start`.

Prefer running `python3 scripts/research_supervisor.py --dry-run` first. No
background or paid worker is activated merely by installing these examples.
