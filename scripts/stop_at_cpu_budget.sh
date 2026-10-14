#!/usr/bin/env bash
# Run one workload in a dedicated cgroup and terminate it at an observed CPU budget.
# Requires /run to be a writable per-arm bind mount and cgroup-v2 cpu.stat.
set -u

budget_usec="$1"
shift
if [[ ! "$budget_usec" =~ ^[1-9][0-9]*$ ]]; then
  echo "budget_usec must be a positive integer" >&2
  exit 64
fi

read_cpu() {
  awk '$1 == "usage_usec" { print $2; found=1; exit } END { if (!found) exit 1 }' /sys/fs/cgroup/cpu.stat
}

start_cpu="$(read_cpu)" || exit 65
"$@" &
child_pid=$!
stop_reason="natural_exit"
target_cpu=$((start_cpu + budget_usec))

while kill -0 "$child_pid" 2>/dev/null; do
  current_cpu="$(read_cpu)" || exit 65
  if (( current_cpu >= target_cpu )); then
    stop_reason="cpu_budget"
    kill -TERM "$child_pid" 2>/dev/null || true
    for _ in 1 2 3 4 5; do
      kill -0 "$child_pid" 2>/dev/null || break
      sleep 0.02
    done
    if kill -0 "$child_pid" 2>/dev/null; then
      kill -KILL "$child_pid" 2>/dev/null || true
    fi
    break
  fi
  sleep 0.02
done

wait "$child_pid"
child_status=$?
end_cpu="$(read_cpu)" || exit 65
cat /sys/fs/cgroup/cpu.stat > /run/cpu.stat
printf 'start_cpu_usec=%s\nend_cpu_usec=%s\nused_cpu_usec=%s\nbudget_usec=%s\nstop_reason=%s\nchild_status=%s\n' \
  "$start_cpu" "$end_cpu" "$((end_cpu - start_cpu))" "$budget_usec" "$stop_reason" "$child_status" > /run/stop_receipt.txt
if [[ "$stop_reason" == "cpu_budget" ]]; then
  exit 0
fi
exit "$child_status"
