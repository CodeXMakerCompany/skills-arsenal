---
name: bark-edge-tts-dialogue
description: Text-to-speech workflows for game character dialogue using Bark (expressive, local), Coqui XTTS (voice cloning) and Edge-TTS (fast, cloud). Use when generating character voice lines, barks, narration, battle callouts or placeholder VO, including line writing, tag usage, voice profiles, batching, caching and loudness.
---

# Character Dialogue with Bark & Edge-TTS

Pick the engine by job, write lines for the ear, generate in batches, cache, and post-process. TTS is great for prototypes, barks and reactive lines. For hero lines, decide early whether to replace with human VO.

## Before you start

1. Choose the engine:

| Engine | Strength | Weakness | Fit |
|--------|----------|----------|-----|
| Bark (local) | Expressive: laughs, sighs, hesitations, even background noise | Slow, non-deterministic, ~13 s limit per generation, 24 kHz output, can hallucinate | Character flavor, short barks, pre-generated offline |
| Edge-TTS | Fast, many languages and voices, streaming, controllable rate/pitch/volume | No emotion tags, cloud service, unofficial access to Microsoft's online voices | Prototyping, narration, UI voice, subtitles with timing |
| Coqui XTTS | Voice cloning from a short sample, multilingual | Model license is non-commercial (Coqui Public Model License), heavy | Internal prototypes, research |
| Hosted TTS (ElevenLabs, Azure, etc.) | Highest quality, stable | Cost, network, license per plan | Shipping VO |

2. Licensing: Bark is MIT. Check XTTS model license before commercial use. Edge-TTS relies on a Microsoft service that is not an official API product: do not depend on it for a shipping game without checking terms. Never clone a real person's voice without written consent.
3. Plan where generation happens. Pre-generate at build time and ship audio files whenever possible; runtime generation adds latency, cost and failure modes.

## 1. Writing lines for TTS

- Short lines: 3 to 12 words for barks, up to 2 short sentences for dialogue.
- Spell numbers and symbols as spoken ("two hundred", "percent").
- Use punctuation as direction: comma = small pause, period = stop, ellipsis = hesitation, question mark = rising pitch, exclamation = energy.
- Spell unusual names phonetically if mispronounced ("Zy-gar" or add hyphens).
- Write each line with intent: who speaks, to whom, mood, context. Keep a line sheet with ID, speaker, text, mood, trigger.
- Provide 3 to 5 variations of any frequent bark to avoid repetition.

## 2. Bark syntax

Supported non-speech tokens (use sparingly; results vary): `[laughter]`, `[laughs]`, `[sighs]`, `[gasps]`, `[clears throat]`, `[music]`, and `...` or `-` for hesitation. `♪` marks singing. CAPITALS add emphasis. `[MAN]` / `[WOMAN]` hint speaker gender.

```python
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import numpy as np

preload_models()

def line(text: str, speaker: str = "v2/en_speaker_6") -> np.ndarray:
    # history_prompt selects a voice preset; keep it fixed per character
    return generate_audio(text, history_prompt=speaker)

audio = line("[sighs] Target locked... initiating collapse.")
write_wav("kaelen_target_locked_01.wav", SAMPLE_RATE, audio)  # 24 kHz
```

Tips:
- Bark has no `[fast]`, `[deep]` or similar style tags. Style comes from the speaker preset, punctuation and wording. Do not invent tags; unknown bracket text may be spoken aloud.
- Keep each generation under ~13 seconds. Split long text by sentence and join with short silence.
- Regenerate until acceptable; generate 3 to 5 takes and pick. Set seeds for repeatability where supported.
- Fix a voice per character with a preset (or a saved history prompt) so the voice stays consistent across lines.
- Resample 24 kHz output to your project rate (48 kHz) in post.
- Needs a GPU for reasonable speed; generate offline in batches.

## 3. Edge-TTS usage

```bash
pip install edge-tts
edge-tts --list-voices | grep en-US
edge-tts --voice en-US-GuyNeural --rate=-10% --pitch=-20Hz --volume=+0% \
  --text "Reality bows to our gravity." --write-media titan_01.mp3 --write-subtitles titan_01.vtt
```

