---
name: notebook-cast
description: Group sources into a Gemini Notebook (NotebookLM) and fire off a generation — a podcast by default, or a video, briefing doc, study guide, quiz, flashcards, mindmap, slides or infographic. Use when the user says "haz un podcast", "genera un podcast de esto", "manda esto al notebook", "audio overview", "notebooklm", "gemini notebook", "crea un briefing doc", or hands over a pile of links, files or notes to be turned into something. Collects what the generation needs, submits it, and leaves it processing without waiting.
---

# Notebook Cast

Group the data, fire the generation, walk away. Report the artifact id, not a finished file.

Generation takes minutes and the CLI does not block. `create` returns an artifact id the
instant the job is queued, and the audio appears in the notebook later.

> **Wrong:** fire a podcast, then poll `studio status` in a loop until it finishes.
> **Right:** fire it, report the artifact id and how to check later, end the turn.

Never poll, never background a waiting loop, never promise a finished file in this turn.
Checking is a separate request the user makes when they come back.

---

## What to collect before firing

The user's text almost never contains all of it. Ask for what is missing **in one message**,
then fire. Do not ask one question at a time, and do not fire with a guessed focus prompt.

| Needed | Default if unstated | Must ask when |
|---|---|---|
| **Sources** — urls, files, text, YouTube, Drive ids | — | Always required. Never invent sources. |
| **Notebook** — new, or an existing one | Ask, then `notebook list` | Always. |
| **Output type** | `audio` (podcast) | Only if their words are ambiguous. |
| **Focus prompt** (`--focus`) | — | Always ask. This is the main quality lever. |
| **Language** | `es-419` | Never guess a non-Spanish language from the sources. |
| **Format / length** | `deep_dive`, `default` | Offer the options when they want something other than a standard podcast. |

The focus prompt is what separates a generic summary from the thing they wanted. This user
writes long, structured, Spanish focus prompts — roles, constraints, what to attack, the
tone, how to close. Treat a one-line focus as a smell and ask for more, or draft one from
their description and have them confirm it before firing.

---

## CLI map

| What | Where |
|---|---|
| Repo | `/home/codexmaker/Mcp/gemini-notebook-mcp-cli` |
| Binary | `nlm` → `/home/codexmaker/.local/bin/nlm` (v0.15.8) |
| Guide | `docs/CLI_GUIDE.md` in that repo |
| Downloads | `/home/codexmaker/skills-arsenal/out/notebook-cast/` |

Add `export PATH="$HOME/.local/bin:$PATH"` to any command that calls `nlm`.

Both command styles work: `nlm audio create <nb>` and `nlm create audio <nb>`. Use
noun-first consistently.

**`--confirm` / `-y` is required on every `create`.** Without it the CLI prompts, and a
non-interactive run hangs on that prompt.

---

## Auth

The account is already signed in; credentials are stored by the CLI, not in this repo.
There is **no** `nlm auth status` — the real check is a call that needs auth:

```bash
export PATH="$HOME/.local/bin:$PATH" && nlm notebook list --json
```

A notebook list means auth is good. On an auth error run `nlm auth refresh` (non-interactive)
and only fall back to `nlm login` if that fails. Never re-run login unprompted — it opens a
browser the user has to drive.

---

## The loop

1. **Collect** what the table above requires, in one message.
2. **Notebook** — `nlm notebook list` to pick one, or `nlm notebook create "Title"`.
3. **Sources** — add them and **wait**. This is the only blocking step.
4. **Fire** the generation with `--confirm --json`, capture the artifact id.
5. **Report** the id, the notebook id, and the one command to check later. Stop.
6. **Offer another** generation from the same notebook — the sources are already there, so a
   second output type is nearly free.

Step 6 matters: once a notebook holds the sources, a briefing doc or a mindmap alongside the
podcast costs one more command and no re-upload.

---

## Sources — the one place you wait

Generation starts from processed sources. Firing before they are ready produces a thin or
failed artifact, so `--wait` here and only here.

```bash
export PATH="$HOME/.local/bin:$PATH"
nlm source add <notebook> --url "https://..." --url "https://..." --wait --json
nlm source add <notebook> --youtube "https://..." --wait --json
nlm source add <notebook> --file /path/to/doc.pdf --wait --json
nlm source add <notebook> --text "..." --title "Notas" --wait --json
```

- `--url` and `--youtube` are **repeatable** — one call for a batch of links.
- `--wait-timeout` defaults to 600s. Raise it for long audio or video sources.
- Build `--text` content from a file or a heredoc, never by interpolating into a shell
  string.
- `nlm source list <notebook> --json` confirms what landed before you fire.

A source that fails to process is not a reason to abandon the run — report it, confirm the
rest are ready, and ask whether to proceed without it.

---

## Podcast (the default)

```bash
export PATH="$HOME/.local/bin:$PATH"
nlm audio create <notebook> \
  --format deep_dive --length default \
  --language es-419 \
  --focus "<the full focus prompt>" \
  --confirm --json
```

| Flag | Values |
|---|---|
| `--format` | `deep_dive` (default), `brief`, `critique`, `debate` |
| `--length` | `short`, `default`, `long` |
| `--language` | BCP-47. See below. |
| `--focus` | Free text. The main lever. |
| `--source-ids` | Comma-separated, to generate from a subset instead of the whole notebook. |

### The accent trap

The region subtag picks the **voice accent**, and the focus prompt cannot override it:

