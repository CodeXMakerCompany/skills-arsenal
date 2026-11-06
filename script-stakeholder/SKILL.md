---
name: script-stakeholder
description: Write the storyboard and narration for a video that explains a change to product owners, stakeholders and other non-technical people — what someone could not do before, what they can do now, why it matters, and what it still does not do. Strips all technical detail: no code, terminals, logs, architecture or jargon. Use when the user asks for a video for the PO, business, clients or leadership, "para el PO", "para stakeholders", "explícalo simple", "sin tecnicismos", "para negocio", or hands over a shipped change to be communicated.
---

# Script — Stakeholder

They do not need to know how it works. They need to know **what changed for a person,
and whether it was worth it.**

The failure mode is not being too simple. It is explaining the machine instead of the
outcome — a pipeline diagram where a before-and-after belonged.

> "We migrated the import to a queue-backed worker, so throughput went from 40 to 900
>  rows per second."
> → true, and it answers a question nobody in the room asked.
>
> "Onboarding a new client used to take an afternoon. It now takes under a minute,
>  and nobody has to babysit it."
> → the same change, in the terms the decision was funded in.

---

## The hard rule

**The output is always a script, and nothing technical appears in it.**

Never on screen: code, terminals, logs, stack traces, config files, SQL, queries,
architecture diagrams, dashboards full of metrics, internal service names, branch names,
ticket ids, version strings.

Never in the words: the jargon in the swap table below, untranslated.

What *is* on screen: the product as a person uses it, the outcome, and at most one
number framed as a person's experience.

If the change has no visible surface — a refactor, an infrastructure migration — say so
plainly and script the *consequence* instead: what is now possible, cheaper, or no
longer at risk. A video of nothing visible is an honest two frames, not a fabricated
demo.

---

## This skill inverts the arsenal's language rule

`topic-miner` and `script-qa` keep technical nouns in English because engineers read
them faster. Here that rule is wrong. A stakeholder does not know what `el deployment`
is, and asking them to is how a good change gets heard as noise.

Every technical term is replaced by the outcome it produces:

| Don't say | Say |
|-----------|-----|
| el deployment, deploy | la nueva versión ya está disponible |
| latency, p99, response time | cuánto tarda en responder |
| el endpoint, la API | la conexión con <el sistema> |
| refactor | limpieza interna, sin cambios visibles |
| el bug, el stack trace | el error que veían los usuarios |
| cache | guardamos el resultado para no recalcularlo cada vez |
| rollback | volvimos a la versión anterior |
| feature flag | lo activamos solo para un grupo primero |
| migración de base de datos | movimos los datos a su nuevo lugar |
| throughput | cuántas operaciones aguanta por minuto |
| queue, worker, async | el trabajo sigue en segundo plano, sin que nadie espere |
| timeout | se rinde después de esperar demasiado |
| uptime, SLA | cuánto tiempo estuvo disponible |
| technical debt | atajos que tomamos antes y ahora cuestan tiempo |

The test: read the line to someone who has never seen the product. If they can repeat it
back, it ships.

---

## Before writing

Four decisions. Each is a line in the output.

**1. Who could not do what.** A person, named by role — "el equipo de soporte", "un
cliente nuevo" — doing a real task. Not "the system".

**2. What they can do now.** One sentence, present tense.

**3. Why it matters.** The outcome in their terms: time, money, risk, or how many people
it affects. One number, if an honest one exists.

**4. What it does not do yet.** Stated, every time. Naming the limit is what makes the
rest believable, and it stops a roadmap question from becoming a roadmap commitment.

---

## The arc

Five beats. Shorter than a technical video — 45–90s, and under 60 if the change is small.

| Beat | Job | Share |
|------|-----|-------|
| **1. Antes** | The person hitting the old friction. Real product, real task. | ~20% |
| **2. El momento** | The new thing happening, once, at human speed. | ~25% |
| **3. Después** | The outcome, visible. The task is done. | ~20% |
| **4. Qué significa** | What this buys: time, cost, risk, reach. One number at most. | ~20% |
| **5. El límite** | What it still does not do, and who to ask next. | ~15% |

- **Frame 1 is the person's problem**, never a logo and never a title card.
- **No reveal beat.** Naming the architecture is a technical-video move. Here the product
  name lands once, on the end card.
- **One idea per frame.** If a frame needs two sentences to explain, it is two frames.
- **Never show the inside.** No "and behind the scenes…" frame. That is `script-qa`'s
  audience, not this one.