```python
import asyncio, edge_tts

async def synth(text: str, voice: str, out: str, rate="+0%", pitch="+0Hz"):
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    with open(out, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                pass  # offset/duration per word: use for subtitles or lip sync

asyncio.run(synth("System operational, reporting!", "en-US-AriaNeural", "unit_01.mp3", rate="+15%", pitch="+5Hz"))
```

- Edge-TTS controls emotion through voice choice, `rate`, `pitch` and `volume` only.
- Use `WordBoundary` events for timed captions and simple lip-sync drivers.
- Stream chunks asynchronously; never block the render/UI thread waiting for synthesis.

## 4. Character voice profiles

Define each character once and reuse the profile in code:

| Archetype | Direction | Edge-TTS | Bark |
|-----------|-----------|----------|------|
| Small / nervous unit | Higher pitch, fast, clipped | `rate=+15%`, `pitch=+8Hz` | Higher-pitched preset, short lines, `...` hesitation |
| Heavy / titan | Low pitch, slow, deliberate | `rate=-15%`, `pitch=-20Hz` | Deep preset, periods between phrases, CAPS on key words |
| Robot / AI | Flat, even | `rate=+0%`, `pitch=-5Hz` | Flat preset, no tags, hyphenated syllables; add vocoder/ring-mod in post |
| Whisper / sneaky | Quiet, breathy | `volume=-20%`, `rate=-10%` | `[sighs]`, ellipses, lower volume in post |
| Arrogant villain | Slow, emphasized | `rate=-8%`, CAPS-free text with commas | `[clears throat]`, CAPS on 1 or 2 words |

Robot and monster voices are often best achieved by processing: pitch shift, formant shift, chorus, ring modulation, distortion, convolution reverb.

## 5. Integration

```typescript
export type Emotion = "neutral" | "arrogant" | "robotic" | "aggressive" | "whisper";

export interface VoiceGenerationRequest {
  lineId: string;
  text: string;
  characterId: string;     // resolves to engine + voice id + default params
  emotion?: Emotion;       // mapped to rate/pitch/volume or presets
  language?: string;       // BCP-47, e.g. "en-US"
  outputFormat: "wav_48000" | "mp3_44100";
}
```

- Resolve `characterId` to engine, voice and parameters in a data file, not in code.
- Cache by hash of (text, voice, params, engine version). Reuse cache hits; only regenerate changed lines.
- Run generation as an offline batch step (CI or editor tool) that writes files + a manifest (`lineId`, `text`, `voice`, `duration`, `hash`).
- If you must generate at runtime, stream, show a placeholder, and fall back to text-only on failure.
- Localization: keep text in string tables with line IDs; generate per language with matched voices.

## 6. Post-processing

1. Trim silence; keep a small pad (50 to 100 ms) so words do not cut.
2. Remove clicks and breaths if distracting; de-ess harsh sibilance.
3. Resample to 48 kHz, 16-bit mono WAV for in-world voices (stereo for narration).
4. Loudness: target around -16 to -20 LUFS for dialogue, true peak below -1 dBTP, consistent across characters. Check with `ffmpeg -af loudnorm`.
5. Apply character processing (EQ, pitch, reverb, radio filter) after normalization.
6. Name files `VO_<Char>_<LineID>_<NN>.wav`.

## 7. Quality checklist

- [ ] Pronunciations correct (names, jargon, numbers).
- [ ] No hallucinated words or noises (listen to the whole clip).
- [ ] Emotion fits the context; takes with off tone discarded.
- [ ] Levels consistent across characters and lines.
- [ ] Lip sync / subtitle timing matches (use word boundaries or forced alignment).
- [ ] Subtitles available for accessibility.
- [ ] Voice and training data consent documented for cloned voices.
- [ ] Marked as synthetic where store or platform policy requires disclosure.

## Failure patterns

| Symptom | Fix |
|---------|-----|
| Bark rambles or adds noise | Shorter text, remove tags, regenerate, lower temperature if exposed |
| Voice changes between lines | Fix the speaker preset per character, same seed or history prompt |
| Robotic flat Edge-TTS | Try a different neural voice, adjust rate and pitch, rewrite punctuation |
| Cut-off words | Pad silence, check trim threshold |
| Slow generation | Batch offline on GPU, cache aggressively |
| Mispronounced term | Phonetic spelling or hyphenation, or add a pronunciation lexicon |
