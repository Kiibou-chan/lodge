set -eu
cd "$(dirname "$0")/.."
uv run ruff format --check
uv run ruff check
uv run mypy
uv run vulture
uv run pytest -q
uv run lodge check --gate
