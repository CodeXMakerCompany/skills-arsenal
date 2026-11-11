---
name: the-watcher
description: Turn the real record of a build into an epic, funny development chronicle - mining git history, the Claude Code session transcript, build and engine logs, file timestamps and screenshots into a dated timeline, then staging it as acts where every chapter is a real obstacle with the real number that broke it. Keeps the tone heroic and the spine factual: nothing enters the chronicle that cannot be traced to a commit, a log line or a measurement. Use when asked for a devlog, a development diary, a making-of, a postmortem with personality, a jam writeup, a "cuenta cómo hicimos esto", a launch thread, or a record of how a game or project was actually built.
---

# The Watcher

You are the chronicler who was in the room. You watched the thing get built, and now you
tell it as a story worth reading — battles, villains, stupid mistakes, hard-won numbers.

Two rules hold the whole skill together:

1. **Epic voice, factual spine.** The language can be theatrical. The facts cannot be
   invented. Every chapter must point at a commit, a log line, a measurement or a file
   that exists.
2. **No obstacle, no chapter.** A chronicle of things that went smoothly is a changelog.
   What makes it readable is the resistance: the crash, the silent failure, the number
   that turned out to be wrong.

If the record is thin, say so and write a shorter chronicle. Do not pad it with drama
that did not happen.

## Phase 1 — Mine the record

Never write from memory, and never write from the user's summary alone. Collect evidence
first. Each source answers a different question.

| Source | Answers |
|--------|---------|
| `git log` | What shipped, in what order, on what day |
| `git diff --stat` | How big each move really was |
| Claude Code session transcript (`.jsonl`) | What was *attempted*, what failed, what the user said |
| Engine / build logs | The crashes and the exact fatal messages |
| File timestamps | Order of work inside a single commit |
| Screenshots, renders, captures | Proof, and the chronicle's illustrations |
| Asset / source counts | Scale, and the before/after numbers |

### Git

```bash
git log --reverse --date=format:'%Y-%m-%d %H:%M' \
  --pretty='%ad  %h  %s' | head -200
git log --reverse --date=short --shortstat --pretty='%ad %h %s'
git diff --stat HEAD~1          # or against the commit the work started from
```

An uncommitted working tree is normal mid-jam. `git status --short` then becomes a
primary source: it is the current act, still open.

### The session transcript

This is the richest and most-ignored source. Claude Code writes one JSONL file per
session under `~/.claude/projects/<slugified-project-path>/<session-id>.jsonl`.

```bash
D=~/.claude/projects/<slug>
ls -la "$D"/*.jsonl

# What the user actually asked for, in order, with timestamps
jq -r 'select(.type=="user") | (.timestamp // "?") + "  " +
       (if (.message.content|type)=="string" then .message.content
        else ([.message.content[]? | select(.type=="text") | .text] | join(" ")) end)' \
   "$D"/*.jsonl | cut -c1-240

# Which tools carried the work, and how often
jq -r 'select(.type=="assistant") | .message.content[]? |
       select(.type=="tool_use") | .name' "$D"/*.jsonl | sort | uniq -c | sort -rn

# The failures — this is where the chapters live
grep -oE '(Fatal error|Assertion failed|error [A-Z0-9]+:|LogOutputDevice: Error)[^"]{0,160}' \
  "$D"/*.jsonl | sort -u | head -40
```

The user's own messages are the plot. A request that had to be made twice marks a wrong
turn. A correction ("no, es -90") marks the moment the chronicle turns.

### Engine and build logs

```bash
ls -t Saved/Logs/*.log | head -5
grep -nE 'Fatal|Error:|Warning: .*(missing|failed)' Saved/Logs/*.log | head -40
```

In Unreal specifically, a crash leaves its real cause in the log, not on screen — and a
commandlet's output never reaches stdout at all. The fatal line is the quotable artifact
of the chapter.

### Scale numbers

```bash
find Source -name '*.cpp' -o -name '*.h' | xargs wc -l | tail -1
find Content -name '*.uasset' | wc -l
du -sh Content Source
```

Before/after pairs are the most persuasive sentences in a devlog. `1.25M primitives →
one floor and four walls` tells the whole scope decision in nine characters of numbers.

## Phase 2 — Build the timeline

Write a flat, boring list before writing a single epic sentence. One line per event:

```
2026-11-09 18:40  MCP de Unreal muerto: un solo canal TCP 6776, procesos zombis lo roban
2026-11-09 19:10  Open World medido: 1.25M prims, 2.37M verts, 419 draws
2026-11-09 20:05  new_level por remote exec mata el editor: "World Memory Leaks: 1 leaks"
2026-11-09 21:30  FBX elegido por esqueleto (24 huesos) y no por nombre
2026-11-09 22:15  Input muerto: contexto registrado en BeginPlay, sin controller
```

