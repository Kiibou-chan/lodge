set -eu
cd "$(dirname "$0")/.."
mkdir -p .drafts
reference=$(mktemp "$PWD/.drafts/differential-XXXXXX.json")
trap 'rm -f "$reference"' EXIT HUP INT TERM
uv run --frozen --quiet python scripts/differential_dump.py "$PWD" > "$reference"
bun ts/scripts/differential.ts "$PWD" "$reference"
