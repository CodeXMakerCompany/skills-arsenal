---
name: ue-indie-game-setup
description: Cut an Unreal Engine 5 project down to a render budget an indie or jam team can actually ship, and prove the cut with measurements instead of guesses. Covers the three scenario profiles (conservative 3D, stylized low-poly, flat 2D), the exact cvars each one sets and why, template scope auditing (Open World landscapes, World Partition proxies, volumetric clouds), and the measurement traps that make UE performance work on Linux/AMD look like something it is not. Use when the editor crawls, when a project was started from a heavyweight template, when deciding what to turn off for a small team, or when asked for a "perfect indie setup". Default profile is conservative 3D.
---

# UE5 Indie Game Setup

UE5's templates default to a AAA render stack: Lumen, Virtual Shadow Maps, TSR, Nanite,
volumetric clouds, and on the Open World template an entire streaming landscape. Each of
those is defensible on a funded team with a profiling budget. Together, on an indie
project, they produce an editor nobody can work in.

This skill cuts the stack to a chosen scenario profile and verifies the cut. The order
matters: **measure, attribute, cut, verify**. Skipping to "turn off Lumen" sometimes
works and teaches nothing, and on Linux it can hide the real cause.

## Before you start

1. **Find out what template the project came from.** Inventory the level's actors by
   class before touching settings (section 1). A `Landscape` plus dozens of
   `LandscapeStreamingProxy` means Open World, and no cvar fixes that.
2. **Check the platform.** Lumen and VSM cost noticeably more on Linux/Vulkan than on
   Windows/D3D12, and the GPU profiler behaves differently (section 1.3). Record the GPU.
3. **Confirm the level is saved.** A level named `Untitled_*` lives in `/Temp` and has
   never been written to disk. Any level transition destroys it. Save it first.
4. **Ask which scenario profile applies** (section 2) if the user has not said. It changes
   whether Nanite, atmosphere and reflections stay.

## 1. Diagnose before cutting

### 1.1 Inventory the level

```python
import unreal
from collections import Counter
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
for k, v in Counter(a.get_class().get_name() for a in actors).most_common():
    print(f'{v:4d}  {k}')
```

What each finding means:

| Finding | Meaning | Fixable by cvars? |
|---------|---------|-------------------|
| `Landscape` + many `LandscapeStreamingProxy` | Open World template, World Partition streaming | **No** — scope problem (section 5) |
| `VolumetricCloud` | Per-pixel raymarched clouds, one of the heaviest actors in the engine | Yes (`r.VolumetricCloud 0`) but prefer deleting it |
| `SkyAtmosphere` | Physically based sky; moderate, usually worth keeping | Keep |
| `ExponentialHeightFog` | Cheap *unless* its volumetric fog flag is on | Yes (`r.VolumetricFog 0`) |
| `SkyLight` with real-time capture | Re-captures the sky cubemap every frame | Set `real_time_capture=False` |
| Hundreds of static meshes | Draw-call problem, not a feature problem | Instancing / HLOD, not cvars |

### 1.2 Read the current render configuration

```python
for cv in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.Shadow.Virtual.Enable',
           'r.AntiAliasingMethod','r.VolumetricCloud','r.VolumetricFog','r.Nanite',
           'r.ScreenPercentage','r.Shadow.CSM.MaxCascades']:
    print(f'{cv:38s} = {unreal.SystemLibrary.get_console_variable_float_value(cv)}')
```

Beware: `get_console_variable_float_value` returns `0.0` both for a cvar set to zero and
for a cvar that **does not exist**. Never conclude a feature is off from a `0.0` alone on
a cvar name you are not certain about.

### 1.3 Get the frame's real shape with ProfileGPU

```python
unreal.SystemLibrary.execute_console_command(None, 'r.ProfileGPU.ShowUI 0')
unreal.SystemLibrary.execute_console_command(None, 'ProfileGPU')
```

The result lands in `Saved/Logs/<Project>.log` one frame later, not in the return value.
Pull the two things that matter:

```bash
grep -oE "FRAME [0-9]+ draws [0-9]+ prims [0-9]+ verts.*" Saved/Logs/*.log | tail -1
grep -oE "(Lumen[A-Za-z]*|VirtualShadowMap[A-Za-z]*|VolumetricCloud[A-Za-z]*|TemporalSuperResolution)" \
  Saved/Logs/*.log | sort | uniq -c | sort -rn | head -20
```

The first line gives draws / primitives / vertices — that is your scope, and it is honest.
The second gives which expensive passes are actually in the frame.

**On Linux with AMD/Vulkan, ProfileGPU reports no timings**: every entry comes back
`0.00ms` and `-nan%` because GPU timestamp queries are unavailable. The pass hierarchy and
geometry counts are still correct and still worth having. Do not report the zeros as "the
GPU is idle".

### 1.4 The two traps that fake a frame-rate measurement

Both of these will hand you a number that has nothing to do with rendering cost:

