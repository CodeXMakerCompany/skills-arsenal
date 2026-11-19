# Audio

Game audio and generated speech. Two of these produce sound, two put it into an engine.

```
Audio/
├── elevenlabs-sfx-generator/   AI sound effects: prompt, params, trim, loudness, layering
├── bark-edge-tts-dialogue/     character dialogue with Bark, Edge-TTS, XTTS
├── ue-sfx-pipeline/            a raw file to something Unreal actually plays
└── ue-niagara-audio-trigger/   tag-driven cues, Niagara and MetaSound parameters
```

## The pipeline

```
elevenlabs-sfx-generator   or   bark-edge-tts-dialogue
                 |
          ue-sfx-pipeline            WAV, trim, mono, attenuation, concurrency
                 |
     ue-niagara-audio-trigger        who plays it, when, with what parameters
```

Generating a sound is the easy half. `ue-sfx-pipeline` exists because the two things that make a generated sound unusable in an engine are dead air at the head, which delays the hit, and a stereo file, which will not spatialise at all.

## Route

| Need | Skill |
|---|---|
| An impact, a UI click, an ambience | `elevenlabs-sfx-generator` |
| A character line, a barked callout, a narrator | `bark-edge-tts-dialogue` |
| The sound plays late, or does not spatialise | `ue-sfx-pipeline` |
| Too many instances of one sound at once | `ue-sfx-pipeline`, the concurrency asset |
| A cue that fires with a VFX, driven by gameplay state | `ue-niagara-audio-trigger` |
| Narration in your own cloned voice | [`audio-clone`](../audio-clone/SKILL.md) at the root |

## The line between dialogue and narration

`bark-edge-tts-dialogue` is for **characters inside a game**: many short lines, batched and cached, with correct Bark tags and per-character voice profiles.

[`audio-clone`](../audio-clone/SKILL.md) at the root is for **narration in your own voice** over video, through fish.audio. Different job, different pipeline, and reaching for the wrong one wastes a render.

## Not here

- VFX timing the audio syncs to: [`Videogames`](../Videogames/MAP.md), particularly `ue-anim-montages-notifies` for notify-driven cues.
- Flipbook and SubUV textures a Niagara effect needs: [`Graphics2D`](../Graphics2D/MAP.md).
- Spanish video narration and its script gate: the root content skills in [`ARSENAL-MAP.md`](../ARSENAL-MAP.md).