| Code | Accent |
|---|---|
| `es`, `es-ES` | Spain Spanish |
| `es-419`, `es-US` | **Latin-American Spanish — use this** |

Writing "en español latino" in the focus prompt does not change the accent. Only the
language code does. This is observed Gemini Notebook behavior, not a documented guarantee,
so re-check it if an output comes back with the wrong accent.

`NOTEBOOKLM_HL=es-419` sets it as the default for every artifact.

---

## Other output types

Same pattern: `--confirm --json`, capture the id, do not wait.

| Type | Command | Notable flags |
|---|---|---|
| Video | `nlm video create <nb>` | `--format explainer\|brief\|cinematic\|short`, `--style classic\|whiteboard\|anime\|watercolor\|retro_print\|…`, `--style-prompt` with `--style custom`. Styles do not apply to `cinematic` or `short`. |
| Report | `nlm report create <nb>` | `--format "Briefing Doc"\|"Study Guide"\|"Blog Post"\|"Create Your Own"\|Interactive`, `--prompt` |
| Quiz | `nlm quiz create <nb>` | `--count`, `--difficulty`, `--focus` |
| Flashcards | `nlm flashcards create <nb>` | `--difficulty`, `--focus` |
| Mindmap | `nlm mindmap create <nb>` | — |
| Slides | `nlm slides create <nb>` | `nlm slides revise <artifact-id> --slide '1 …'` creates a new deck |
| Infographic | `nlm infographic create <nb>` | `--orientation`, `--style` |
| Data table | `nlm data-table create <nb>` | `--description` |

`--format short` on video is vertical and about 60s — the one that fits the short-form
pipeline. Its language selection is best-effort, so add the language requirement to the
focus prompt as well as `--language`.

---

## Checking later

```bash
export PATH="$HOME/.local/bin:$PATH"
nlm studio status <notebook> --json --mcp-compatible
```

**Always `--mcp-compatible`.** Plain `--json` returns every artifact's full
`custom_instructions`, and this user's focus prompts run to thousands of words — three
artifacts measured 18 KB against 1.2 KB lean. The lean envelope also carries what you
actually need: a `summary` with `total` / `completed` / `in_progress` / `queued`, plus a
`title` and an `error_reason` per artifact.

Statuses are `queued`, `in_progress`, `completed`, `failed`. **Generations do fail** — one
of this account's three audio artifacts did — so never report a fired job as a finished one.

---

## Downloading

```bash
export PATH="$HOME/.local/bin:$PATH" && mkdir -p /home/codexmaker/skills-arsenal/out/notebook-cast
nlm download audio <notebook> --id <artifact-id> \
  --output /home/codexmaker/skills-arsenal/out/notebook-cast/<name>.m4a
```

**Audio is AAC in an MP4 container.** The output name must end `.m4a` or `.mp4`; a `.mp3`
suffix is **rejected** rather than written with contradicting bytes. Transcode afterwards
only if the user needs mp3:

```bash
ffmpeg -i raw.m4a -acodec libmp3lame -q:a 2 podcast.mp3
```

Other types: `nlm download video|report|mind-map|slide-deck|infographic|data-table`, and
`nlm download quiz|flashcards --format html|markdown`. `nlm download all <nb> --output-dir`
pulls every completed artifact at once.

`out/` is gitignored, so nothing downloaded here is ever committed.

---

## Failure modes

| Symptom | Cause | Response |
|---|---|---|
| Command hangs with no output | `--confirm` missing, sitting on a prompt | Kill it, re-run with `--confirm`. |
| `status: failed`, `generation_failed` | Expired auth, rate limit, or an unsupported prompt | Check auth, then retry. If the same prompt fails twice, the prompt is the suspect. |
| Thin or generic artifact | Fired before sources finished | Confirm `source list` is ready, then regenerate. |
| Spain accent on Spanish audio | `--language es` or `es-ES` | Re-fire with `es-419`. The focus prompt cannot fix it. |
| `.mp3` download rejected | Audio is AAC/MP4 | Download `.m4a`, transcode after. |
| Status output floods the context | Plain `--json` with long focus prompts | Always `--mcp-compatible`. |
| Auth error mid-run | Session expired | `nlm auth refresh` first, `nlm login` only if that fails. |

---

## Boundaries

- Do not wait for a generation, in the foreground or the background. Fire and report.
- Do not invent sources, and do not add a source the user did not give you.
- Do not write the focus prompt and fire it unconfirmed. Draft it, show it, fire on their yes.
- Do not delete notebooks, sources or artifacts without an explicit instruction — every
  destructive command needs `--confirm` for a reason.
- Do not run `nlm login` unprompted; it hijacks a browser.
- Do not make a notebook public (`nlm share public`) unless asked. These notebooks hold the
  user's unpublished work.
- One generation per explicit request. No batch loops over a list of notebooks.

---

## Pipeline handoff

This is a research-and-package stage, not a replacement for the script pipeline. Two real
seams:

- **Into the pipeline.** A briefing doc or study guide over a pile of primary sources is good
  raw material for `topic-miner`, which wants Tier 1 detail. The notebook does the reading.
- **Alongside it.** A NotebookLM podcast is two synthetic hosts discussing sources — a
  different product from a 30–60s scripted short. It does not go through `anti-slop` or
  `audio-clone`, and it is not voiced in the user's own cloned voice. Keep them separate
  rather than feeding one into the other.

CLI surface verified 2026-11-01 against `nlm` 0.15.8 at commit `8ac9728`. Re-read
`docs/CLI_GUIDE.md` after any update to that repo — the command set moves.
