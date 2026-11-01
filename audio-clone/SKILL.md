---
name: audio-clone
description: Generate speech from text with the user's own cloned voices on fish.audio. Use when the user asks to generate audio, narrate or voice a script, "haz el audio", "genera la voz", "lee esto con mi voz", "audio-clone", asks which voices or models they have, or hands over text to be spoken. Lists their My Voices models, lets them pick one, renders the text to an mp3, then offers the list again.
---

# Audio Clone

Pick one of the user's trained fish.audio voices, speak their text, hand back an mp3.

Two things decide whether a run works, and neither is the text:

> **The `model` header.** Without `model: s2.1-pro-free` this account gets
> `402 Insufficient API credit` — the API defaults to the paid `s2.1-pro`.
> **The output file.** `curl` writes the error body to `-o` on failure, so a failed run
> leaves a `.mp3` that is actually JSON. Always check what landed.

---

## Credentials

The token lives in `/home/codexmaker/skills-arsenal/.env` as **`MIRO_FISH_KEY`**.

```bash
cd /home/codexmaker/skills-arsenal && set -a && . ./.env && set +a
```

**Never print the key, echo it, paste it into a URL, or write it into a file that is not
`.env`.** Pass it only in the `Authorization: Bearer $MIRO_FISH_KEY` header. `.env`,
`.env.*`, `*.key` and `secrets.*` are all gitignored in this repo — keep it that way.

If `$MIRO_FISH_KEY` is empty, stop and say so. Do not prompt for a key in chat.

---

## API map

| Job | Call |
|---|---|
| List the user's voices | `GET https://api.fish.audio/model?self=true` |
| Generate speech | `POST https://api.fish.audio/v1/tts` |

Auth on both: `Authorization: Bearer $MIRO_FISH_KEY`. New keys: `https://fish.audio/app/api-keys`.

---

## The loop

1. **List** the user's voices (below). Number every row.
2. **Select** — they pick a number, a title, or say "the Spanish one".
3. **Text** — if they have not given it yet, ask for it. Never invent the text.
4. **Generate** — one call, the chosen `_id` as `reference_id`.
5. **Verify** the output is audio, not JSON. Report path, size and duration.
6. **Show the list again** and ask whether to generate another.

Step 6 is not optional. The list comes back every time without being asked for.

---

## Listing voices

```bash
cd /home/codexmaker/skills-arsenal && set -a && . ./.env && set +a
curl -sS "https://api.fish.audio/model?self=true&page_size=50" \
  -H "Authorization: Bearer $MIRO_FISH_KEY" \
  | python3 -I -c "
import json,sys
d=json.load(sys.stdin)
for m in d.get('items',[]):
    print(f\"{m['_id']}\t{m['state']}\t{m.get('languages')}\t{m['title']}\")"
```

`self=true` is what scopes it to **My Voices**. Without it you get the public catalogue.
The response is `{total, items, has_more, ...}`; each item's id field is **`_id`** (not `id`),
and that is what `reference_id` takes.

**Only `state: trained` models can speak.** A model still `training`, or `failed`, must be
shown as unavailable rather than offered as a choice.

Present it with the title first — that is what the user selects on:

| # | Voice | Language | Model ID |
|---|---|---|---|
| 1 | Anzu | es | `4cb5c3df…` |

Truncate the id in the table; hold the full one internally for step 4.

As of 2026-11-01 this account has three, all `trained` and all `type: tts`: **Feliz Jueves**
(es), **Anzu** (es), **Oguri Cap** (ja). Always re-list rather than trusting that line.

---

## Generating audio

```bash
cd /home/codexmaker/skills-arsenal && set -a && . ./.env && set +a
mkdir -p out/audio-clone
curl -sS -X POST "https://api.fish.audio/v1/tts" \
  -H "Authorization: Bearer $MIRO_FISH_KEY" \
  -H "Content-Type: application/json" \
  -H "model: s2.1-pro-free" \
  -d @- <<'JSON' \
  -o "out/audio-clone/<voice>-<slug>.mp3" -w "HTTP %{http_code} bytes=%{size_download}\n"
{"text":"...","reference_id":"<_id>","format":"mp3","mp3_bitrate":128,"language":"es-MX","normalize":true}
JSON
```

Build the JSON body with `python3 -c` or a heredoc, **never** by interpolating the text into
a shell string — an apostrophe or a `$` in the script will corrupt the request or the body.

### The fields that matter

