# Noctu — standalone

`noctu.py` is the Noctu design as a single dependency-free script: it reads Claude Code's session JSON on stdin and prints two rows. No ccstatusline, no network, no packages.

![preview](preview.png)

```json
"statusLine": { "type": "command", "command": "python3 ~/.claude/noctu.py", "padding": 0 }
```

**What it shows:** model, context meter, effort and session time on the first row; the git branch (or a muted `no git` chip), the weekly limit meter with its reset countdown, cost, lines changed and a non-default output style on the second. Every column is padded to its widest cell, so both rows line up.

**Where the numbers come from:** all of it is in the session JSON Claude Code pipes in. Context is `context_window.used_percentage`, and the limit meter is `rate_limits.seven_day`, or `five_hour` when that's the only window reported. No network. On older Claude Code versions without `context_window`, context falls back to the transcript's last token usage. A field with no data shows a dim dash instead of moving the columns.

**Want the Fable window too?** Use [`noctu-fable.py`](noctu-fable.py) instead. It's the same script plus `fable 15%` on the second row. That number only comes from Anthropic's usage endpoint, so this variant reads your Claude Code OAuth token (the `CLAUDE_CODE_OAUTH_TOKEN` env var, then `~/.claude/.credentials.json`, then the macOS Keychain entry Claude Code writes). It sends the token only to `api.anthropic.com`, and at most once every three minutes (cached in `~/.cache/noctu/usage.json`). No token or no network shows a dim dash.

```json
"statusLine": { "type": "command", "command": "python3 ~/.claude/noctu-fable.py", "padding": 0 }
```

Edit `noctu-fable.py`; `noctu.py` is generated from it by stripping the `# fable:begin` / `# fable:end` blocks. Run `python3 scripts/make_standalone.py` after an edit. The build refuses to write if any token or network code reaches the plain file.

**Portable on purpose:** the source is plain ASCII, with every glyph written as a unicode escape, so it survives any clipboard. Output is written as UTF-8 bytes, so a Windows console can't garble it.

**Check it:** `python3 standalone/scenarios.py` renders it against the eight example sessions the [statuslin.es](https://statuslin.es) sandbox uses and checks every value and column, for both files. The Fable variant runs against a stubbed usage endpoint.

**License:** this file is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) so it can live in galleries that require public-domain submissions. The rest of the repository is MIT.
