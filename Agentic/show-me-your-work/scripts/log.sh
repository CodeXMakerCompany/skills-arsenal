#!/usr/bin/env bash
# Append one decision row to a TSV trail.
# Usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>
set -euo pipefail

if [ "$#" -ne 6 ]; then
  echo "usage: $0 <logfile> <phase> <decision> <why> <evidence> <result>" >&2
  exit 64
fi

logfile=$1
shift

sanitize() {
  local cell
  cell=$(printf '%s' "$1" | tr '\t\n\r' '   ')
  case $cell in
    [=+@-]*) printf "'%s" "$cell" ;;
    *) printf '%s' "$cell" ;;
  esac
}

if [ ! -s "$logfile" ]; then
  printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' > "$logfile"
fi

row=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for cell in "$@"; do
  row="$row	$(sanitize "$cell")"
done
printf '%s\n' "$row" >> "$logfile"
