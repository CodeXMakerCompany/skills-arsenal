---
name: script-qa
description: Write the storyboard and narration for a video that shows QA how to test a functionality — preconditions, each step with its expected result, how failure looks, edge cases and what is out of scope. Covers new features, bug-fix verification, regression areas and boundary behaviour. Use when the user asks for a QA walkthrough, a test walkthrough video, "guion para QA", "cómo prueba QA esto", "script de pruebas", "video de testing", or hands over a feature or a fixed bug to be verified.
---

# Script — QA

A QA walkthrough is a test plan someone can watch. Every frame is one step, and every
step carries the thing a test plan cannot leave out: **what you should see, and what it
looks like when it fails.**

A video that shows the happy path and stops is a demo, not a test. QA already knows how
to click. What they do not know is which observable makes this a pass.

> "Frame 2: the user uploads the CSV. Frame 3: the users appear."
> → unverifiable. Appear how many? How fast? What if two rows collide?
>
> "Frame 2: upload `fixtures/400-users.csv` as `admin@acme.test`.
>  Expected: banner reads `400 imported, 0 skipped`, table count goes 12 → 412.
>  Fails as: banner reads a lower count, or the count does not change — row 187 has a
>  duplicate email, and that is the case under test."
> → a step QA can execute and judge.

---

## The hard rule

**The output is always a script, and every step frame has an assertion.** No frame may
say only what to do. Each one states what should be observed and how failure presents.

If the request is thin, write the script with assumptions marked in one line at the top.
A script with marked assumptions is reviewable; a question is not.

If a step has no observable result, it is not a test step — it is setup. Move it into
preconditions.

---

## What this produces

| File | When | Holds |
|------|------|-------|
| `STORYBOARD.md` | always | Frontmatter, preconditions, then ordered step frames |
| `SCRIPT.md` | only with a voice | The locked narration, verbatim |
| `tokens.json` | only with TTS | Display versus spoken text |

**Default to no voice.** On-screen labels carry the step, the expected result and the
failure mode better than narration does — QA pauses and scrubs, and text survives that.
Add a voice only when asked.

---

## Before writing

Four decisions. Each is a line in the output.

**1. The one behaviour under test.** One sentence. If it takes two, it is two videos —
and two test cases.

**2. The environment and the data**, exactly. Build or version, URL or binary, role and
account, feature flags, and the named fixture. "A user" is not test data;
`fixtures/400-users.csv` is. Anything a QA cannot recreate from the script is a defect
in the script.

**3. The oracle.** The single unambiguous signal that this passed. A count, a banner
string, a status code, a row in a table, a state flip. If the oracle is "looks right",
there is no test yet — go find the number.

**4. What is out of scope.** State it. An unstated boundary gets tested anyway, fails,
and comes back as a bug that was never a bug.

---

## Pick the arc by kind

| Kind | Arc | Where the time goes |
|------|-----|---------------------|
| **feature** | preconditions → happy path, one step per frame → the oracle → edge cases → out of scope | the steps (~50%) |
| **bugfix** | the bug as filed → repro on the broken build → the fix landed → same repro, clean → regression area | the repro (~35%) |
| **regression** | what changed underneath → the paths to re-walk → what must still hold → sign-off criteria | the paths (~50%) |
| **edge-case** | the boundary → behaviour just inside → just outside → what the system actually does → whether that is correct | inside/outside (~45%) |

Rules across all four:

- **Frame 1 is the precondition state**, not a title card. QA has to see the starting
  point to know they reproduced it.
- **One action per frame.** Two actions in a frame means a failure cannot be localised.
- **The repro comes before the fix**, always, in `bugfix`. A video that opens on the fix
  gives QA nothing to compare against.
- **Negative cases are not optional.** At least one frame shows the thing failing
  correctly — rejected input, a permission denial, a timeout.
- **No sped-up steps without a label.** QA will time it. A sped clip that hides a 9-second
  wait turns into a performance bug report.

---

## Frame template

```markdown
## Step 3 — Import rejects the duplicate row

- preconditions: logged in as admin@acme.test, 12 users in the table
- action: upload fixtures/400-users.csv via Settings → Import
- expected: banner "400 imported, 0 skipped"; table count 12 → 412; row 187 flagged amber
- fails as: count below 412, no amber flag, or a 500 — row 187 is a duplicate email
- duration: 7s
- transition_in: cut
- status: outline
- reads: banner text lands (0.3-2.1s); count ticks 12 → 412 (2.1-4.4s); amber flag on row 187 (4.4-7.0s)
- sound: one click on upload; silence while the count ticks

Why this frame exists: this is the only step where the duplicate-handling path runs.
Everything before it is setup; everything after assumes it passed.
```