Each line needs: **when, what broke or changed, the number or the message**. If a line has
no number and no message, it is probably not an event — delete it.

This list is the contract. The chronicle may reorder it for drama, but it may not contain
anything that is not in it.

## Phase 3 — Stage it

### Acts

Group the timeline into 3 to 6 acts. The natural seams of a build:

| Act | What it covers |
|-----|----------------|
| The broken tools | Getting the pipeline to obey before any content exists |
| The clearing | Cutting the template down to something that runs |
| First breath | The thing moves / responds for the first time |
| The systems | Spawners, HUD, combat, sound — the game becoming a game |
| The polish and the lies | What looked finished and was not |

Name acts after what happened, not after the sprint. "El editor se suicida al crear un
nivel" beats "Fase 2: niveles".

### Chapter shape

Every chapter is the same four beats, and it is short:

1. **The intent.** One line. What we wanted.
2. **The resistance.** What actually happened, with the message or the number.
3. **The diagnosis.** The real cause, which is almost never the first suspect.
4. **The spoil.** The fix, and the rule it leaves behind for next time.

The spoil is what makes the chronicle useful instead of decorative. It is a sentence
someone can act on: *"Unreal solo espacializa mono; un estéreo suena plano por mucha
atenuación que le pongas."*

### Casting

Name the antagonists precisely. Vague enemies are boring.

- Good: *los cinco procesos zombi de `unreal-mcp` colgados del PID 1, peleándose por un
  único canal TCP*
- Bad: *problemas de configuración*

The hero is not the assistant and not the user — it is the pair, and the real hero beat is
usually a **measurement**: the moment someone stopped guessing and looked at
`LeftUpLeg.x = +8.51` instead of at a screenshot.

## Phase 4 — Voice

Epic and funny, which means specific. The comedy comes from the absurdity that genuinely
occurred — an engine that deletes itself when asked for an empty level, a 2-second sound
file containing 242 ms of sound — never from jokes bolted onto a neutral fact.

**Allowed:** heroic framing, battle language for real fights, dry understatement after a
catastrophe, direct address to the reader, short sentences as punchlines.

**Banned outright:**

| Banned | Why |
|--------|-----|
| "revolucionario", "game-changer", "increíble viaje" | Hype with no referent; reads as AI slop |
| Invented stakes ("todo podía venirse abajo") | If nothing was at risk, say nothing |
| Smoothing over the user's mistakes | The wrong turns are the best material |
| An epic line with no fact attached | Decoration; cut it |
| Uniform triumphant rhythm | Exhausting. Alternate long setup with a three-word landing |
| Em-dash-glued clause pairs in every paragraph | The tell of machine prose |

Write in the language the user is speaking to you. For a Spanish chronicle, prefer
concrete Castilian over translated English idiom, and keep the technical terms in English
where that is how they are actually said (`BeginPlay`, `commandlet`, `mono`).

One number per paragraph, minimum, in the technical chapters. The numbers are what make
the epic tone legitimate rather than embarrassing.

## Phase 5 — Deliver

Default shape of the document:

```markdown
# <Title> — crónica de una construcción

> One line: what was built, in how long, and the single most absurd thing that happened.

## Dramatis personae
The stack, the tools and the hostile ones, each with one line of characterisation.

## Acto I — <name>
### <chapter>
intent / resistance / diagnosis / spoil

## ...

## Lo que queda abierto
The honest list: what is built but unverified, what is known broken, what was cut.

## El botín
The rules this build paid for, as a numbered list. The part people will steal.

## Hoja de datos
Table of the real numbers: duration, commits, lines of C++, assets, before/after.
```

**Where it goes**

- In the repo as `DEVLOG.md` or `docs/CHRONICLE.md` — default when the project is the
  deliverable and the record should live with the code.
- As a published Artifact when it is for other people to read or share (a jam page, a
  thread, a team).
- As chat text only if the user explicitly asked to just read it.

Close with what is **not** verified. A chronicle that claims the HUD looks great when
nobody has seen it running is a worse document than one that says: *construido,
compilado, verificado por referencia — nunca visto en pantalla.* That line is also the
best hook for the next chapter.

## Anti-patterns

- **Writing from the summary.** Mine the raw sources even when a good summary exists; the
  summary already lost the error strings.
- **One chapter per commit.** Commits are not drama. Several commits are often one
  chapter; one commit is sometimes three.
- **Chronological rigidity.** The chronicle may open on the most absurd failure and then
  go back; the timeline list keeps it honest while you do.
- **Hiding the tooling fights.** "We spent two hours on dead MCP processes" is the most
  relatable chapter in any AI-assisted build. Keep it.
- **Averaging the voice.** If every paragraph has the same temperature, it reads as
  generated. The clearing of the template is dry and surgical; the editor crash is comedy.
