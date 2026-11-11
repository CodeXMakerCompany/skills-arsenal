---
name: ue-sfx-pipeline
description: Take a raw sound effect file and make it play correctly in Unreal Engine 5 - converting to the WAV format the engine actually imports, trimming dead air that delays the hit, downmixing to mono so the sound can be spatialised at all, and authoring SoundAttenuation and SoundConcurrency assets. Then play it from C++ with PlaySoundAtLocation and randomised pitch, including why an attached audio component is the wrong choice for a pickup that destroys itself. Use when adding sound effects, when an imported sound will not spatialise, when a sound feels late, or when many simultaneous effects turn into noise.
---

# UE5 Sound Effect Pipeline

Most "the sound is wrong" problems in Unreal are decided before the asset is imported:
the wrong format, dead air at the head, or a stereo file that the engine will never
spatialise. Fix those first, then the playback code is five lines.

## Before you start

1. **Unreal imports WAV.** The sound factory wants uncompressed PCM. An MP3, OGG or M4A
   dropped into `Content/` is a loose file, not an asset.
2. **Decide 2D or 3D.** A UI click is 2D and may stay stereo. Anything that happens at a
   place in the world must be **mono** (section 2).
3. **Measure the file before converting it.** Dead air and peak level decide the trim and
   whether you need to touch the gain at all.

## 1. Measure first

```bash
ffprobe -v error -show_entries format=duration \
  -show_entries stream=codec_name,sample_rate,channels \
  -of default=noprint_wrappers=1 pop.mp3

# Peak and average level
ffmpeg -i pop.mp3 -af volumedetect -f null /dev/null 2>&1 | grep -E "mean_volume|max_volume"

# Where the actual sound is
ffmpeg -i pop.mp3 -af "silencedetect=noise=-60dB:d=0.02" -f null /dev/null 2>&1 \
  | grep -oE "silence_(start|end): [0-9.]+"
```

A real example: a 2.04 s "pop" turned out to be **90 ms of leading silence, 242 ms of
sound, and 1.74 s of nothing**. Imported as-is, every pickup would fire 90 ms late —
clearly audible — and carry 1.7 s of silence in memory. Measuring takes one command and
changes the whole asset.

`max_volume` near 0 dB means it is already loud; leave the gain alone and set level with
the volume multiplier at the call site. Do not normalise by reflex.

## 2. Convert: mono matters more than anything else

```bash
ffmpeg -y -i pop.mp3 \
  -af "atrim=start=0.088:end=0.345,asetpts=PTS-STARTPTS,\
pan=mono|c0=0.5*c0+0.5*c1,afade=t=out:st=0.245:d=0.012" \
  -ar 48000 -acodec pcm_s16le S_CubePickup.wav
```

Each part earns its place:

| Part | Why |
|------|-----|
| `atrim` | Removes the head delay and the dead tail |
| `asetpts=PTS-STARTPTS` | Rebases timestamps after the trim, or the file keeps the original offset |
| `pan=mono` | **Unreal only spatialises mono assets.** A stereo file plays 2D however the attenuation is configured |
| `afade` out | 10–15 ms, so a waveform that does not end at zero does not click |
| `pcm_s16le` | 16-bit PCM is what the sound factory accepts |
| `-ar 48000` | 44.1 or 48 kHz both fine; stay consistent across the project |

The mono rule is the one people lose hours to. Attenuation set up perfectly on a stereo
asset does nothing, and nothing in the editor says why.

Always add a small margin around the measured trim points — cutting exactly on the first
non-silent sample shaves the attack transient, which is the part that gives a sound its
snap.

## 3. Import

```python
t = unreal.AssetImportTask()
t.set_editor_property('filename', '/abs/path/S_CubePickup.wav')
t.set_editor_property('destination_path', '/Game/SoundEffects')
t.set_editor_property('destination_name', 'S_CubePickup')
t.set_editor_property('automated', True)
t.set_editor_property('replace_existing', True)
t.set_editor_property('save', False)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
unreal.EditorAssetLibrary.save_directory('/Game/SoundEffects',
                                         only_if_is_dirty=False, recursive=True)
```

Save the **directory**, not the task; `task.save = True` is unreliable about dependencies.
Then confirm what arrived:

```python
w = unreal.EditorAssetLibrary.load_asset('/Game/SoundEffects/S_CubePickup')
print(w.get_editor_property('num_channels'))   # must be 1 for a positional sound
print(w.get_editor_property('duration'))
```

## 4. Attenuation and concurrency

Two small data assets, both fully scriptable — unlike Sound Cues, which need a node graph.