- **Background throttling.** `editor.ThrottleCPUWhenNotForeground` (Editor Preferences →
  "Use Less CPU when in Background") caps the editor while another window has focus.
- **Idle viewport redraw.** A viewport that is *not* in Realtime mode only repaints on a
  fixed low-frequency timer. The tell is a frame time that is a suspiciously round
  constant — **exactly 333.3 ms (3.0 fps)** — identical across wildly different render
  settings. That is the idle timer, not your GPU.

There is no reliable Python API to force a viewport into Realtime, so **a remote script
cannot measure editor fps**. Measure one of these ways instead:

| Method | Good for |
|--------|----------|
| `stat unit` in the viewport while navigating (human reads it) | The real number, including Game/Draw/GPU split |
| `stat fps` plus Realtime enabled on the viewport | Quick sanity check |
| Geometry counts from ProfileGPU (section 1.3) | Scope, platform independent |
| Packaged build with `-benchmark -fps=...` | Shipping numbers |

If you cannot measure, say so plainly and change settings on reasoning. Do not invent a
before/after.

## 2. Scenario profiles

Pick one. The profile decides the cvars; everything else in this skill is shared.

| Profile | For | Nanite | GI | Reflections | Sky |
|---------|-----|--------|----|-------------|-----|
| **`conservative-3d`** *(default)* | Believable materials and lighting in small, contained scenes. The safe indie choice. | Keep | Off, SkyLight does the ambient | Screen space | SkyAtmosphere, no clouds |
| **`stylized-lowpoly`** | Simple geometry, flat colors, readable silhouettes. Cheapest for the look it gives. | Off | Off | Reflection captures only | Simple gradient or SkyAtmosphere |
| **`flat-2d`** | 2D, isometric or fixed camera. Almost nothing needs to be dynamic. | Off | Off | None | None |

Profile deltas on top of the shared base in section 3:

```ini
; conservative-3d (default)
r.ReflectionMethod=2          ; screen space
r.Shadow.CSM.MaxCascades=3
; Nanite left at 1

; stylized-lowpoly
r.Nanite=0
r.ReflectionMethod=0          ; reflection captures only
r.Shadow.CSM.MaxCascades=2
r.SkyLight.RealTimeReflectionCapture=0

; flat-2d
r.Nanite=0
r.ReflectionMethod=0
r.Shadow.CSM.MaxCascades=1
; delete SkyAtmosphere and the cloud actor entirely; bake what light you can
```

## 3. The shared base configuration

Write this into `Config/DefaultEngine.ini`. These are project settings, so they apply to
the editor *and* to packaged builds — which is the point of persisting them rather than
typing cvars into the console.

```ini
[/Script/Engine.RendererSettings]
; ---- Global illumination: Lumen off, lean on a SkyLight ----
r.DynamicGlobalIlluminationMethod=0
; ---- Reflections: screen space instead of Lumen (0 = captures only, cheaper still) ----
r.ReflectionMethod=2
; ---- Shadows: classic cascades instead of Virtual Shadow Maps ----
r.Shadow.Virtual.Enable=0
r.Shadow.CSM.MaxCascades=3
; ---- Antialiasing: TAA. TSR (=4) costs considerably more ----
r.AntiAliasingMethod=2
; ---- Volumetric fog off ----
r.VolumetricFog=0
; ---- Without Lumen, mesh distance fields only cost memory and build time ----
r.GenerateMeshDistanceFields=False
r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=True
```

Value reference, because the numbers are not guessable:

| Cvar | Values |
|------|--------|
| `r.DynamicGlobalIlluminationMethod` | 0 None, 1 Lumen, 2 Screen Space |
| `r.ReflectionMethod` | 0 None, 1 Lumen, 2 Screen Space |
| `r.AntiAliasingMethod` | 0 None, 1 FXAA, 2 TAA, 3 MSAA, 4 TSR |
| `r.Shadow.CSM.MaxCascades` | Engine default 10; 2–3 is plenty for a contained scene |

### Why each switch

- **Lumen off** is the single largest win on a small project. Lumen runs dozens of passes
  per frame (scene update, card capture, screen probes, reflections) and it is built for
  large dynamic worlds. A contained scene with a SkyLight and a few reflection captures
  looks fine and costs a fraction. It also removes Lumen's dependency on distance fields.
- **Virtual Shadow Maps off** removes the page-table machinery and projection passes. VSM
  earns its cost with Nanite-heavy, high-detail scenes; on indie geometry, 2–3 CSM
  cascades look equivalent and are far cheaper. Also drop `MaxCascades` from the default
  10 — ten cascades on a 40 m playspace is pure waste.
- **TSR → TAA**. TSR is a high-quality temporal upscaler with real cost. TAA is cheap and
  stable. If ghosting bothers you, FXAA (=1) is cheaper still and has no temporal history.
- **Volumetric fog and clouds off.** Both are raymarched per pixel. Height fog without the
  volumetric flag gives most of the atmosphere for almost nothing.
