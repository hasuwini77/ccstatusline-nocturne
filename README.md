# Nocturne — a ccstatusline theme

A two-line status line for [Claude Code](https://claude.com/claude-code), built for dark terminals with a busy background: muted bars, bright numbers, and two badges that anchor the eye.

![Nocturne status line](preview.png)

```
◆  Opus 5 ▏ medium ▏ ctx ▓▓▓▓░░ 42% ▏ 128 t/s ▏ ok ▏ $0.42
 master ▏ session ▓░░░░ 2% 4h29m ▏ week ▓▓▓░░ 51% 2d6h49m
```

## The idea

Most status lines shout. This one is built on one rule: **the bar recedes, the number speaks.** Every meter is two pieces — a muted bar in a dark tint and its percentage in the bright accent — so the shapes read as texture and your eye lands on the values.

- **Two badges, not blocks.** Only the model and the branch carry filled chips, each with its own icon compartment in a deeper tone. Everything else is flat text.
- **Colour means something.** Yellow is context, orange is the session window, purple is the week, blue is throughput, green is health and cost. Each meter's countdown inherits its own colour, so a meter reads as one unit.
- **Same at every width.** No flex stretching, so nothing jumps when you split a pane. Needs ~60 columns; degrades by truncation below that.
- **Quiet when there's nothing to say.** The branch badge, its wedge and divider all disappear outside a git repository, and counters hide at zero.


## The four themes

Every theme is the same layout and the same rules — only the surface changes. Pick one, copy its `settings.json`.

### Nocturne
The original. Two badges, muted bars, thin dividers.

![Nocturne](themes/nocturne/preview.png)

```bash
cp themes/nocturne/settings.json ~/.config/ccstatusline/settings.json
```

### Nocturne Flat
**No Nerd Font required** — not a single private-use glyph. Same colours and layout, plain `|` dividers, no badges. Use this over SSH, in a bare terminal, or anywhere the fancy glyphs come out as boxes.

![Nocturne Flat](themes/nocturne-flat/preview.png)

```bash
cp themes/nocturne-flat/settings.json ~/.config/ccstatusline/settings.json
```

### Nocturne Powerline
The loud one. Every field is a filled block with arrow separators, for people who want the classic powerline look.

![Nocturne Powerline](themes/nocturne-powerline/preview.png)

```bash
cp themes/nocturne-powerline/settings.json ~/.config/ccstatusline/settings.json
```

### Nocturne Light
For light terminals. The palette is re-derived rather than inverted — bars go pale, values go deep, so contrast holds on a white background.

![Nocturne Light](themes/nocturne-light/preview.png)

```bash
cp themes/nocturne-light/settings.json ~/.config/ccstatusline/settings.json
```

## Install

Requires **ccstatusline ≥ 2.2.29**, a **Nerd Font**, and a truecolor terminal (WezTerm, Ghostty, iTerm2, Windows Terminal).

```bash
npm i -g ccstatusline@2.2.29
mkdir -p ~/.config/ccstatusline
cp themes/nocturne/settings.json ~/.config/ccstatusline/settings.json
```

Then point Claude Code at ccstatusline. Copy `statusline.sh` to `~/.claude/statusline.sh` and add this to `~/.claude/settings.json`:

```json
"statusLine": { "type": "command", "command": "bash ~/.claude/statusline.sh", "padding": 0 }
```

The launcher resolves the global install directly instead of going through `npx`, which otherwise re-bootstraps npm on **every render**. It checks nvm and Homebrew paths, and falls back to `npx` only if no global install exists.

## Palette

| Field | Bar | Value |
|---|---|---|
| Context | `#6B5A28` | `#F0C755` |
| Session | `#7A4A1E` | `#E8903C` |
| Week | `#6B4BA8` | `#B69CFF` |
| Model badge | `#5B3FD1` / `#7C5CFF` | `#0B0E14` |
| Branch badge | `#1E6B52` / `#2E9E7A` | `#0B0E14` |
| Throughput | — | `#5B9BE8` |
| Cost / health | — | `#7CE38B` / `#3E8E5A` |
| Separators | — | `#79808E` |

Swap any of them in `settings.json`. Colours use the `hex:RRGGBB` form — **no `#`**, or ccstatusline silently renders them uncoloured.

## Notes

The preview shows a sample session. Widths were checked at 230, 113 and 100 columns, inside a repo and outside one.

This is a **configuration, not a fork**. It contains no ccstatusline code — just a `settings.json` describing widgets, colours and layout. The program itself is [ccstatusline](https://github.com/sirmalloc/ccstatusline) by sirmalloc (MIT); install it from npm and point it at this file.

## License

MIT
