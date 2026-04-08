#!/bin/sh

set -u

FOLLOW_LOGS=0
FOLLOW_SECONDS=5

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

if ! command -v openclaw >/dev/null 2>&1; then
    echo "Missing required binary: openclaw" >&2
    exit 1
fi

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

    openclaw logs --follow &
    pid=$!
    sleep "$FOLLOW_SECONDS"
    kill "$pid" >/dev/null 2>&1 || true
    wait "$pid" 2>/dev/null || true
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
