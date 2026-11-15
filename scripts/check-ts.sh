set -eu
cd "$(dirname "$0")/../ts"
command -v bun >/dev/null 2>&1 || { echo "bun is not installed" >&2; exit 2; }
[ -d node_modules ] || { echo "ts/node_modules is missing; run bun install --frozen-lockfile in ts/" >&2; exit 2; }
bun --bun run check
