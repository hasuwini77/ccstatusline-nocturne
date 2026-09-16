#!/usr/bin/env bash
# Smoke test: the "no git" chip shows outside a repository and nowhere else.
# Renders every theme plus the standalone script in a throwaway repo and a
# throwaway plain directory. Needs node, python3, git and a global ccstatusline.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CCS=""
for _c in "$HOME"/.nvm/versions/node/*/lib/node_modules/ccstatusline/dist/ccstatusline.js \
          /opt/homebrew/lib/node_modules/ccstatusline/dist/ccstatusline.js \
          /usr/local/lib/node_modules/ccstatusline/dist/ccstatusline.js; do
  [ -f "$_c" ] && CCS="$_c"
done
[ -n "$CCS" ] || { echo "ccstatusline not installed globally"; exit 2; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/repo" "$TMP/plain"
git -C "$TMP/repo" init -q -b main
# a first commit, or `rev-parse --abbrev-ref HEAD` in noctu.py has nothing to name
git -C "$TMP/repo" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init

session() { printf '{"session_id":"t","transcript_path":"/dev/null","cwd":"%s","model":{"id":"claude-opus-5","display_name":"Opus 5"},"workspace":{"current_dir":"%s","project_dir":"%s"}}' "$1" "$1" "$1"; }
# strip colour, and ccstatusline's non-breaking spaces back to plain ones
plain() { sed $'s/\x1b\\[[0-9;]*m//g; s/\xc2\xa0/ /g'; }

fail=0
check() { # $1=label $2=output $3=dir kind
  if [ "$3" = plain ]; then
    grep -q 'no git' <<<"$2" || { echo "FAIL $1: no placeholder outside a repo"; fail=1; }
  else
    grep -q 'no git' <<<"$2" && { echo "FAIL $1: placeholder inside a repo"; fail=1; }
    grep -q 'main' <<<"$2" || { echo "FAIL $1: branch missing inside a repo"; fail=1; }
  fi
}

for theme in "$ROOT"/themes/*/; do
  name="$(basename "$theme")"
  for kind in repo plain; do
    out="$(session "$TMP/$kind" | (cd "$TMP/$kind" && node "$CCS" --config "$theme/settings.json") | plain)"
    check "$name/$kind" "$out" "$kind"
  done
done
for kind in repo plain; do
  out="$(session "$TMP/$kind" | python3 "$ROOT/standalone/noctu.py" | plain)"
  check "standalone/$kind" "$out" "$kind"
done

[ "$fail" = 0 ] && echo "ok: no-git chip correct in $(ls -d "$ROOT"/themes/*/ | wc -l | tr -d ' ') themes + standalone"
exit "$fail"