| Field | Use |
|---|---|
| `text` | **Required.** The user's words, verbatim. |
| `reference_id` | The voice's `_id`. Omit it and you get a generic voice, not theirs. |
| `language` | BCP-47, matched to the voice: `es-MX` for the Spanish ones, `ja` for Oguri Cap. Drives number and date normalization. |
| `normalize` | Keep `true`. Turns `10x`, `p99`, `4.1` into spoken words. |
| `format` | `mp3` (default), or `wav` when it is going into an editor. |
| `mp3_bitrate` | `128` is right for voice. `192` only if asked. |
| `prosody.speed` | Only when the user asks for faster or slower. Default is correct. |
| `chunk_length` | Leave at `300`. |

### The `model` header

| Value | Cost | Use |
|---|---|---|
| `s2.1-pro-free` | free | **Default. Always start here.** |
| `s2.1-pro` | 15 USD / 1M UTF-8 bytes | Only if the user explicitly asks and has added API credit. |
| `drama-3` | 50 USD / 1M | Never without being asked. |

Omitting the header silently selects paid `s2.1-pro`, which **402s on this account**. API
credit is separate from a fish.audio subscription, so a paid plan does not make the paid
models work.

Spanish accented characters cost more than one UTF-8 byte each, so a paid run on Spanish
text costs more than the per-character arithmetic suggests. Say so before any paid call.

---

## Verifying and reporting

Never report success on an HTTP code alone — check the bytes that landed:

```bash
file "out/audio-clone/<name>.mp3"
```

| What `file` says | Meaning |
|---|---|
| `MPEG ADTS, layer III…` | Real audio. Report it. |
| `JSON text data` | **The run failed.** `cat` the file, read `message`, fix, re-run. |
| `empty` | Connection dropped mid-stream. Re-run. |

Then report four things and show the list again:

1. **Absolute path** under `/home/codexmaker/skills-arsenal/out/audio-clone/`.
2. **Duration** (`ffprobe -v error -show_entries format=duration -of default=nw=1 <file>`,
   when ffprobe is installed) and file size.
3. **Which voice and which model** produced it.
4. Surface the file so the user can play it — it is in a session folder, so it opens in the
   file pane.

Name files `<voice>-<slug>-<n>.mp3`. `out/` is gitignored, so nothing here is ever committed.
Expect roughly 1.5× the clip's own length in wall time: 2.7s of audio took 3.9s.

---

## Failure modes

| Symptom | Cause | Response |
|---|---|---|
| `402 Insufficient API credit` | `model` header missing or set to a paid model | Re-run with `model: s2.1-pro-free`. |
| `.mp3` is `JSON text data` | Error body written to `-o` | `cat` it, read `message`. Never hand the file over. |
| `401` | Bad or revoked key | Stop. The user reissues at fish.audio/app/api-keys. Do not retry. |
| `429` | Concurrency cap, 5 on the starter tier. No `Retry-After` header. | One request at a time, exponential backoff. Never parallelise. |
| Generic voice, not theirs | `reference_id` missing or wrong | Re-list and confirm the `_id`. |
| Model not in the list | It is `training` or `failed` | Nothing to do here; they finish it on fish.audio. |
| Mispronounced English terms | Latin voice reading English nouns | Expected. See below. |

---

## Spanish scripts and English technical terms

The content pipeline writes Spanish with English technical nouns on purpose — *"el context
window"*, *"hacer un rollback"*. A Spanish voice will read those with Spanish phonetics,
and `anti-slop` already flags the ones that mangle badly.

**Do not fix pronunciation by translating the term.** That breaks the register rule the whole
pipeline is built on. The options, in order: leave it, use `pronunciation_dictionary`, or
respell only in the TTS input while the script itself keeps the real term. Report which
terms came out wrong so `voice-card` can record them once instead of per script.

---

## Boundaries

- Do not write the text. The user supplies it, or it comes from `short-script` via
  `anti-slop`. Never generate audio from text you drafted without being asked.
- Do not create or train new voice models. This skill selects from models that already
  exist in the account. Cloning a real person's voice needs that person's consent, and
  that is not a thing to arrange through here.
- Do not use a paid model without an explicit go-ahead, and say the cost first.
- Do not print, log or commit the API key.
- One request at a time. No batch loops over a list of scripts without being asked.

---

## Pipeline handoff

`audio-clone` is the voice stage: `short-script` → `anti-slop` → **`audio-clone`** →
`caption-spec`. It takes a script that has already passed the anti-slop verdict; a script
that has not should go through that gate first, since paying to voice slop is the one
avoidable cost in the pipeline.

Pronunciation problems belong to `voice-card`, which owns the locked persona spec. When a
term comes out wrong, note it there rather than patching it per run.

API shape verified 2026-11-01 against `GET /model` and `POST /v1/tts`. Re-check the `model`
header values and pricing if a run starts 402-ing — the free tier is a promotion, not a
guarantee.
