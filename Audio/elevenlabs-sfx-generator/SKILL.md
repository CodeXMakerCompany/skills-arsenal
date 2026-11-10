---
name: elevenlabs-sfx-generator
description: Prompting, API parameters and post-processing for AI-generated game sound effects with ElevenLabs (or similar text-to-SFX models). Use when creating UI sounds, impacts, spells, weapons, creature sounds, ambiences or loops, and when preparing them for Unreal, Unity or Godot.
---

# AI Sound Effect Generation (ElevenLabs)

Good SFX come from a clear prompt, several takes, and disciplined cleanup. Generate variations, pick the best, edit, loudness-match, and name consistently. The model is the first draft of a sound designer's layer, not the final mix.

## Before you start

1. Define the sound's job: UI feedback, gameplay event, ambience, music sting. Job sets duration, loudness and whether it must loop.
2. List what you need as a sound set (e.g. card play, card draw, hit light/heavy, spell cast/impact, footsteps by surface). Generate sets for consistency.
3. Check the current ElevenLabs docs and model ids before scripting. The sound effects model versions change; the older `eleven_text_to_sound_v2` is documented as deprecated with a removal date, so read the current docs for the replacement id. Confirm pricing and license for commercial use on your plan.
4. API key goes in `.env`, never committed.

## 1. Prompt structure

`[Source/object] + [action] + [material/texture] + [acoustic character] + [layers/tail] + [duration]`

Rules:
- Describe sound, not the story. Use physical sources and verbs: "slams", "scrapes", "snaps", "sizzles".
- Name materials: stone, glass, wet flesh, brass, plastic, leather, ice.
- Add acoustic words: dry, close-mic, distant, reverberant, metallic ring, sub-bass thump, high transient, crisp, muffled.
- Specify the layers: transient (attack), body, tail. Example: "sharp click transient, short body, no reverb tail".
- State the exclusions that matter: "no music", "no voice", "no background noise", "dry, no reverb" (reverb is better added in engine).
- Keep prompts short (one to three clauses). Long prompts blur the result.

### Examples

| Use | Prompt |
|-----|--------|
| Card play | `Heavy stone tablet slapped onto a wooden table, short impact snap, low thud, dry, no reverb` |
| Card draw | `Single playing card slid across felt, soft whoosh, crisp edge, close mic` |
| Energy spell | `Rising electrical charge-up swell then sharp energy burst, high-frequency sizzle, short decay` |
| Explosion | `Large explosion, deep sub-bass boom, debris crackle, rolling tail` |
| Creature attack | `Insectoid jaw snap, wet crunch, fast sharp transient, high pitch hiss` |
| UI confirm | `Clean soft UI confirmation chime, two notes rising, glassy, very short, no reverb` |
| UI error | `Short low muted buzz, dull, subtle, single pulse` |
| Ambience loop | `Quiet cave ambience, distant water drips, faint low wind, no music, seamless loop` |

## 2. API parameters

Typical request (verify field names against current docs):

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Heavy stone tablet slapped onto a wooden table, short impact snap, dry",
    "duration_seconds": 1.2,
    "prompt_influence": 0.6
  }' --output card_play_01.mp3
