#!/usr/bin/env bash
#
# Build a flat skill directory from the categorized arsenal, and install it.
#
#   ./bin/skills.sh check      validate every SKILL.md, find name collisions
#   ./bin/skills.sh build      regenerate dist/skills/ as a flat set of links
#   ./bin/skills.sh install    point ~/.claude/skills at dist/skills
#   ./bin/skills.sh status     what is in the repo, in dist, and installed
#
# Categories are for humans. Loaders want <name>/SKILL.md one level deep, so
# the categorized tree stays the source of truth and this generates the flat
# view from it. On Windows it uses directory junctions, which need no admin
# rights. On macOS and Linux it uses symlinks.
#
# Flags: --dry-run (print, change nothing), --target DIR (install elsewhere)

set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
DIST="$ROOT/dist/skills"
MANIFEST="$DIST/.manifest.tsv"
DEFAULT_TARGET="$HOME/.claude/skills"

DRY_RUN=false
TARGET="$DEFAULT_TARGET"
COMMAND="${1:-status}"
shift || true

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --target) TARGET="$2"; shift ;;
    *) echo "unknown flag: $1" >&2; exit 64 ;;
  esac
  shift
done

IS_WINDOWS=false
case "${OSTYPE:-}" in msys*|cygwin*|win32*) IS_WINDOWS=true ;; esac

say() { printf '%s\n' "$*"; }
run() { if $DRY_RUN; then say "  would: $*"; else "$@"; fi; }

# --- link abstraction -------------------------------------------------------

# On Windows every mklink costs a cmd.exe spawn, which turns a 130-skill build
# into minutes. Collect the commands and run cmd once instead.
BATCH_FILE=""

batch_begin() {
  $IS_WINDOWS || return 0
  $DRY_RUN && return 0
  BATCH_FILE="$(mktemp).bat"
  printf '@echo off\r\n' > "$BATCH_FILE"
}

batch_flush() {
  [ -n "$BATCH_FILE" ] || return 0
  [ -s "$BATCH_FILE" ] && cmd //c "$(cygpath -w "$BATCH_FILE")" >/dev/null
  rm -f "$BATCH_FILE"
  BATCH_FILE=""
}

# link_dir <link path> <source dir>
link_dir() {
  local link=$1 src=$2
  if $DRY_RUN; then say "  would link $(basename "$link") -> ${src#"$ROOT"/}"; return 0; fi
  if $IS_WINDOWS; then
    if [ -n "$BATCH_FILE" ]; then
      printf 'mklink /J "%s" "%s" >nul\r\n' \
        "$(cygpath -w "$link")" "$(cygpath -w "$src")" >> "$BATCH_FILE"
    else
      cmd //c mklink //J "$(cygpath -w "$link")" "$(cygpath -w "$src")" >/dev/null
    fi
  else
    ln -s "$src" "$link"
  fi
}

# Safe on a junction and on a symlink: neither follows into the source.
# Verified on Windows before this script was written.
unlink_dir() { rm -rf -- "$1"; }

# --- frontmatter ------------------------------------------------------------

# --- check ------------------------------------------------------------------

# One awk pass over every SKILL.md. Parsing them one file at a time costs a
# handful of process spawns each, which on Windows is most of the runtime.
# Emits: path <TAB> name <TAB> has-description <TAB> missing-frontmatter
scan_frontmatter() {
  find "$ROOT" -name SKILL.md -not -path "$ROOT/dist/*" -print0 \
    | xargs -0 awk '
        FNR == 1 {
          infm = 0; nm[FILENAME] = ""; ds[FILENAME] = 0; bad[FILENAME] = 0
          line = $0; sub(/\r$/, "", line)
          if (line == "---") infm = 1; else bad[FILENAME] = 1
          next
        }
        infm && /^---\r?$/ { infm = 0; next }
        infm && /^name:/ {
          v = $0; sub(/^name:[ \t]*/, "", v); sub(/\r$/, "", v)
          nm[FILENAME] = v; next
        }
        infm && /^description:/ {
          v = $0; sub(/^description:[ \t]*/, "", v); sub(/\r$/, "", v)
          if (v != "") ds[FILENAME] = 1
          next
        }
        END {
          for (f in nm) printf "%s\t%s\t%d\t%d\n", f, nm[f], ds[f], bad[f]
        }
      '
}

