# Submissions — what to do, and when

Two channels. Neither can be done from a terminal: both require a signed-in human, deliberately.

---

## 1. statuslin.es — ready now, blocked on one unknown

Submitting requires **signing in with GitHub** at https://statuslin.es/submit — the form isn't visible until you do.

One thing to check when you get there: the guide says the gallery *"runs the submitted script in a sandbox against the same JSON scenarios on this page"*, and the cards carry language tags like `Python`. That suggests entries are **standalone scripts**, not ccstatusline configs. If the form only accepts a script, tell me and I'll port the Noctu layout to a single self-contained file.

Honest limit if we do port it: a sandboxed script only receives Claude Code's status JSON — model, cwd, transcript path, cost, duration. The **session and weekly usage meters can't come from that**; they need the usage endpoint that ccstatusline caches. A script version would carry context, git, cost and throughput, and drop the two usage bars.

**Card text (one per theme, submit the default first):**

> **Noctu** — A two-row status line built on one rule: the bar recedes, the number speaks. Every meter splits into a muted bar and a bright value, so the shapes read as texture and the numbers carry the signal. Model and context on one row, branch and the weekly limit on the other; only those two get filled badges, because only those two are identity. The columns stay aligned at any width and with any branch name, which a config alone cannot do — a small post-render pass measures each row and pads it. Seven palettes, two layouts.

---

## 2. awesome-claude-code — blocked until 2026-09-30

Their ground rules: a resource must be **at least 14 days old with continued commits**, or have **at least 100 stars**. This repo's first commit is 2026-09-16, so it becomes eligible on **2026-09-30** — keep committing between now and then, or cross 100 stars sooner.

Submitting early gets the issue auto-closed by a bot, so don't.

Three more things from their CONTRIBUTING:

- **The web issue form only.** `gh` CLI submissions are explicitly forbidden and risk a temporary interaction ban: https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml
- **One resource at a time.** Submit the repo, not individual themes.
- **Style:** a description, not a pitch. One line. No emojis. Don't address the reader.

**Entry text, written to their style:**

> Noctu — Status line themes for Claude Code built on ccstatusline, providing two layouts and seven palettes with column-aligned meters, git-aware collapsing, and a post-render alignment script.

Their own README advertises "scintillating status lines", so the category fits.

---

## 3. What actually moves first

The list maintainer says it plainly: build, **get users**, then submit — not the reverse. So the order is statuslin.es, then your profile, then the list on the 30th.

- [ ] Sign in at statuslin.es and submit Noctu (report back what the form wants)
- [ ] Pin the repo on your profile, hide the forks
- [ ] Keep committing until 2026-09-30, then file the awesome-claude-code issue
- [ ] After acceptance, add their badge to the README
