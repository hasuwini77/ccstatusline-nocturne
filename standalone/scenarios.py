#!/usr/bin/env python3
"""Render noctu.py the way the statuslin.es sandbox does, and check the result.

Mirrors the gallery's eight example sessions (src/render/scenarios.ts in
NathanAB/statuslin.es): same stdin JSON, a seeded git repo in the working
directory (none for the non-git one), COLUMNS/LINES only, no locale.

    python3 standalone/scenarios.py          # check all eight, print renders
    python3 standalone/scenarios.py --quiet  # checks only
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, 'noctu.py')
ANSI = re.compile(r'\x1b\[[0-9;]*m')

OPUS = {'id': 'claude-opus-4-8', 'display_name': 'Opus 4.8'}
SONNET = {'id': 'claude-sonnet-4-6', 'display_name': 'Sonnet 4.6'}
HAIKU = {'id': 'claude-haiku-4-5', 'display_name': 'Haiku 4.5'}
FABLE = {'id': 'claude-fable-5', 'display_name': 'Fable 5'}
COST = {'total_cost_usd': 0.41, 'total_duration_ms': 612000, 'total_api_duration_ms': 48000,
        'total_lines_added': 128, 'total_lines_removed': 34}


def usage(pct, size=200000):
    return {'context_window_size': size, 'used_percentage': pct, 'remaining_percentage': 100 - pct}


def empty_usage(size=200000):
    return {'context_window_size': size, 'used_percentage': None, 'remaining_percentage': None}


def win(pct, h, m):
    return {'used_percentage': pct, 'resets_at': int(time.time()) + h * 3600 + m * 60}


# (key, stdin, git branch or None, strings the plain render must contain, must not contain)
SCENARIOS = [
    ('clean-main', dict(model=OPUS, effort={'level': 'high'}, cost=COST, context_window=usage(22),
        rate_limits={'five_hour': win(26, 2, 7), 'seven_day': win(7, 49, 0)}),
     'main', ['Opus 4.8', 'main', '22%', 'week', '7%', 'high', '$0.41', '+128/-34'], ['no git']),
    ('fresh-session', dict(model=OPUS, effort={'level': 'high'}, context_window=empty_usage(),
        cost=dict(COST, total_cost_usd=0, total_lines_added=0, total_lines_removed=0)),
     'main', ['ctx  —', 'week —', '$0.00'], ['+0/-0', 'None']),
    ('dirty-feature', dict(model=SONNET, effort={'level': 'medium'}, cost=COST, context_window=usage(48),
        rate_limits={'five_hour': win(40, 1, 12), 'seven_day': win(18, 70, 0)}),
     'feat/auth', ['feat/auth', '48%', '18%', 'medium'], []),
    ('near-full', dict(model=OPUS, effort={'level': 'max'}, cost=dict(COST, total_cost_usd=4.12),
        context_window=usage(91), output_style={'name': 'Explanatory'},
        rate_limits={'five_hour': win(88, 0, 18), 'seven_day': win(61, 20, 0)}),
     'main', ['91%', '61%', 'max', '$4.12', 'Explanatory'], []),
    ('big-context', dict(model=FABLE, effort={'level': 'xhigh'}, cost=COST,
        context_window=usage(64, 1000000),
        rate_limits={'five_hour': win(33, 3, 30), 'seven_day': win(80, 120, 0)}),
     'main', ['Fable 5', '64%', '80%', 'xhigh'], ['100%']),
    ('post-compact', dict(model=HAIKU, cost=COST, context_window=empty_usage(),
        rate_limits={'five_hour': win(52, 4, 2)}),
     'main', ['ctx  —', '5h', '52%'], ['week']),
    ('worktree', dict(model=OPUS, effort={'level': 'low'}, cost=COST, context_window=usage(37),
        rate_limits={'five_hour': win(44, 2, 50), 'seven_day': win(20, 31, 0)}),
     'worktree-feature', ['worktree-feature', '37%', '20%', 'low'], []),
    ('non-git', dict(model=OPUS, effort={'level': 'high'}, cost=COST, context_window=usage(22)),
     None, ['no git', '22%'], []),
]


def run(stdin, branch):
    with tempfile.TemporaryDirectory() as d:
        if branch:
            for cmd in (['init', '-q'], ['checkout', '-q', '-b', branch],
                        ['-c', 'user.email=a@b.c', '-c', 'user.name=a', 'commit', '-q',
                         '--allow-empty', '-m', 'seed']):
                subprocess.run(['git'] + cmd, cwd=d, check=True, capture_output=True)
        payload = dict(session_id='t', transcript_path='/nonexistent/transcript.jsonl', cwd=d,
                       version='2.1.155', output_style={'name': 'default'})
        payload.update(stdin)
        payload['workspace'] = {'current_dir': d, 'project_dir': d}
        env = {'PATH': os.environ.get('PATH', ''), 'COLUMNS': '120', 'LINES': '40'}
        return subprocess.run([sys.executable, SCRIPT], input=json.dumps(payload).encode(),
                              cwd=d, env=env, capture_output=True, timeout=5)


def main():
    quiet = '--quiet' in sys.argv
    failures = []
    source = open(SCRIPT, 'rb').read()
    if not source.isascii():
        failures.append('source: not ASCII-only (pastes through a non-UTF-8 clipboard garble it)')
    for key, stdin, branch, want, avoid in SCENARIOS:
        res = run(stdin, branch)
        out = res.stdout.decode('utf-8', errors='replace')
        plain = ANSI.sub('', out)
        if not quiet:
            print('--', key)
            print(out)
        if res.returncode != 0 or res.stderr:
            failures.append('%s: exit %d %s' % (key, res.returncode, res.stderr.decode()[-200:]))
        for s in want:
            if s not in plain:
                failures.append('%s: missing %r' % (key, s))
        for s in avoid:
            if s in plain:
                failures.append('%s: unexpected %r' % (key, s))
        rows = plain.split('\n')
        dividers = [[m.start() for m in re.finditer('▏', r)] for r in rows]
        shared = min(len(x) for x in dividers)
        if any(x[:shared] != dividers[0][:shared] for x in dividers):
            failures.append('%s: columns not aligned %s' % (key, dividers))
    for f in failures:
        print('FAIL', f)
    if not failures:
        print('ok: %d statuslin.es scenarios' % len(SCENARIOS))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
