#!/usr/bin/env python3
"""Build standalone/noctu.py from standalone/noctu-fable.py.

The Fable file is the source. Lines between `# fable:begin` and `# fable:end`
exist only in it; lines between `# plain:begin` and `# plain:end` only in the
plain build. The plain build must never touch the network or a credential, so
it carries no Network Access / Reads Token badge on statuslin.es.

    python3 scripts/make_standalone.py          # write noctu.py
    python3 scripts/make_standalone.py --check  # fail if noctu.py is stale
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'standalone', 'noctu-fable.py')
TARGET = os.path.join(ROOT, 'standalone', 'noctu.py')
MARK = re.compile(r'^\s*# (fable|plain):(begin|end)\s*$')
# what statuslin.es badges as a token read or a network call
FORBIDDEN = re.compile(r'Claude Code-credentials|claudeAiOauth|CLAUDE_CODE_OAUTH_TOKEN|\.credentials|'
                       r'urllib|http\.client|socket|api\.anthropic\.com', re.I)


def build(text, keep):
    out, inside = [], None
    for line in text.splitlines(keepends=True):
        m = MARK.match(line)
        if m:
            kind, edge = m.groups()
            if (edge == 'begin') == (inside is not None):
                raise SystemExit('unbalanced marker: ' + line.strip())
            inside = kind if edge == 'begin' else None
            continue
        if inside is None or inside == keep:
            out.append(line)
    if inside:
        raise SystemExit('unclosed # %s:begin' % inside)
    return ''.join(out)


def main():
    source = open(SOURCE, encoding='ascii').read()
    plain = build(source, 'plain')
    leaks = sorted(set(m.group(0) for m in FORBIDDEN.finditer(plain)))
    if leaks:
        raise SystemExit('plain build leaks network/credential code: %s' % ', '.join(leaks))
    if '--check' in sys.argv:
        if open(TARGET, encoding='ascii').read() != plain:
            raise SystemExit('standalone/noctu.py is stale: run python3 scripts/make_standalone.py')
        print('ok: noctu.py matches noctu-fable.py minus the Fable blocks')
        return
    open(TARGET, 'w', encoding='ascii').write(plain)
    print('built standalone/noctu.py')


if __name__ == '__main__':
    main()
