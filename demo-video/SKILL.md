---
name: demo-video
description: Plan and render a demo video that explains how one functionality works — the problem it solves, the move that solves it, and the proof. Always produces an approved scene script with labels before any render, then drives the HyperFrames CLI. Use when the user asks for a demo video, a feature walkthrough, "graba un demo", "haz un video de esta funcionalidad", "demo de este feature", "muestra cómo funciona esto", a release clip, or hands over a working feature to be shown.
---

# Demo Video

A demo video is an argument, not a tour. It earns attention by showing a **problem**,
then the **one move** that kills it.

The feature is never the content. The broken state is the content; the feature is the
punchline.

> "Here's our new bulk-import screen. You click here, then here, then Save."
> → a tour. Nobody finishes it.
>
> "Onboarding 400 users took an afternoon of CSV surgery. Now it's one paste.
> Here's the 400 landing in nine seconds."
> → a demo. The feature never needed introducing.

If the only possible narration is *"and then you click…"*, **there is no video yet.**
Go back to Phase 0.

---

## The hard rule

**No render without an approved scene script.** Always.

Every run produces the scene script first and stops for the user's approval. Not a
summary of it, not a description of what it would contain — the table from
[Scene script](#scene-script), filled in, on screen, waiting.

This holds when the user says "just make it", when the feature is small, and when a
previous video in the same session was already approved. A render is minutes of
compute and a file someone will publish; the script is the only cheap place to be
wrong. If the user insists on skipping it, produce it anyway and render in the same
turn — they can ignore it, but it has to exist.

---

## Phase 0 — Understand the functionality (blocking)

Five answers. Missing any of them means the video cannot be scripted, so ask for the
missing ones and stop.

| # | Question | Why the video dies without it |
|---|----------|-------------------------------|
| 1 | **What is tedious, slow, or impossible today?** | This is Scene 1. No problem, no video. |
| 2 | **Who hits it, and how often?** | Decides whether the stakes beat is a number or a shrug. |
| 3 | **What is the single action that fixes it?** | One action. Two means two videos. |
| 4 | **What is the observable proof?** | A count, a timer, a diff, a state flip. Something the camera can see. |
| 5 | **Where does it run?** | A URL for `capture`, a local app, or a mockup. Decides production route. |

Then ask the assets question below — before scripting, not during.

Answer 3 is the test. If the fix is "configure these six things, then it works", the
demo is not ready — say so, and offer to demo the one sub-step that *is* a single move.

Also establish, once: **who watches this.** An internal release clip, a sales demo, and
a short-form post for the channel have different lengths and different endings. Default
to the channel conventions in `topic-miner` when the user does not say.

---

## Assets — ask, never assume

Once the five answers are in, ask one question: **does this video need material the
agent cannot generate?** Logos, brand fonts, product screenshots, recorded footage,
music, an avatar, a customer's data.

Then wait. Three outcomes:

- **No** — proceed. Every frame is built from HTML, registry blocks and `capture <url>`.
  Create nothing.
- **Yes** — create the folder described below, tell the user the exact path, and wait for
  them to fill it before scripting the affected scenes.
- **No answer** — treat it as no. Never invent the folder on a guess.

Only on an explicit yes does the folder get created.

### The folder

Named after the video, with `-assets` at the end, beside the project `init` created:

```
demo-bulk-import/              # the HyperFrames project
bulk-import-demo-assets/       # <video-title-slug>-assets
```

Inside it, every file is named so the relation to the script is readable without asking
again — scene number, then what it is:

```
bulk-import-demo-assets/
  01-estado-roto-csv-surgery.mp4
  01-estado-roto-spreadsheet.png
  03-movimiento-paste-action.mp4
  04-prueba-400-users-landed.png
  brand-logo.svg                 # no scene prefix: used across scenes
  brand-font.woff2
  REFERENCES.md                  # one line per file: what it is, where it came from
```

- **Scene prefix binds the asset to the row.** `01-` is scene 1. An asset used
  everywhere takes no prefix.
- **`REFERENCES.md` carries provenance** — source, licence, and whether it is real
  production data or seeded. A proof frame built on seeded data must be labeled on
  screen, and this file is where that gets caught.
- The script names the file in `En pantalla`, so the mapping is explicit rather than
  inferred at render time.
- **A missing asset stops the render.** Say which file and which scene; never substitute
  a placeholder and render anyway — that is how a fake proof ships.
- Assets never go in this repo. They live with the video project.

---

## Narrative spine

Five beats, in this order. This is the structure every demo that works converges on,
and the order is the load-bearing part — a feature shown before its problem reads as a
feature list.

| Beat | Job | Budget |
|------|-----|--------|
| **1. El estado roto** | Show the pain happening. Real UI, real friction, no narration of the obvious. | 10–15% |
| **2. El costo** | What it costs: minutes, errors, the 3am page. One number beats one adjective. | 10–15% |
| **3. El movimiento** | The single action. Uninterrupted, at real speed or honestly sped up with a label. | 30–40% |
| **4. La prueba** | The observable result. The thing a skeptic would demand. | 20–25% |
| **5. El límite** | What it still does not do, and the next step. Builds more trust than a CTA. | 10–15% |

Rules that hold across all five:

- **The screen carries the what; the voice carries the why.** Never narrate what is
  visibly happening. If the voiceover says "now I click Import", cut that line — the
  cursor already said it.
- **One functionality per video.** A second feature is a second video. Say so rather
  than widening the script.
- **Never fake the proof.** No sped-up clip presented as real time without a label, no
  seeded data pretending to be production, no cut that hides a loading state. A demo
  caught lying costs more than the feature earned.
- **Beat 1 starts at frame 1.** No logo, no "hi everyone", no title card before the pain.

---

## Scene script

The deliverable of every run — and it is not written here. **A script skill owns the
format, chosen by audience:**

| Audience | Skill | Produces |
|----------|-------|----------|
| QA, engineers verifying behaviour | `script-qa` | preconditions, steps with expected results and failure modes |
| Product owners, stakeholders, clients | `script-stakeholder` | before / the moment / after / what it means / the limit, no technical detail |

Pick one and say which. **Never one video for both** — a stakeholder video carrying a
terminal does neither job. Two audiences means two scripts and two renders.

Invoke it, get back `STORYBOARD.md` (plus `SCRIPT.md` and `tokens.json` when there is a
voice), and bring that here for approval. Pass it what Phase 0 established: the kind,
the one thing, the real artifact or oracle, the destination and its duration target, and
whether assets exist.

What this skill adds on top of the returned storyboard, before asking for approval:

- **Label per frame** — the exact type from the taxonomy below, or `—` for none. Most
  frames are `—`. Name the token when it is not the default `--ink` on `--surface`.
- **Asset per frame** — the filename from the `-assets` folder, when the frame uses
  supplied material: `01-estado-roto-csv-surgery.mp4`.
- **El presupuesto** — total seconds against the destination target, and total voiceover
  words against the speaking rate.
- **Riesgos** — anything that will be hard to capture, look fake, or be legally awkward.

Then stop and ask for approval. Never render on an unapproved storyboard.

### Duration budget

| Destination | Target | Voiceover ceiling |
|-------------|--------|-------------------|
| Short-form vertical (the channel) | 30–60s | ~2.5 words/second |
| Release clip / changelog | 60–90s | ~2.5 words/second |
| Sales or onboarding demo | 90–180s | ~2.3 words/second |

Over the word ceiling means the voice will be rushed or the video will run long. Cut
words, never speed up the read.

---

## Label taxonomy — when to use each

A label is a confession that the frame is not self-explanatory. Prefer fixing the frame.
When the frame genuinely cannot carry it, pick the lightest thing that works.

| Label | Use when | Do not use when | Registry starting point |
|-------|----------|-----------------|-------------------------|
| **Captions** | Always. Assume muted autoplay. | Never skip them. | `caption-clip-wipe`, `caption-editorial-emphasis` |
| **Title card** | Marking a beat boundary in a 90s+ video. | Before beat 1, or in a 30s clip — it eats the hook. | `canopy-part-title`, `code-slice-hero` |
| **Lower third** | Naming the environment, version, or person once. | Repeating it every scene. | `lt-clean-bar` |
| **Callout / arrow** | A small state change the eye would miss. | The change is already the only thing moving. | `catalog --query "annotation callout pointing at ui element"` |
| **Highlight / spotlight** | One element matters among many on a busy screen. | Full-screen changes. | `catalog --query "spotlight dim surrounding ui"` |
| **Zoom** | UI detail or text illegible at the target aspect ratio. | It already reads at 9:16. Gratuitous zoom reads as padding. | `cinematic-zoom` |
| **Cursor emphasis** | The action *is* a click or a drag — beat 3. | Passive playback or output scrolling by. | `agent-cursor` |
| **Speed label** | Any clip not at real time. Mandatory, not optional. | — | hand-build; keep it on screen for the whole sped segment |
| **Before/after wipe** | The comparison itself is the proof. | States are sequential rather than parallel. | `before-after-wipe` |
| **Code diff** | The change being demoed is code. | The change is in the UI. | `code-diff` |
| **Browser / device frame** | Establishing that this is a real running app. | Abstract or diagrammatic beats. | `browser-device-stage`, `app-showcase` |
| **Chart** | The proof is a number over time or a comparison. | The proof is a single value — put it in a caption. | `data-chart`, `bar-chart-race` |

Two limits:

- **At most one label type on screen at a time.** A callout plus a highlight plus a zoom
  is not emphasis, it is noise.
- **Legibility at 9:16 is a hard gate, not a preference.** Vertical destination means code
  and UI text must survive a phone screen. If a frame needs a zoom to be readable, the
  zoom is part of the script, not a fix at render time. Rule of thumb: code at 16px or
  larger in the rendered frame, at most ~12 lines visible, and never a full-width IDE
  screenshot shrunk to fit.

---

---

## Look — black and pink neon, homologated

One palette for every demo video. It is not re-picked per video: paste these tokens into
each project unchanged, so two clips a month apart still read as the same channel.

```css
:root {
  --bg:        #0A0A0F;  /* near-black, not #000 — pure black smears on OLED */
  --surface:   #14141C;  /* cards, browser frames, code plates */
  --line:      #2A2A38;  /* hairlines, borders, grid */
  --ink:       #F2F2F7;  /* information: body, code, numbers, captions */
  --ink-muted: #9A9AAD;  /* secondary labels, timestamps, the old state */
  --neon:      #FF2D95;  /* accent: the one thing that matters this frame */
  --neon-hi:   #FF6FB5;  /* cursor, motion trails, active state */
  --neon-wash: rgba(255, 45, 149, 0.18);  /* highlight fills, spotlight tint */
}
```

The discipline that keeps it legible — the palette serves the information, never the
reverse:

- **Information is near-white; pink is punctuation.** `--ink` carries every fact: body
  copy, code, the number in beat 4. `--neon` marks *one* element per frame. Saturated
  pink text on black halates at phone size and will fail the contrast audit in
  `check --json` — take its `suggestedColor` rather than arguing with it.
- **Glow on accents only, never on text that carries information.** A neon underline, a
  cursor trail, a border pulse: yes. Glowing code or a glowing paragraph: no.
- **One accent per frame.** If two things are pink, nothing is.
- **No second hue.** No green-and-red success/error pair. When a beat needs two states —
  a diff, a before/after — the new state is `--neon` and the old is `--ink-muted`.
- **Futuristic comes from motion and restraint**, not decoration. Scanlines, grain and
  chromatic aberration are allowed at low opacity over `--surface`, never over code or a
  number.
- **Captions are `--ink` on a `--surface` plate.** Never pink captions, never captions
  straight onto footage.

Registry blocks ship their own colours. Point their colour variables at these tokens when
mounting — `add --vars '{...}'`, or `data-variable-values` on the host — instead of
accepting a block's default look. A block that cannot be recoloured is the wrong block.

## Production — the local HyperFrames plugin

Drive the HyperFrames plugin **already installed on this machine**. Never install it,
never upgrade it, never substitute another copy or version.

### Step 1 — Locate `<PLUGIN_ROOT>`, or reject

Two levels above the loaded `hyperframes` SKILL.md sits a directory holding `plugin.json`
or `.claude-plugin/plugin.json` identifying `hyperframes`. That directory is
`<PLUGIN_ROOT>`; it resolves under `~/.claude/plugins/cache/hyperframes/hyperframes/<version>/`.
Confirm it before anything else:

```bash
ls "$PLUGIN_ROOT/plugin.json" "$PLUGIN_ROOT/skills/hyperframes/scripts/plugin-cli.mjs"
```

**Not found → stop and reject the build.** Report that the plugin is absent, name the
paths that were checked, and hand the user the line to run themselves:

```bash
claude plugin install hyperframes --marketplace heygen-com/hyperframes -y
```

Then end the turn. Do not install it, do not `npm i` or `bun install`, do not build the
bundled monorepo, do not fall back to `npx hyperframes`, and do not hand-roll ffmpeg to
get around it. Installing a renderer is the user's call.

The bundled `packages/cli` is **source only** — no `dist/`, no `node_modules`, fifteen-plus
runtime dependencies. Pointing `node` at it directly will fail. Use the launcher below.

### Step 2 — Every command goes through the launcher

```bash
node "<PLUGIN_ROOT>/skills/hyperframes/scripts/plugin-cli.mjs" <command> <args...>
```

Never bare `hyperframes`, never `npx hyperframes`. The launcher pins the CLI to the
version this plugin shipped with, suppresses update notices, and disables standalone
skill refreshes — including during `init`. `npx` resolves whatever npm calls latest and
runs it against these skills; the two drift apart.

For readability, define it once in the project directory:

```bash
export PLUGIN_ROOT=<the path confirmed in step 1>
hf() { node "$PLUGIN_ROOT/skills/hyperframes/scripts/plugin-cli.mjs" "$@"; }
```

Four rules that come with the launcher:

- **Run in the user's project directory, never in the plugin directory.** Treat the
  plugin directory as read-only; outputs and scratch work live in the project.
- **A download failure is an error, not permission to use latest.** The first call may
  fetch that exact pinned version through npm. If it fails, report it and stop.
- **Never run** `skills update`, `skills check`, or `npx skills add`. The plugin manager
  owns updates, and a plugin is never updated mid-video-task.
- **Bundled Node helpers take the same launcher**, as `--script <absolute-path> <args...>`.
  Pass this convention to any delegated agent, or it will fall back to global skills.

It still needs **Node 22+ and FFmpeg** on the machine. Check both before promising a
render; neither is something to install unasked either — report and stop.

### Step 3 — the loop

Read `/hyperframes` first for the render contract, then:

```bash
hf init demo-<feature>          # blank project
hf capture <url>                # only when demoing a live web app
```

Find a block per beat rather than hand-building. Query in **English** even though the
video is Spanish — the catalog is indexed in English:

```bash
hf catalog --query "<what the beat should do>" --json
hf add <name> --json
```

Then the write/check/see loop, in this order, every time:

```bash
hf lint                         # after the first pass and each structural change
hf check --json                 # the gate: fix every error
hf snapshot                     # read the PNGs — this is how you see the video
hf preview --background         # hand the person the URL and wait
hf render --quality draft -o out.mp4
```

- `check --json` is a gate, not advice. While a lint error stands, the layout and
  contrast audits do not run, and `0 samples` means nothing was checked.
- **Look at the snapshots.** Passing checks is not seeing the video. Snapshot a midpoint
  of every scene; unstyled or missing content is a mount defect, not a style problem.
- Qualities: `draft` while iterating, `looks` for review, `delivery` for the final cut.
- Narration: `hf tts`, or `audio-clone` for the user's own cloned voice. Write the lines
  first, gate them through `anti-slop`, then render audio.
- Wrap edits in `hf history begin --who <you> --label "<plan>"` and `hf history end`, so
  a bad pass is `hf history undo` rather than hand-editing back.

---

## Render gates

Do not hand over a file until every gate passes:

1. `check --json` clean — zero errors, non-zero samples.
2. Every scene snapshotted and actually looked at.
3. Rendered duration matches the root `data-duration` (`ffprobe` it), and the file is non-empty.
4. Captions present and legible at the target aspect ratio.
5. Palette conformance: no hue outside the token block, one accent per frame, no glow on
   any text carrying information.
6. Every asset the script names exists in the `-assets` folder, and anything seeded rather
   than real is labeled on screen.
7. Every command ran through `plugin-cli.mjs` from the located `<PLUGIN_ROOT>` — no bare
   or `npx`-resolved CLI anywhere in the transcript.

A failure at 3 usually means a mount duration, not a render bug. Fix the composition.

---

## Reject filters

Refuse to script, and say why, when:

- There is no problem — the request is a UI tour. Offer to find the problem instead.
- The "one move" is six steps. Offer the one sub-step that is a single move.
- The proof cannot be shown on screen, only asserted.
- The functionality does not work yet. A demo of a mockup is a mockup, and it must be
  labeled as one on screen.
- The honest version of the video would embarrass the feature. Say that out loud; it is
  product feedback, not a scripting problem.
- The HyperFrames plugin is not installed on the machine. Reject the build, name the
  paths checked, hand over the install line, and stop — never install it to proceed.

---

## Output

1. **Lo que entendí** — the five Phase 0 answers, with assumptions marked.
2. **La tensión** — before and after, one sentence.
3. **El guion de escenas** — the table, complete.
4. **El presupuesto** — seconds and words against the target.
5. **Los labels** — which types this script uses and why, one line each.
   **Los assets** — the folder path and what is still missing, when the answer was yes.
6. **El plan de producción** — the exact commands, in order, for this video.
7. **Riesgos** — what will be hard to capture or will look fake.

Then: **stop and ask for approval.** Render only after a yes.

---

## Pipeline handoff

A demo video is the end of the pipeline, not a stage in it. It consumes:

- `script-qa` / `script-stakeholder` — the storyboard and narration, by audience. This
  skill never writes frames inline.
- `topic-miner` — for the angle and audience when the demo is content rather than internal.
- `anti-slop` — every voiceover line passes its gate before `tts`. Spoken Spanish slop is
  worse than written: the synthetic voice has no irony.
- `audio-clone` — the user's own cloned voice, when the demo is for the channel.
- `hyperframes` plugin — the render contract, the registry, and the CLI.

When a demo surfaces something genuinely surprising about the feature — a limit, a
number nobody publishes, a workaround that shouldn't be necessary — hand it back to
`topic-miner` as a topic with the *El recibo* or *Qué NO arregla* angle. The demo already
produced the proof.