- **expected** and **fails as** are both mandatory. A frame missing either is incomplete.
- **preconditions** repeats per frame when the state changed in the frame before.
- **status** — `outline`, `built`, `animated`. Everything starts `outline`.
- **The why-line names what this step proves.** No answer means the step is setup.

### Reads windows

One read per thing QA must register, with a window. Windows **never overlap**.

Budget **~0.3s per word + 0.5s**, last read of a frame at least **2s**. Then add for
scanning: a banner string, a count change or a table row needs **3s minimum**, and a
stack trace or a diff gets its own frame.

The expected result always gets its own read. It is the point of the frame.

### Sound

Every visible action gets a sound or an explicit `silence`. Silence before the oracle
lands is the cheapest emphasis available — use it where the number appears.

---

## Preconditions block

Opens `STORYBOARD.md`, before frame 1. QA reads this and nothing else to set up.

```markdown
## Preconditions

- build: <version or commit-free build label>
- url: <environment>
- account: <role and login used>
- flags: <feature flags and their state>
- data: <named fixtures, and whether seeded or production-like>
- out of scope: <what this video does not cover>
```

Seeded data is labeled seeded, on screen, in any frame that carries the oracle. A pass
proven on fabricated data that nobody flagged is how a bug reaches production with a
green tick next to it.

---

## Copy rules

- **Titles**: ≤6 words, no trailing period. Name the step's behaviour, not "Step 3".
- **Use the product's exact strings.** Never paraphrase a banner, an error or a button
  label — QA matches on text.
- **Expected results are observable and numeric where possible.** "Faster" is not an
  assertion; "under 2s, was 9s" is.
- **No hedging.** "Should probably show" means the behaviour is undefined. Say so and
  flag it as a question for the developer, in its own line.
- **Never on screen**: commit hashes, PR numbers, internal ticket ids. QA cannot act on
  them and they date the video.
- **Banned words**: seamless, simply, just, obviously, effortless. If a step is obvious,
  cut the frame.

Output language: Spanish, technical terms left in English — `el build`, `un rollback`,
`el endpoint`, `los flags`. This file stays in English.

---

## Voice — only when asked

- **Register**: flat and procedural. This is not a pitch.
- **Pacing**: one step per breath. Sentences ≤14 words. ~2.5 words/second.
- **No echo.** The screen shows the expected result; the voice says why that result
  proves the behaviour.
- **Commands verbatim**, and shown being typed in the same frame.

Every line passes `anti-slop` before `tts`.

### Pronunciation tokens — only with TTS

```json
{ "lines": [ { "id": "l1", "tokens": ["Sube", "el", {"display": "CSV", "spoken": "ce ese ve"}] } ] }
```

- One line is one caption phrase, ≤~40 characters of display text.
- Initialisms: space the letters — `C S V`, `A P I`.
- Acronyms read as words: respell phonetically.
- Spell out numbers and URLs; `dot` for the separator.
- Keep one display → spoken lexicon across videos so a term never shifts pronunciation.

---

## Output order

1. **Assumptions** — one line: build, environment, voice or none, anything inferred.
2. **The behaviour under test**, the oracle, and what is out of scope.
3. **The frontmatter block.**
4. **The preconditions block.**
5. **Every step frame**, in the template above.
6. **Open questions** — undefined behaviour found while scripting, as a list for the
   developer. This list is often the most valuable output of the whole run.
7. **`SCRIPT.md` and `tokens.json`** — only when there is a voice.

---

## Final check

Any failure is a rewrite, not a note.

- [ ] Every step frame has both `expected` and `fails as`.
- [ ] The oracle is observable and appears in a frame of its own.
- [ ] Preconditions are complete enough to recreate from the script alone.
- [ ] Named fixtures, not "a user"; seeded data labeled on screen.
- [ ] At least one negative or rejected case.
- [ ] One action per frame.
- [ ] Reads windows do not overlap; scan-heavy frames get 3s+.
- [ ] Out of scope is stated.
- [ ] Open questions listed rather than guessed at.
- [ ] Total duration inside the requested range without padding.

---

## Pipeline handoff

This skill stops at the script. It does not build compositions or render.

- `demo-video` owns everything after approval: assets, the locked palette, the local
  HyperFrames plugin and the render gates. It calls this skill for the script step.
- `script-stakeholder` is the same functionality for a non-technical audience. Different
  video, different script — never one video retitled for both.
- `anti-slop` gates narration before `tts`; `audio-clone` records it.

A script that cannot be shot — the oracle only exists in a dashboard nobody can share,
the fixture cannot be recreated — comes back here for a rewrite. Production never invents
a substitute observable.
