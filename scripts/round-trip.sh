set -eu
cd "$(dirname "$0")/.."
round_trip_folder=$(mktemp -d)
trap 'rm -rf "$round_trip_folder"' EXIT HUP INT TERM
git clone --no-local --quiet . "$round_trip_folder/source"
bun ts/scripts/round-trip.ts "$round_trip_folder/source" HEAD
