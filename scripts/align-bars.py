#!/usr/bin/env python3
"""Align meter bars into one column across status line rows.

ccstatusline can't do this: each row's bar sits behind a variable-width field
(model name, git branch), so the column moves. We pad after the fact — find the
first bar glyph on every row, and insert spaces before the short ones.
"""
import sys

BARS = ('▓', '░')
MARK = '\u200b'  # zero-width space marking where padding goes (left of the label)


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
    sys.stdout.write('\n'.join(l.replace(MARK, '') for l in lines))


if __name__ == '__main__':
    main()
