#!/usr/bin/env python3
"""Noctu - a two-row status line for Claude Code, no dependencies.

Reads Claude Code's session JSON on stdin and prints two rows: a model chip
with the context meter, effort and session time, then a branch chip with the
weekly limit, its reset, cost and lines changed.

The source is ASCII-only on purpose: every glyph is a unicode escape, so the file
survives any copy-paste, and output is written as UTF-8 bytes whatever the
console's encoding.

The design rule: the bar recedes, the number speaks. Meters are a muted bar
plus a bright value, and only the model and the branch get filled badges,
because only those two are identity. The columns are aligned by measuring
each row rather than padding to a guess, so they hold with any branch name.
"""
# plain:begin
# This variant makes no network calls and reads no credentials. For the weekly
# Fable window too, use noctu-fable.py.
# plain:end
# fable:begin
# Fable variant: the weekly Fable window only comes from Anthropic's usage
# endpoint, so this file reads your Claude Code OAuth token (the
# CLAUDE_CODE_OAUTH_TOKEN env var, ~/.claude/.credentials.json, or the macOS
# Keychain entry "Claude Code-credentials") and calls api.anthropic.com with
# it, at most once every three minutes. The token goes nowhere else.
# Without the token or the network it shows a dim dash.
# fable:end
import json
import os
import subprocess
import sys
import time
# fable:begin
import urllib.request
# fable:end

# palette (hex -> truecolor SGR)
VIOLET, VIOLET_DK = '7C5CFF', '5B3FD1'
TEAL, TEAL_DK = '2E9E7A', '1E6B52'
# outside a repository: the divider grey, sunk toward the background
SLATE, SLATE_DK, SLATE_INK, SLATE_GLYPH = '3C414B', '262A32', '979CA8', '727681'
YELLOW, YELLOW_BAR = 'F0C755', '6B5A28'
PURPLE, PURPLE_BAR, PURPLE_DIM = 'B69CFF', '463A6B', '8B79C9'
ORANGE, ORANGE_BAR, ORANGE_DIM = 'E8903C', '7A4A1E', 'C97B3C'
GREEN, BLUE, DIM, INK, WHITE = '7CE38B', '5B9BE8', '79808E', '0B0E14', 'FFFFFF'
EFFORT = '3E8E5A'
# fable:begin
RED, RED_LABEL = 'FF6B6B', '9C4A4A'
USAGE_URL = 'https://api.anthropic.com/api/oauth/usage'
USAGE_CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'noctu', 'usage.json')
USAGE_TTL, USAGE_RETRY = 180, 60
# fable:end
BAR_FULL, BAR_EMPTY, ARROW, DIVIDER, BRANCH_ICON, DIAMOND = '\u2593', '\u2591', '\ue0b0', '\u258f', '\uf418', '\u25c6'
BAR_WIDTH = 10


def fg(h):
    return '\x1b[38;2;%d;%d;%dm' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def bg(h):
    return '\x1b[48;2;%d;%d;%dm' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


RESET = '\x1b[0m'


def chip(icon, label, body, icon_bg, ink=INK, glyph=WHITE, bold=True):
    """icon compartment + label + arrow cap - the badge that anchors each row"""
    return (bg(icon_bg) + fg(glyph) + ' ' + icon + ' ' + RESET +
            bg(body) + fg(ink) + ('\x1b[1m ' if bold else ' ') + label + ' ' + RESET +
            fg(body) + ARROW + RESET)


def meter(pct, bar_colour, value_colour, label):
    filled = round(max(0.0, min(100.0, pct)) / 100 * BAR_WIDTH)
    bar = fg(bar_colour) + BAR_FULL * filled + BAR_EMPTY * (BAR_WIDTH - filled) + RESET
    return (fg(value_colour) + label + RESET + ' ' + bar + ' ' +
            fg(value_colour) + '%d%%' % round(pct) + RESET)


def dim_meter(label):
    return fg(DIM) + label + ' \u2014' + RESET


def until(epoch):
    """Compact countdown to a unix time: 2d1h, 3h07m, 18m."""
    try:
        left = max(0, int(float(epoch) - time.time()))
    except (TypeError, ValueError):
        return None
    days, rem = divmod(left, 86400)
    hours, mins = rem // 3600, rem % 3600 // 60
    if days:
        return '%dd%dh' % (days, hours)
    return '%dh%02dm' % (hours, mins) if hours else '%dm' % mins


def limit_meter(limits):
    """The weekly window, or the five-hour one when that's all that has reported."""
    limits = limits if isinstance(limits, dict) else {}
    for key, label, bar, value, timer in (('seven_day', 'week', PURPLE_BAR, PURPLE, PURPLE_DIM),
                                          ('five_hour', '5h  ', ORANGE_BAR, ORANGE, ORANGE_DIM)):
        window = limits.get(key)
        if isinstance(window, dict) and window.get('used_percentage') is not None:
            left = until(window.get('resets_at'))
            return (meter(window['used_percentage'], bar, value, label),
                    fg(timer) + left + RESET if left else fg(DIM) + '\u2014' + RESET)
    return dim_meter('week'), fg(DIM) + '\u2014' + RESET


