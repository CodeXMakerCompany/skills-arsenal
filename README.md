# skills-arsenal

Personal Claude Code skills, synced across machines.

Each directory is one skill, defined by a `SKILL.md` with YAML frontmatter
(`name`, `description`) followed by the instructions Claude loads on invocation.

## Skills

| Skill | Purpose |
|-------|---------|
| [`topic-miner`](topic-miner/SKILL.md) | Mine recent AI news for short-form technical video topics with a senior engineering angle. Outputs scored topics in Spanish. |

## Install on a new machine

This repo *is* the personal skills directory. Clone it into place:

```bash
git clone git@codexmaker:CodeXMakerCompany/skills-arsenal.git ~/.claude/skills
```

If `~/.claude/skills` already exists, clone elsewhere and symlink it instead.

> The `codexmaker` host alias routes through the personal SSH key.
> See `~/.ssh/config`. Using `git@github.com:` directly would pick the wrong key.

## Sync

```bash
cd ~/.claude/skills
git pull            # get skills from other machines
git add . && git commit -m "add: <skill>" && git push
```

Skills are loaded at session start — restart Claude Code after pulling for new
skills to appear in the `/` menu.

## Content pipeline

`topic-miner` is the first stage of a short-form technical content pipeline.
Planned stages:

| Skill | Stage | Status |
|-------|-------|--------|
| `topic-miner` | Mine AI news → scored topics | ✅ |
| `scar-extractor` | Interview loop → personal war stories | ⬜ |
| `anti-slop` | Quality gate — kills generic AI phrasing | ⬜ |
| `short-script` | Topic → 30–60s script, word-budgeted | ⬜ |
| `hook-engineer` | First 1.5 seconds, ranked variants | ⬜ |
| `voice-card` | Locked persona spec for consistency | ⬜ |
| `caption-spec` | Word-level timed captions, mobile-safe | ⬜ |
| `code-on-screen` | Legible code in 9:16 vertical | ⬜ |
| `series-architect` | Multi-part arcs that compound | ⬜ |

Pipeline state (topics, scripts, posts, metrics) lives in Airtable.
This repo holds the *system*; Airtable holds the *inventory*.