```

| Parameter | Guidance |
|-----------|----------|
| `text` | The prompt. Keep it concise |
| `duration_seconds` | Between 0.5 and 30. If omitted the model guesses a length. Set it explicitly: 0.5 to 1.5 s for UI and impacts, 2 to 4 s for spells, longer for ambience |
| `prompt_influence` | Higher follows the text literally with less variation, lower gives freer results. Start around 0.5 to 0.75 for precise sounds, lower for exploratory ideas |
| `loop` | Available on newer models for seamless loops; verify before relying on it and still check the loop point |
| output format | Request the highest quality available, then convert to WAV |

Workflow tips:
- Generate 4 to 8 takes per sound (loop over seeds or repeated requests) and audition quickly.
- Request a slightly longer duration than needed and trim, do not squeeze a tail into a short duration.
- Keep a manifest: prompt, parameters, model id, date, chosen take, file name.

## 3. Post-processing

Do this for every chosen sound:

1. **Trim:** remove leading and trailing digital silence. Aim for a head under 10 ms so the transient lands on the trigger. Keep natural tails; do not cut a decay mid-tail.
2. **Fades:** apply 2 to 5 ms fade in/out on one-shots to avoid clicks.
3. **Clean:** high-pass to remove rumble below ~30 Hz for non-bass sounds; denoise only if audible.
4. **Loudness:** normalize by role, not blindly to one value.

| Category | Target |
|----------|--------|
| UI sounds | Peak -6 to -3 dBFS, short loudness |
| Impacts / hits | Peak -3 dBFS |
| Ambience / loops | -24 to -18 LUFS integrated, peak below -3 dBFS |
| Music stingers | Match the music bus level |

5. **Format:** deliver uncompressed `48 kHz` or `44.1 kHz` 16-bit (or 24-bit) PCM WAV mono for 3D positional sounds, stereo for UI, ambience and music. Use the project's sample rate (Unreal and Unity default to 48 kHz) to avoid resample at runtime.
6. **Loops:** crossfade the tail into the head, check at zero crossings, verify by looping 10 times in an editor.

### Commands (FFmpeg + SoX)

```bash
# Convert to 48 kHz mono 16-bit WAV
ffmpeg -i in.mp3 -ar 48000 -ac 1 -sample_fmt s16 raw.wav

# Trim silence at head and tail, peak normalize to -3 dB, tiny fades
sox raw.wav out.wav silence 1 0.005 1% reverse silence 1 0.005 1% reverse \
    fade 0.003 0 0.005 norm -3

# Measure loudness (LUFS) for ambience
ffmpeg -i out.wav -af loudnorm=I=-20:TP=-3:LRA=11:print_format=summary -f null -
```

Check the result by ear and with a waveform; thresholds that are too aggressive clip quiet tails.

## 4. Building a sound that sounds designed

- **Layer:** combine 2 to 4 generated sounds (impact + tail + texture + sub). Generate each layer with its own prompt.
- **Vary:** produce 3 to 6 variations of anything that repeats (footsteps, hits, card plays). Randomize in engine with pitch (+/- 5 to 10%) and volume (+/- 2 dB).
- **Pitch and time:** pitch down for weight, up for size reduction. Small pitch shifts hide the "AI" signature.
- **EQ and compression:** carve space per category (UI mids/highs, impacts low-mids, ambience wide). Use a limiter on the master, not on individual one-shots.
- **Reverb in engine:** keep sources dry and use the game's reverb/submix so sounds fit the space.
- **Consistency:** keep one character per category (all UI glassy, all combat punchy). Reuse prompt prefixes.

## 5. Engine hand-off

- File names: `SFX_<Category>_<Name>_<NN>.wav` (e.g. `SFX_Card_Play_03.wav`).
- Import with the right settings: compression format per platform, streaming off for short sounds, looping flag for loops.
- Group variations into a Sound Cue / MetaSound random node (Unreal), Audio Random Container (Unity), or random stream (Godot).
- Set concurrency limits and attenuation per category (see `ue-niagara-audio-trigger` for the Unreal orchestration).
- Test in context with music and voice playing. Adjust levels in the mix, not by re-exporting.

## 6. Quality and legal

- Do not request sounds "in the style of" a named franchise or recognizable copyrighted audio.
- Store provenance (service, model, plan, date) for each file in case of a rights audit.
- Do not ship raw generated audio. Always listen for artifacts: warbles, hiss, abrupt endings, accidental voices or music.

## Failure patterns

| Symptom | Fix |
|---------|-----|
| Result is vague or muddy | Shorter prompt, concrete source and material, raise `prompt_influence` |
| Contains music or voices | Add "no music, no voice", lower duration |
| Click at start or end | Fades, trim at zero crossing |
| Too much reverb | Say "dry, close-mic, no reverb", add reverb in engine |
| Loops audibly | Crossfade the join, or generate a longer take and cut a stable middle |
| Feels samey in game | More variations, pitch/volume randomization, layer differently |
| Too quiet/loud in game | Match loudness by category, then mix on buses |