# fable:begin
def claude_token():
    """Claude Code's OAuth access token, from wherever Claude Code keeps it."""
    token = os.environ.get('CLAUDE_CODE_OAUTH_TOKEN')
    if token:
        return token
    try:
        with open(os.path.join(os.path.expanduser('~'), '.claude', '.credentials.json')) as fh:
            return json.load(fh)['claudeAiOauth']['accessToken']
    except (OSError, ValueError, KeyError, TypeError):
        pass
    if sys.platform == 'darwin':
        try:
            out = subprocess.run(['security', 'find-generic-password', '-s', 'Claude Code-credentials', '-w'],
                                 capture_output=True, text=True, timeout=2)
            return json.loads(out.stdout)['claudeAiOauth']['accessToken']
        except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
            pass
    return None


def parse_fable(usage):
    """The Fable-scoped weekly limit; older responses carried it as seven_day_fable."""
    for limit in usage.get('limits') or []:
        scope = (limit or {}).get('scope') or {}
        if limit.get('kind') == 'weekly_scoped' and (scope.get('model') or {}).get('display_name') == 'Fable':
            return limit.get('percent')
    return (usage.get('seven_day_fable') or {}).get('utilization')


def fable_percent():
    """Weekly Fable utilisation, cached on disk so renders don't each hit the API."""
    try:
        with open(USAGE_CACHE) as fh:
            cached = json.load(fh)
        ttl = USAGE_TTL if cached.get('fable') is not None else USAGE_RETRY
        if time.time() - cached.get('fetched_at', 0) < ttl:
            return cached.get('fable')
    except (OSError, ValueError, AttributeError):
        pass
    fable = None
    token = claude_token()
    if token:
        request = urllib.request.Request(USAGE_URL, headers={
            'Authorization': 'Bearer ' + token, 'anthropic-beta': 'oauth-2025-04-20'})
        try:
            with urllib.request.urlopen(request, timeout=2) as res:
                fable = parse_fable(json.load(res))
        except (OSError, ValueError, AttributeError):
            fable = None
    try:
        os.makedirs(os.path.dirname(USAGE_CACHE), exist_ok=True)
        tmp = USAGE_CACHE + '.%d' % os.getpid()
        with open(tmp, 'w') as fh:
            json.dump({'fetched_at': time.time(), 'fable': fable}, fh)
        os.replace(tmp, USAGE_CACHE)
    except OSError:
        pass
    return fable


# fable:end
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

    # Claude Code reports context usage directly; the transcript estimate is
    # only a fallback for versions that predate context_window
    ctx = data.get('context_window')
    if isinstance(ctx, dict):
        pct = ctx.get('used_percentage')
    else:
        window = 1_000_000 if '[1m]' in model_id else 200_000
        pct = context_percent(data.get('transcript_path'), window)

    left = [chip(DIAMOND, model, VIOLET, VIOLET_DK)]
    branch = git_branch(cwd)
    right = [chip(BRANCH_ICON, branch, TEAL, TEAL_DK) if branch else
             chip(BRANCH_ICON, 'no git', SLATE, SLATE_DK, SLATE_INK, SLATE_GLYPH, bold=False)]

    row1 = [meter(pct, YELLOW_BAR, YELLOW, 'ctx ') if pct is not None
            else dim_meter('ctx ')]
    level = (data.get('effort') or {}).get('level')
    row1.append(fg(EFFORT) + level + RESET if level else fg(DIM) + '\u2014' + RESET)
    took = duration(cost.get('total_duration_ms'))
    row1.append(fg(BLUE) + took + RESET if took else fg(DIM) + '\u2014' + RESET)

    row2 = list(limit_meter(data.get('rate_limits')))
    # fable:begin
    fable = fable_percent()
    row2.append(fg(RED_LABEL) + 'fable ' + RESET + fg(RED) + '%d%%' % round(fable) + RESET
                if isinstance(fable, (int, float)) else fg(DIM) + 'fable \u2014' + RESET)
    # fable:end
    spent = cost.get('total_cost_usd')
    if spent is not None:
        row2.append(fg(GREEN) + '$%.2f' % spent + RESET)
    added, removed = cost.get('total_lines_added'), cost.get('total_lines_removed')
    if added or removed:
        row2.append(fg(GREEN) + '+%d' % (added or 0) + RESET + fg(DIM) + '/' + RESET +
                    fg('FF6B6B') + '-%d' % (removed or 0) + RESET)
    style = (data.get('output_style') or {}).get('name')
    if style and style != 'default':
        row2.append(fg(DIM) + style + RESET)

    # every column lines up: pad each cell to the widest one above or below it
    rows = [[left[0]] + row1, [right[0]] + row2]
    widths = {}
    for cells in rows:
        for i, cell in enumerate(cells[:-1]):
            widths[i] = max(widths.get(i, 0), visible_len(cell))
    sep = ' ' + fg(DIM) + DIVIDER + RESET + ' '
    out = [sep.join(cell + ' ' * (widths.get(i, 0) - visible_len(cell)) if i < len(cells) - 1 else cell
                    for i, cell in enumerate(cells))
           for cells in rows]
    sys.stdout.buffer.write('\n'.join(out).encode('utf-8'))


if __name__ == '__main__':
    main()