- **Mesh distance fields off** once Lumen is gone: nothing left consumes them except
  distance-field AO and shadows, and they cost memory plus asset build time.
- **Nanite is a per-profile decision, not a reflex.** Nanite costs where Nanite meshes are;
  with no Nanite meshes in the project it is nearly free, and it genuinely helps dense
  static geometry. Turn it off for stylized and 2D work, keep it for conservative 3D.

## 4. Applying settings: runtime first, then persist

Apply as runtime cvars first. It is instantly reversible, touches no files, and lets the
user judge the look before anything is committed:

```python
for c in ['r.DynamicGlobalIlluminationMethod 0','r.ReflectionMethod 2',
          'r.Shadow.Virtual.Enable 0','r.VolumetricCloud 0','r.VolumetricFog 0',
          'r.AntiAliasingMethod 2']:
    unreal.SystemLibrary.execute_console_command(None, c)
```

Then write the ini. Replace the whole `[/Script/Engine.RendererSettings]` section rather
than appending keys, so duplicates cannot accumulate, and validate afterwards:

```python
import configparser, io
c = configparser.ConfigParser(strict=False, allow_no_value=True)
c.read_string(io.open('Config/DefaultEngine.ini', encoding='utf-8').read())
print(dict(c['/Script/Engine.RendererSettings']))
```

Verify the project actually loads them — a typo in an ini fails silently:

```bash
UnrealEditor-Cmd <project>.uproject -run=pythonscript -script=check_cvars.py \
  -unattended -nosplash -nopause
grep -ah "FINAL" Saved/Logs/*.log      # commandlet output goes to the log, not stdout
```

## 5. Scope: the part cvars cannot fix

A streaming landscape is not a setting. If the inventory in section 1.1 found one, the
project is carrying an open world it does not need, and the frame will keep pushing
millions of primitives whatever the render settings say.

**Preserve, then replace** — never delete first:

1. If the level is unsaved (`/Temp/Untitled_*`), save it to a real path so the template
   survives and the user can return to it:
   `unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/Maps/L_OpenWorld')`.
   A World Partition level writes its actors as many separate assets under
   `Content/__ExternalActors__`; expect a hundred-plus files, which is normal.
2. Build a small level beside it and make that the default map. See the companion skill
   `ue-minimal-level-bootstrap` for the procedure and the crash it avoids.
3. Point the project at the new level:

```ini
[/Script/EngineSettings.GameMapsSettings]
EditorStartupMap=/Game/Maps/L_Main.L_Main
GameDefaultMap=/Game/Maps/L_Main.L_Main
```

4. Leave the heavy level on disk. Deleting it is the user's call, not yours.

Other scope levers, in the order they usually pay off: trim editor-only plugins from the
`.uproject`; drop unused template content from `Content/`; replace copy-pasted static
meshes with instanced static meshes; and only then reach for HLODs.

## 6. Further levers, after the base is in

Apply these when the base profile is not enough. Roughly in order of payoff per effort:

| Lever | How | Cost to the look |
|-------|-----|------------------|
| Bake the lighting | Sun to `Stationary`, build lighting | None — usually *better*; needs a bake step |
| SkyLight real-time capture off | `real_time_capture=False`, capture once | Sky changes stop being live |
| Reflection captures by hand | Place `SphereReflectionCapture` per area | None; this is the intended workflow without Lumen |
| Screen percentage | `r.ScreenPercentage 80` | Softer image; big GPU win, good for the editor |
| Cap the frame rate | `t.MaxFPS 60` | None; stops the GPU burning on an uncapped editor |
| Scalability presets | `sg.ShadowQuality 1`, `sg.EffectsQuality 1` | Shipping-side quality tiers |
| Texture streaming pool | `r.Streaming.PoolSize` to fit VRAM | Pop-in if set too low |

A note on build times rather than frame times: a cold Derived Data Cache means the editor
is compiling shaders while you judge performance. Check `Saved/Logs` for shader compile
activity and the DDC size before concluding anything about a fresh project or a fresh
machine.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| fps identical across every setting change, at a round constant like 333.3 ms | Idle viewport redraw or background throttle, not render cost | Enable Realtime on the viewport; measure with `stat unit` by hand |
| `ProfileGPU` shows `0.00ms` / `-nan%` everywhere | Linux/AMD Vulkan has no GPU timestamp queries | Use the geometry counts and pass list; measure fps another way |
| Settings in the ini appear to do nothing | Section duplicated, or the key sits under the wrong section header | Replace the whole section; validate with `configparser` |
| Editor still crawls after the full cut | A heavyweight level is still the one open | Confirm which level loaded, not which is configured as default |
| A cvar reads `0.0` and you conclude the feature is off | `get_console_variable_float_value` returns `0.0` for unknown cvars too | Verify the cvar name exists before trusting the value |
| Scalability warning in the log: "Setting the console variable ... was ignored as it is lower priority" | A `SetByScalability` write lost to a higher-priority source such as your ini | Expected; the ini wins, which is what you wanted |
