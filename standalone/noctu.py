#!/usr/bin/env python3
"""Noctu — a two-row status line for Claude Code, no dependencies, no network.

Reads Claude Code's session JSON on stdin, prints two rows:

    ◆ Opus 5  ▏ ctx  ▓▓▓▓░░░░░░ 38% ▏ $0.42 ▏ 14m
     master   ▏ diff +128/-34   ▏ 2.1k lines

The design rule: the bar recedes, the number speaks. Meters are a muted bar
plus a bright value, and only the model and the branch get filled badges,
because only those two are identity. The columns are aligned by measuring
each row rather than padding to a guess, so they hold with any branch name.
"""
import json
import os
import subprocess
import sys

# palette (hex -> truecolor SGR)
VIOLET, VIOLET_DK = '7C5CFF', '5B3FD1'
TEAL, TEAL_DK = '2E9E7A', '1E6B52'
YELLOW, YELLOW_BAR = 'F0C755', '6B5A28'
GREEN, BLUE, DIM, INK, WHITE = '7CE38B', '5B9BE8', '79808E', '0B0E14', 'FFFFFF'
BAR_FULL, BAR_EMPTY, ARROW, DIVIDER, BRANCH_ICON, DIAMOND = '▓', '░', '', '▏', '', '◆'
BAR_WIDTH = 10


def fg(h):
    return '\x1b[38;2;%d;%d;%dm' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def bg(h):
    return '\x1b[48;2;%d;%d;%dm' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


RESET = '\x1b[0m'


def chip(icon, label, body, icon_bg):
    """icon compartment + label + arrow cap — the badge that anchors each row"""
    return (bg(icon_bg) + fg(WHITE) + ' ' + icon + ' ' + RESET +
            bg(body) + fg(INK) + '\x1b[1m ' + label + ' ' + RESET +
            fg(body) + ARROW + RESET)


def meter(pct, bar_colour, value_colour, label):
    filled = round(max(0.0, min(100.0, pct)) / 100 * BAR_WIDTH)
    bar = fg(bar_colour) + BAR_FULL * filled + BAR_EMPTY * (BAR_WIDTH - filled) + RESET
    return (fg(value_colour) + label + RESET + ' ' + bar + ' ' +
            fg(value_colour) + '%d%%' % round(pct) + RESET)


def context_percent(transcript, window):
    """Token usage of the most recent assistant turn, as a share of the window."""
    if not transcript or not os.path.exists(transcript):
        return None
    used = None
    try:
        with open(transcript, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    msg = json.loads(line).get('message') or {}
                except ValueError:
                    continue
                u = msg.get('usage')
                if isinstance(u, dict):
                    used = (u.get('input_tokens', 0) + u.get('output_tokens', 0) +
                            u.get('cache_read_input_tokens', 0) +
                            u.get('cache_creation_input_tokens', 0))
    except OSError:
        return None
    return None if used is None else min(100.0, used / window * 100)


def git_branch(cwd):
    try:
        out = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=cwd or None,
                             capture_output=True, text=True, timeout=1)
        name = out.stdout.strip()
        return name if out.returncode == 0 and name else None
    except (OSError, subprocess.SubprocessError):
        return None


def duration(ms):
    if not ms:
        return None
    mins = int(ms // 60000)
    return '%dh%02dm' % (mins // 60, mins % 60) if mins >= 60 else '%dm' % mins


def visible_len(text):
    out = i = 0
    while i < len(text):
        if text[i] == '\x1b':
            j = text.find('m', i)
            if j == -1:
                break
            i = j + 1
            continue
        out += 1
        i += 1
    return out


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    model = (data.get('model') or {}).get('display_name') or 'Claude'
    model_id = (data.get('model') or {}).get('id') or ''
    workspace = data.get('workspace') or {}
    cwd = workspace.get('current_dir') or data.get('cwd') or os.getcwd()
    cost = data.get('cost') or {}

    window = 1_000_000 if '[1m]' in model_id else 200_000
    pct = context_percent(data.get('transcript_path'), window)

    left = [chip(DIAMOND, model, VIOLET, VIOLET_DK)]
    branch = git_branch(cwd)
    right = [chip(BRANCH_ICON, branch, TEAL, TEAL_DK)] if branch else ['']

    row1 = [meter(pct, YELLOW_BAR, YELLOW, 'ctx ') if pct is not None
            else fg(DIM) + 'ctx  —' + RESET]
    spent = cost.get('total_cost_usd')
    if spent is not None:
        row1.append(fg(GREEN) + '$%.2f' % spent + RESET)
    took = duration(cost.get('total_duration_ms'))
    if took:
        row1.append(fg(BLUE) + took + RESET)

    row2 = []
    added, removed = cost.get('total_lines_added'), cost.get('total_lines_removed')
    if added or removed:
        row2.append(fg(GREEN) + '+%d' % (added or 0) + RESET + fg(DIM) + '/' + RESET +
                    fg('FF6B6B') + '-%d' % (removed or 0) + RESET)
    style = (data.get('output_style') or {}).get('name')
    if style and style != 'default':
        row2.append(fg(DIM) + style + RESET)

    sep = ' ' + fg(DIM) + DIVIDER + RESET + ' '
    rows = [(left[0], row1), (right[0], row2)]
    width = max(visible_len(head) for head, _ in rows)
    out = []
    for head, fields in rows:
        if not head and not fields:
            continue
        pad = ' ' * (width - visible_len(head))
        out.append(head + pad + sep + sep.join(fields) if fields else head + pad)
    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    main()
