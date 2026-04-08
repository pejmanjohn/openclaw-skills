#!/bin/sh

set -u

FOLLOW_LOGS=0
FOLLOW_SECONDS=5

if ! command -v openclaw >/dev/null 2>&1; then
    echo "Missing required binary: openclaw" >&2
    exit 1
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --follow-logs)
            FOLLOW_LOGS=1
            ;;
        --follow-seconds)
            shift
            if [ "$#" -eq 0 ]; then
                echo "Missing value for --follow-seconds" >&2
                exit 2
            fi
            FOLLOW_SECONDS="$1"
            case "$FOLLOW_SECONDS" in
                ''|*[!0-9]*|0)
                    echo "Invalid value for --follow-seconds: $FOLLOW_SECONDS (must be a positive integer)" >&2
                    exit 2
                    ;;
            esac
            ;;
        -h|--help)
            echo "Usage: $0 [--follow-logs] [--follow-seconds N]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
    shift
done

print_section() {
    printf '\n== %s ==\n' "$1"
}

run_command() {
    printf '$ openclaw'
    for arg in "$@"; do
        printf ' %s' "$arg"
    done
    printf '\n'

    openclaw "$@"
    status=$?
    if [ "$status" -ne 0 ]; then
        printf '[exit %s]\n' "$status"
    fi
}

follow_logs() {
    printf '$ openclaw logs --follow (auto-stop after %ss)\n' "$FOLLOW_SECONDS"
    if command -v timeout >/dev/null 2>&1; then
        timeout "$FOLLOW_SECONDS" openclaw logs --follow
        status=$?
        if [ "$status" -ne 0 ] && [ "$status" -ne 124 ]; then
            printf '[exit %s]\n' "$status"
        fi
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$FOLLOW_SECONDS" <<'PY'
import os
import signal
import subprocess
import sys

seconds = int(sys.argv[1])
proc = subprocess.Popen(["openclaw", "logs", "--follow"], start_new_session=True)
try:
    sys.exit(proc.wait(timeout=seconds))
except subprocess.TimeoutExpired:
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    sys.exit(0)
PY
        status=$?
        if [ "$status" -ne 0 ]; then
            printf '[exit %s]\n' "$status"
        fi
        return
    fi

    printf 'Skipping log follow: requires timeout or python3 for bounded execution.\n'
}

print_section "OpenClaw diagnostics"
printf 'Read-only collection mode.\n'

print_section "Version"
run_command --version

print_section "Environment overrides"
found_override=0
for var_name in OPENCLAW_HOME OPENCLAW_STATE_DIR OPENCLAW_CONFIG_PATH OPENCLAW_LOG_LEVEL; do
    eval "var_value=\${$var_name-}"
    if [ -n "$var_value" ]; then
        printf '%s=%s\n' "$var_name" "$var_value"
        found_override=1
    fi
done
if [ "$found_override" -eq 0 ]; then
    printf 'No OpenClaw override variables set.\n'
fi

print_section "Diagnostic ladder"
run_command config file
run_command status
run_command status --all
run_command gateway probe
run_command gateway status
run_command doctor
run_command channels status --probe
run_command config validate
run_command update status

if [ "$FOLLOW_LOGS" -eq 1 ]; then
    print_section "Follow logs"
    follow_logs
fi
