#!/bin/sh

set -eu

SKILL_NAME="openclaw-troubleshooting"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SKILL_SRC="$REPO_ROOT/skills/$SKILL_NAME"
DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

usage() {
    echo "Usage: $0 [--dest DIR]"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --dest)
            shift
            if [ "$#" -eq 0 ]; then
                echo "Missing value for --dest" >&2
                exit 2
            fi
            DEST_DIR="$1"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

TARGET="$DEST_DIR/$SKILL_NAME"

mkdir -p "$DEST_DIR"

if [ -L "$TARGET" ] && [ "$(readlink "$TARGET")" = "$SKILL_SRC" ]; then
    echo "Claude Code skill already installed at $TARGET"
    exit 0
fi

if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
    echo "Refusing to overwrite existing path: $TARGET" >&2
    exit 1
fi

ln -s "$SKILL_SRC" "$TARGET"

echo "Installed $SKILL_NAME for Claude Code at $TARGET"