---

## Frame template

```markdown
## Frame 2 — Un cliente nuevo queda listo

- scene: pantalla de clientes, se pega la lista y la tabla se llena sola
- duration: 6s
- transition_in: cut
- status: outline
- reads: la lista entra (0.3-2.0s); el contador sube a 412 (2.0-4.2s); "listo" en pantalla (4.2-6.0s)
- sound: un clic al pegar; silencio mientras sube el contador
- voiceover: <only when voice: narrated>

Why this frame exists: this is the whole change in one gesture. Everything before it is
the problem; everything after is what it bought.
```

- **scene** — one line, present tense, what is literally visible, in Spanish.
- **status** — `outline`, `built`, `animated`.
- **The why-line is mandatory.** A frame that does not move the argument gets cut.

### Reads and sound

- One read per thing the viewer must register. Windows never overlap.
- **~0.4s per word + 0.5s** — slower than the technical skills. This audience is not
  scanning, and they will not scrub back.
- The last read of a frame gets at least 2s.
- Every visible action gets a sound or an explicit `silence`.

---

## Copy and number rules

- **Titles**: ≤6 words, plain words, no trailing period. No product-internal nouns.
- **One number, framed as experience.** Not "p99 bajó 40%" but "antes tardaba casi dos
  segundos; ahora, menos de medio". If no honest number exists, use none — an invented
  one is the fastest way to lose this room.
- **Percentages need a base.** "30% más rápido" is meaningless without the before.
- **Banned openers**: "Introducing", "Meet", "En el mundo actual".
- **Banned words**: unlock, seamless, supercharge, game-changer, revolucionario,
  innovador, potente, robusto, "sin esfuerzo", "lleva X al siguiente nivel".
- **No promises.** Never imply a date, a roadmap item, or a commitment the user did not
  make. Beat 5 says what it does not do, not when it will.
- **No blame.** The old way was not stupid. It was the right call with less information.

Palette and look: the locked tokens in `demo-video`. The accent lands on the outcome,
once per frame — same system as every other video, so these do not look like a different
company made them.

---

## Voice — usually yes

This is the one audience where narration earns its place: they may watch it in a meeting,
half-listening, without reading labels.

- **Register**: plain, warm, confident. A colleague explaining, not a marketer selling.
- **Pacing**: ~2.3 words/second — slower than technical. Sentences ≤12 words.
- **No echo**; the screen shows the outcome, the voice says what it means.
- **Never speak** a version string, a service name, a ticket id, or an acronym the
  audience has not heard in a meeting.

Every line passes `anti-slop` before `tts`. Spoken corporate Spanish is the single
fastest way to lose a stakeholder's attention, and a synthetic voice delivers a cliché
with total sincerity.

---

## Output order

1. **Assumptions** — one line: audience, duration, voice, anything inferred.
2. **Who could not do what**, what they can do now, why it matters, what it does not do.
3. **The frontmatter block** (`format`, `duration`, `message`, `audience`, `voice`).
4. **Every frame**, in the template above.
5. **Jargon check** — any technical term that survived, and what it was replaced with.
6. **`SCRIPT.md` and `tokens.json`** — when there is a voice.

---

## Final check

- [ ] No code, terminal, log, diagram, dashboard or internal name anywhere on screen.
- [ ] Every term in the swap table was swapped.
- [ ] A person who has never seen the product could repeat the message back.
- [ ] At most one number, with its before, and honestly sourced.
- [ ] Beat 5 exists: the limit is stated.
- [ ] No date, roadmap or commitment implied.
- [ ] Frame 1 is the person's problem, not a logo.
- [ ] One idea per frame.
- [ ] Reads windows do not overlap, budgeted at the slower rate.
- [ ] Total duration under 90s.

---

## Pipeline handoff

- `demo-video` renders it: assets, palette, the local HyperFrames plugin, the gates.
- `script-qa` is the same functionality for QA — preconditions, assertions, failure
  modes. **Never one video retitled for both audiences.** A stakeholder video that tries
  to double as a test plan does neither job, and the tell is a terminal on screen.
- `anti-slop` gates narration; `audio-clone` records it.

When the honest version of this video is unflattering — the change is small, the number
is weak, the limit is bigger than the win — say that to the user before scripting. That
is a product conversation, and it is cheaper now than after the render.
