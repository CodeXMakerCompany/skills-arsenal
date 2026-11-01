# skills-arsenal

Personal Claude Code skills, synced across machines.

Each directory is one skill, defined by a `SKILL.md` with YAML frontmatter
(`name`, `description`) followed by the instructions Claude loads on invocation.

## Skills

| Skill | Purpose |
|-------|---------|
| [`topic-miner`](topic-miner/SKILL.md) | Mine recent AI news for short-form technical video topics with a senior engineering angle. Outputs scored topics in Spanish. |
| [`stack-scout`](stack-scout/SKILL.md) | Scout tools for a need or painpoint, model real cost at your scale, decide build vs buy. Produces a sequenced build strategy when nothing fits. |
| [`anti-slop`](anti-slop/SKILL.md) | Quality gate for Spanish short-form scripts. Kills generic AI phrasing at word, rhythm and structure level, enforces the spoken word budget, returns a ships/doesn't-ship verdict. |
| [`exam-dumps`](exam-dumps/SKILL.md) | Drive the local Free-Exam-Dumps scraper: list ExamTopics certifications with descriptions, scrape the selected one, loop. Maps outputs and the two upstream breakages. |
| [`audio-clone`](audio-clone/SKILL.md) | Generate speech from text with the user's own fish.audio cloned voices. Lists My Voices, renders the chosen one to mp3, loops. Token from `.env`. |
| [`notebook-cast`](notebook-cast/SKILL.md) | Group sources into a Gemini Notebook and fire a generation — podcast by default, plus video, reports, quizzes, slides. Async: reports the artifact id, never waits. |

## Install on a new machine

This repo *is* the personal skills directory. Clone it into place:

```bash
git clone git@codexmaker:CodeXMakerCompany/skills-arsenal.git ~/.claude/skills
```

If `~/.claude/skills` already exists, clone elsewhere and symlink it instead.

## Base layer

External plugins installed alongside this repo. They are *not* part of the arsenal —
they come from the Anthropic plugin directory and follow their own release cycles.
Install them after cloning:

```bash
claude plugin install auto-research@anthropic-plugin-directory -y
claude plugin install unslop@anthropic-plugin-directory -y
claude plugin install caveman-mode-short-answers@anthropic-plugin-directory -y
claude plugin install linkedin-career-intelligence---rankedin@anthropic-plugin-directory -y
```

`hyperframes` ships from HeyGen's own marketplace rather than the Anthropic
directory, so it takes its own line:

```bash
claude plugin install hyperframes --marketplace heygen-com/hyperframes -y
```

| Plugin | Tier | Purpose | Runs |
|--------|------|---------|------|
| `hyperframes` | must | Render stage — write HTML, render video. Eight skills: the render contract, the CLI, ~450 registry blocks, captions and overlays, media and voiceover, Figma import, Remotion port, slideshows. | local |
| `auto-research` | must | Improves a skill in this repo — 5 parallel research agents, then a keep/discard loop. `/auto-research <skill>`. Rewrites `SKILL.md` in place, so commit first. | local |
| `unslop` | reference | AI-slop guardrail for prose. German/English only, so it does not replace `anti-slop` — it is the blueprint `anti-slop` was built from. | local |
| `caveman` | optional | Short, direct answers, no filler. `/caveman` toggles it. | local |
| `rankedin` | optional | Career positioning and next-move analysis. Outside the content pipeline. | remote MCP — input leaves the machine |

### Prerequisites

Only `hyperframes` needs anything beyond the install. Check both before trusting a
render on a new machine:

| Needs | Why | Check |
|-------|-----|-------|
| Node with `npx` | the CLI runs as `npx hyperframes` | `node --version` |
| `ffmpeg` on `PATH` | audio, grading, transcripts and render all shell out to it | `ffmpeg -version` |

```bash
sudo apt install ffmpeg      # Debian/Ubuntu/Pop!_OS
```

> Everything in this section is community-published and unreviewed (`review: none`),
> except `hyperframes`, which is Apache-2.0 from HeyGen.
> `claude plugin list` is the source of truth for what is enabled on a machine.

## Sync

```bash
cd ~/.claude/skills
git pull            # get skills from other machines
git add . && git commit -m "add: <skill>" && git push
```

Skills are loaded at session start — restart Claude Code after pulling for new
skills to appear in the `/` menu.


