#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SKILLS_DIR="$REPO_ROOT/skills"
DEST_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

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

mkdir -p "$DEST_DIR"

installed=0
for skill_src in "$SKILLS_DIR"/*/; do
    [ -d "$skill_src" ] || continue
    skill_name=$(basename "$skill_src")
    target="$DEST_DIR/$skill_name"

    skill_src_clean="${skill_src%/}"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_src_clean" ]; then
        echo "Already installed: $skill_name"
        installed=$((installed + 1))
        continue
    fi

    if [ -e "$target" ] || [ -L "$target" ]; then
        echo "Skipping $skill_name: $target already exists (not our symlink)" >&2
        continue
    fi

    ln -s "$skill_src_clean" "$target"
    echo "Installed $skill_name at $target"
    installed=$((installed + 1))
done

echo "Done. $installed skill(s) installed for Codex."
echo "Restart Codex to pick up new skills."
