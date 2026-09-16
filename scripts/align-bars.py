#!/usr/bin/env python3
"""Align meter bars into one column across status line rows.

ccstatusline can't do this: each row's bar sits behind a variable-width field
(model name, git branch), so the column moves. We pad after the fact — find the
first bar glyph on every row, and insert spaces before the short ones.
"""
import sys

BARS = ('▓', '░')
MARK = '\u200b'   # pad here to line the meters up
MARK2 = '\u2060'  # pad here to line up whatever follows the percentages
MARK3 = '\u2061'  # and again for the column after that
COLUMN_MARKS = (MARK2, MARK3)


def bar_position(line):
    """Return (string index, visible column) of the first bar glyph, or None."""
    col = i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\x1b':
            j = line.find('m', i)
            if j == -1:
                break
            i = j + 1
            continue
        if c in BARS:
            return i, col
        col += 1
        i += 1
    return None


def visible_column(line, needle):
    """Return (string index, visible column) of `needle`, ignoring ANSI escapes."""
    col = i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\x1b':
            j = line.find('m', i)
            if j == -1:
                break
            i = j + 1
            continue
        if c == needle:
            return i, col
        if c not in (MARK, MARK2, MARK3):
            col += 1
        i += 1
    return None


def main():
    lines = sys.stdin.read().split('\n')
    spots = [bar_position(l) for l in lines]
    cols = [s[1] for s in spots if s]
    if len(cols) > 1:
        target = max(cols)
        for n, spot in enumerate(spots):
            if spot:
                idx, col = spot
                if col < target:
                    # pad at the marker (left of the label) so labels stay flush,
                    # falling back to just before the bar when no marker is set
                    at = lines[n].find(MARK)
                    if at == -1 or at > idx:
                        at = idx
                    lines[n] = lines[n][:at] + ' ' * (target - col) + lines[n][at:]
    # later passes: line up each marked column in turn, left to right
    for mark in COLUMN_MARKS:
        spots = [visible_column(l, mark) for l in lines]
        found = [s for s in spots if s]
        if len(found) < 2:
            continue
        target = max(c for _, c in found)
        for n, spot in enumerate(spots):
            if spot:
                idx, col = spot
                if col < target:
                    lines[n] = lines[n][:idx] + ' ' * (target - col) + lines[n][idx:]

    sys.stdout.write('\n'.join(l.replace(MARK, '').replace(MARK2, '').replace(MARK3, '') for l in lines))


if __name__ == '__main__':
    main()