```python
at, eal = unreal.AssetToolsHelpers.get_asset_tools(), unreal.EditorAssetLibrary

att = at.create_asset('ATT_Pickup', '/Game/SoundEffects',
                      unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
a = att.get_editor_property('attenuation')
a.set_editor_property('attenuate', True)          # not 'enable_attenuation'
a.set_editor_property('spatialize', True)
a.set_editor_property('attenuation_shape', unreal.AttenuationShape.SPHERE)
a.set_editor_property('attenuation_shape_extents', unreal.Vector(400.0, 0.0, 0.0))  # inner radius
a.set_editor_property('falloff_distance', 2500.0)
att.set_editor_property('attenuation', a)

con = at.create_asset('CONC_Pickup', '/Game/SoundEffects',
                      unreal.SoundConcurrency, unreal.SoundConcurrencyFactory())
c = con.get_editor_property('concurrency')
c.set_editor_property('max_count', 6)
c.set_editor_property('limit_to_owner', False)
c.set_editor_property('resolution_rule', unreal.MaxConcurrentResolutionRule.STOP_OLDEST)
c.set_editor_property('retrigger_time', 0.0)
con.set_editor_property('concurrency', c)
```

The struct is a **value**: read it, mutate it, write it back. Mutating it without the
final `set_editor_property` changes nothing and reports no error.

Property names do not match the editor labels — `attenuate`, not `enable_attenuation`.
Introspect with `dir(unreal.SoundAttenuationSettings())` rather than guessing.

On concurrency: `max_count` with `STOP_OLDEST` keeps a burst of pickups from stacking into
a wall of noise. Leave `retrigger_time` at 0 for pickups — a non-zero value silently drops
legitimately simultaneous collections, which reads as "sometimes there's no sound".

## 5. Play it from C++

```cpp
if (PickupSound)
{
    const float Pitch = FMath::FRandRange(PitchRange.X, PitchRange.Y);   // 0.94 .. 1.08
    UGameplayStatics::PlaySoundAtLocation(
        this, PickupSound, GetActorLocation(), FRotator::ZeroRotator,
        Volume, Pitch, /*StartTime=*/0.0f,
        Attenuation, Concurrency, /*OwningActor=*/nullptr);
}

Destroy();
```

**`PlaySoundAtLocation`, not an attached `UAudioComponent`.** A component lives on the
actor, and a pickup destroys itself the moment it is collected — the component dies with
it and the sound is cut off a frame after it starts. `PlaySoundAtLocation` is fire and
forget: it spawns an unowned audio component at a world position that outlives the actor.
Passing `nullptr` as the owner is deliberate for the same reason.

**Randomise the pitch at the call site.** A fixed pitch on a sound the player triggers
thirty times a minute turns mechanical within seconds. A window of roughly ±6% is enough
to disguise the repetition without sounding detuned, and it costs one `FRandRange` instead
of a Sound Cue with a modulator node.

Use a Sound Cue instead when designers need to edit the variation without a rebuild, or
when the sound needs randomly chosen waves, layering or branching.

## 6. Loading behaviour

For short, frequently triggered effects, force them resident rather than streamed, or the
first play after a level load hitches while the asset is pulled in. Set it on the sound
wave's `LoadingBehavior` (Force Inline) or by making the owning class a hard reference —
a `ConstructorHelpers::FObjectFinder` already does the latter, which is a quiet benefit of
wiring the asset in the constructor rather than looking it up lazily.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| The file will not import | MP3/OGG/M4A | Convert to 16-bit PCM WAV |
| Sound ignores attenuation, plays flat 2D | Asset is stereo | Downmix to mono |
| Sound arrives noticeably late | Leading silence in the file | Trim it |
| Sound is cut off immediately | Attached audio component on an actor that destroys itself | `PlaySoundAtLocation` |
| Repeated pickups sound mechanical | Fixed pitch | Randomise ±6% at the call site |
| A burst of pickups becomes a wall of noise | No concurrency cap | `max_count` with `STOP_OLDEST` |
| Some simultaneous pickups are silent | `retrigger_time` above 0 | Set it to 0 |
| Click at the end of the sound | Trimmed mid-waveform | 10–15 ms fade out |
| Attenuation settings appear to do nothing | Struct mutated but not written back | Read, mutate, `set_editor_property` |
| First play of the level hitches | Streamed loading | Force inline, or hard-reference it |

Related: [[elevenlabs-sfx-generator]], [[ue-niagara-audio-trigger]],
[[ue-timers-and-triggers]], [[ue-actor-spawner]].