do_check() {
  local errors=0 count=0 table
  table=$(mktemp)
  scan_frontmatter | sort > "$table"

  local path name has_desc no_fm dir dirname_
  while IFS=$'\t' read -r path name has_desc no_fm; do
    [ -n "$path" ] || continue
    count=$((count + 1))
    dir=$(dirname "$path")
    dirname_=$(basename "$dir")

    if [ "$no_fm" = "1" ]; then
      say "ERROR no frontmatter: ${path#"$ROOT"/}"
      errors=$((errors + 1))
      continue
    fi

    if [ -z "$name" ]; then
      say "ERROR missing name: ${path#"$ROOT"/}"
      errors=$((errors + 1))
    elif [ "$name" != "$dirname_" ]; then
      say "ERROR name mismatch: ${path#"$ROOT"/} (name: $name, dir: $dirname_)"
      errors=$((errors + 1))
    fi

    if [ "$has_desc" != "1" ]; then
      say "ERROR missing or empty description: ${path#"$ROOT"/}"
      errors=$((errors + 1))
    fi

    case "$dirname_" in
      *[^a-z0-9-]*)
        say "ERROR name is not a lowercase slug: $dirname_"
        errors=$((errors + 1)) ;;
    esac
  done < "$table"

  # Collisions make a flat view impossible, so they are fatal.
  local dupes
  dupes=$(cut -f2 "$table" | sort | uniq -d)
  if [ -n "$dupes" ]; then
    while IFS= read -r d; do
      [ -n "$d" ] || continue
      say "ERROR duplicate skill name: $d"
      awk -F'\t' -v d="$d" '$2 == d { print "    " $1 }' "$table" | sed "s|$ROOT/||"
      errors=$((errors + 1))
    done <<< "$dupes"
  fi

  rm -f "$table"

  if [ "$errors" -gt 0 ]; then
    say ""
    say "check FAILED: $errors problem(s) across $count skills"
    return 1
  fi
  say "check ok: $count skills, no collisions"
}

# --- build ------------------------------------------------------------------

do_build() {
  do_check || return 1

  if [ -d "$DIST" ] && ! $DRY_RUN; then
    while IFS= read -r entry; do
      [ -n "$entry" ] && unlink_dir "$entry"
    done < <(find "$DIST" -mindepth 1 -maxdepth 1 2>/dev/null)
  fi
  run mkdir -p "$DIST"
  batch_begin

  local n=0
  $DRY_RUN || printf 'name\tcategory\tsource\n' > "$MANIFEST"

  while IFS= read -r skill_md; do
    local dir name category
    dir=$(dirname "$skill_md")
    name=$(basename "$dir")
    category=$(dirname "${dir#"$ROOT"/}")
    [ "$category" = "." ] && category="(root)"

    link_dir "$DIST/$name" "$dir"
    $DRY_RUN || printf '%s\t%s\t%s\n' "$name" "$category" "${dir#"$ROOT"/}" >> "$MANIFEST"
    n=$((n + 1))
  done < <(find "$ROOT" -name SKILL.md -not -path "$ROOT/dist/*" | sort)

  batch_flush
  say "built $n skills into ${DIST#"$ROOT"/}"
  $DRY_RUN || say "manifest: ${MANIFEST#"$ROOT"/}"

  if ! $DRY_RUN; then
    # -L follows the links. Without it find lists them and never descends.
    local visible
    visible=$(find -L "$DIST" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    say "verified: $visible SKILL.md readable at depth 1"
    [ "$visible" = "$n" ] || { say "ERROR expected $n, found $visible"; return 1; }
  fi
}

# --- install ----------------------------------------------------------------

do_install() {
  [ -d "$DIST" ] || { say "dist/skills missing. Run: ./bin/skills.sh build"; return 1; }

  if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
    if [ -L "$TARGET" ]; then
      say "replacing existing link at $TARGET"
      run unlink_dir "$TARGET"
    else
      local backup
      backup="$TARGET.backup-$(date +%Y%m%d-%H%M%S)"
      say "moving existing directory aside:"
      say "  $TARGET"
      say "  -> $backup"
      run mv "$TARGET" "$backup"
    fi
  fi

  run mkdir -p "$(dirname "$TARGET")"
  link_dir "$TARGET" "$DIST"

  if ! $DRY_RUN; then
    local visible
    visible=$(find -L "$TARGET" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    say "installed: $visible skills visible at $TARGET"
    [ "$visible" -gt 0 ] || { say "ERROR nothing readable through the link"; return 1; }
  fi
}

# --- status -----------------------------------------------------------------

do_status() {
  local repo dist_n
  repo=$(find "$ROOT" -name SKILL.md -not -path "$ROOT/dist/*" | wc -l | tr -d ' ')
  say "repo:      $repo skills (source of truth, categorized)"

  if [ -d "$DIST" ]; then
    dist_n=$(find -L "$DIST" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    say "dist:      $dist_n skills flat at ${DIST#"$ROOT"/}"
    [ "$dist_n" = "$repo" ] || say "           STALE. Run: ./bin/skills.sh build"
  else
    say "dist:      not built. Run: ./bin/skills.sh build"
  fi

  if [ -L "$DEFAULT_TARGET" ]; then
    local resolved installed
    resolved=$(readlink "$DEFAULT_TARGET" 2>/dev/null || echo "?")
    installed=$(find -L "$DEFAULT_TARGET" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    say "installed: $installed skills via link -> $resolved"
  elif [ -d "$DEFAULT_TARGET" ]; then
    local installed
    installed=$(find -L "$DEFAULT_TARGET" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    say "installed: $installed skills, as a REAL DIRECTORY (not linked to this repo)"
    say "           Run: ./bin/skills.sh install"
  else
    say "installed: nothing at $DEFAULT_TARGET"
  fi
}

case "$COMMAND" in
  check) do_check ;;
  build) do_build ;;
  install) do_install ;;
  status) do_status ;;
  *) say "usage: $0 {check|build|install|status} [--dry-run] [--target DIR]"; exit 64 ;;
esac
