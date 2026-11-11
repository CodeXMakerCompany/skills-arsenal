---
name: ue2d-paper2d-foundations
description: Set up a 2D project in Unreal Engine 5 with Paper2D - enabling the plugins, sprite import settings that keep pixel art crisp, choosing a pixels-per-unit scale and sticking to it, orthographic camera sizing for an exact pixel ratio, the XZ plane convention, sprite sort order, and the render settings to turn off because a 2D game pays for none of them. Use when starting a 2D game in Unreal, when pixel art looks blurry or shimmers, when sprites render in the wrong order, or when deciding project scale and camera setup for 2D.
---

# UE5 Paper2D Foundations

Unreal is a 3D engine rendering quads. Almost every 2D problem — blurry art, shimmering
edges, wrong draw order — comes from treating it as a 2D engine instead of configuring
the 3D one properly.

> Written from general Paper2D practice rather than verified end to end in one project.
> Treat the numbers as starting points and measure in your own build.

## Before you start

1. **Enable the plugins**: Paper2D ships with the engine. PaperZD (animation state
   machines) and Paper2D Tile Map Editor are separate and worth enabling now rather than
   after you have authored animation by hand.
2. **Pick a pixels-per-unit scale and write it down.** Everything downstream — camera
   size, movement speeds, collision — depends on it being consistent.
3. **Decide the plane.** Paper2D's convention is **XZ**: X is right, Z is up, Y is depth
   and sort order. Fighting this costs you every built-in helper.

## 1. Sprite import settings

For pixel art, the default texture settings destroy the art before you see it:

| Setting | Value | Why |
|---------|-------|-----|
| Filter | **Nearest** | Bilinear blurs every pixel edge |
| Mip Gen Settings | **NoMipmaps** | Mips make distant sprites mush |
| Compression | **UserInterface2D (RGBA)** | DXT compression bands flat colour |
| Texture Group | **2D Pixels (unfiltered)** | Carries the above as a group default |
| sRGB | On for colour, **off** for masks and data | |

Set these on the texture *before* extracting sprites. Changing them later means
re-extracting.

For non-pixel (hand-painted, vector-exported) art, keep bilinear filtering and mips, and
import at twice the display size.

## 2. Scale: pick one and hold it

The common choice is **1 pixel = 1 unreal unit**, which makes a 32×32 sprite 32 uu. It
keeps mental arithmetic trivial and makes physics numbers legible: gravity around
`-980`, jump velocities in the hundreds.

Set it once in Project Settings → Paper2D → **Default Pixels Per Unreal Unit = 1.0**, and
never scale individual sprite actors to compensate for an import mistake. A sprite scaled
to 1.37 is a bug that propagates into collision, animation and camera framing.

## 3. Orthographic camera for an exact pixel ratio

```
OrthoWidth = HorizontalResolution * PixelsPerUnit / DesiredZoom
```

For a 1920×1080 target at 1 uu per pixel and a 3× zoom: `OrthoWidth = 1920 / 3 = 640`.
That gives 640×360 visible units — a clean 16:9 low-resolution canvas.

```cpp
Camera->SetProjectionMode(ECameraProjectionMode::Orthographic);
Camera->SetOrthoWidth(640.0f);
Camera->SetWorldRotation(FRotator(0.0f, -90.0f, 0.0f));   // look down +X at the XZ plane
```

Non-integer zoom is the usual cause of shimmering: at 2.5× some source pixels cover three
screen pixels and others two, and the pattern crawls as the camera moves. Keep the zoom
an integer, and snap the camera position to whole units.

## 4. Sort order

Paper2D sorts by **Y** (depth) and then by the sprite's Sort Order. Give yourself bands
rather than fighting ties:

| Layer | Y | Sort order |
|-------|---|------------|
| Far background | +500 | -200 |
| Background | +200 | -100 |
| Gameplay | 0 | 0 |
| Foreground props | -200 | 100 |
| Effects | -400 | 200 |

Keep gameplay at Y = 0 so collision and movement stay in one plane, and use Y only for
visual layering. For characters that must overlap correctly within the gameplay layer,
set `TranslucencySortPriority` from the actor's Z each frame, or use a small Y offset
derived from Z.

## 5. Turn off what 2D does not use

A 2D game inherits a renderer configured for 3D worlds. In `DefaultEngine.ini`:

```ini
[/Script/Engine.RendererSettings]
r.DynamicGlobalIlluminationMethod=0     ; Lumen has nothing to light
r.ReflectionMethod=0
r.Shadow.Virtual.Enable=0
r.VolumetricFog=0
r.GenerateMeshDistanceFields=False
r.Nanite=0                              ; no Nanite meshes in a sprite game
r.DefaultFeature.MotionBlur=False
r.DefaultFeature.Bloom=False            ; re-enable deliberately if the art wants it
r.AntiAliasingMethod=1                  ; FXAA; TSR smears pixel art
```

TSR and TAA are actively harmful to pixel art: both accumulate across frames and leave
trails on sharp edges. FXAA or none.

See [[ue-indie-game-setup]] for the reasoning behind each of those and how to verify they
took effect.

## 6. Collision in 2D

Constrain physics to the plane so nothing drifts in depth:

```cpp
GetCharacterMovement()->SetPlaneConstraintEnabled(true);
GetCharacterMovement()->SetPlaneConstraintNormal(FVector(0.0f, 1.0f, 0.0f));   // lock Y
```

Sprite collision comes from the sprite's own polygon, edited in the Sprite Editor. Prefer
a simple box or a handful of vertices: a per-pixel outline on a 64×64 sprite generates
dozens of edges and buys nothing a box would not.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pixel art blurry | Bilinear filter, mips, DXT compression | Nearest, NoMipmaps, UserInterface2D |
| Edges shimmer while the camera moves | Non-integer zoom, or sub-pixel camera position | Integer zoom; snap camera to whole units |
| Ghosting trails behind moving sprites | TSR or TAA | FXAA or none |
| Sprites flicker in and out of order | Equal Y and equal sort order | Separate the layers into bands |
| Character drifts out of the plane | No plane constraint | `SetPlaneConstraintNormal` |
| Collision far more expensive than expected | Per-pixel collision geometry | Simplify to a box |
| Everything half the expected size | Pixels-per-unit changed after authoring | Set it once, before building content |

Related: [[sprite-sheet-packer]], [[ue2d-flipbook-animation]], [[ue2d-camera-2d]],
[[ue-indie-game-setup]].
