# Noctu — standalone

`noctu.py` is the Noctu design as a single dependency-free script: it reads Claude Code's session JSON on stdin and prints two rows. No ccstatusline, no network, no packages.

![preview](preview.png)

```json
"statusLine": { "type": "command", "command": "python3 ~/.claude/noctu.py", "padding": 0 }
```

**What it shows:** model, context usage, git branch, cost, session duration, lines changed. Each field appears only when the data is there — no branch outside a repo, no context bar without a readable transcript.

**What it can't show, and why:** the session, weekly and Fable usage meters in the ccstatusline themes come from Anthropic's usage endpoint. A status line that runs without network access cannot have them. If you want those, use the [ccstatusline themes](../README.md) instead — this script is for people who want the look with nothing to install.

Context is read from the transcript's most recent token usage against a 200k window, or 1M when the model id says so.

**License:** this file is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) so it can live in galleries that require public-domain submissions. The rest of the repository is MIT.
