#!/usr/bin/env bash
# ccstatusline launcher — fast path, degrade-never.
# Wired from ~/.claude/settings.json -> statusLine.command
#
# Why a wrapper and not `npx ccstatusline`:
#  - nvm installs node/npx as lazy shims that die in the non-interactive shell
#    Claude Code spawns for the statusline (blank line bug). Resolve real bins.
#  - `npx` re-bootstraps the npm CLI on EVERY render (~800ms CPU). Hand the
#    globally installed dist straight to node: one process, no npm.
# Deliberately no `set -e`/`pipefail`: always print something.
set -u

NODE_BIN="node"; NPX_BIN="npx"
_nvm_bin="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1)"
if [ -n "$_nvm_bin" ] && [ -x "$_nvm_bin/node" ]; then
  NODE_BIN="$_nvm_bin/node"
  [ -x "$_nvm_bin/npx" ] && NPX_BIN="$_nvm_bin/npx"
  PATH="$_nvm_bin:$PATH"
fi

# V8 compile cache (Node >=22): ccstatusline is a large bundled ESM.
export NODE_COMPILE_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/ccstatusline-nodecache"

CCSTATUSLINE_VERSION="2.2.29"
CCS_JS=""
for _c in "$HOME"/.nvm/versions/node/*/lib/node_modules/ccstatusline/dist/ccstatusline.js \
          /opt/homebrew/lib/node_modules/ccstatusline/dist/ccstatusline.js \
          /usr/local/lib/node_modules/ccstatusline/dist/ccstatusline.js; do
  [ -f "$_c" ] && CCS_JS="$_c"
done

if [ -n "$CCS_JS" ]; then
  exec "$NODE_BIN" "$CCS_JS"
else
  # Fallback only — slow. Means the global install is missing:
  #   npm i -g ccstatusline@2.2.29
  exec "$NPX_BIN" -y "ccstatusline@${CCSTATUSLINE_VERSION}"
fi
