# Submissions — what to do, and when

Two channels. Neither can be done from a terminal: both require a signed-in human, deliberately.

---

## 1. statuslin.es — resubmit as v2

Entries are **standalone scripts** run with `python3 script < session.json` in a sandbox, across eight example sessions. Submit `standalone/noctu.py`, interpreter **python**, network access **off**.

v1 (slug `noctu-70fc3a9b`, 2026-09-16) rendered as mojibake: the source was pasted through a non-UTF-8 clipboard. It also ignored `context_window` and `rate_limits`. v2 fixes all of it (#3). Before pasting, run `python3 standalone/scenarios.py` and expect `ok: 8 statuslin.es scenarios`. Copy the file from GitHub's raw view, not a terminal.

There's no edit button on the site, so ask hello@statuslin.es to withdraw v1.

**Title:** Noctu

**Description:**

> Two aligned rows with muted bars and bright values: model, context, effort and session time, then git branch (or a muted no-git chip), weekly limit with reset countdown, cost and lines changed. Themed ccstatusline version at github.com/hasuwini77/ccstatusline-nocturne

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
