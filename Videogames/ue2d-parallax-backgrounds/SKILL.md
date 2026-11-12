---
name: ue2d-parallax-backgrounds
description: Layered parallax backgrounds for 2D games in Unreal Engine 5 - driving layer offsets from camera movement, choosing factors that read as depth, seamless horizontal tiling and the wrap arithmetic that avoids a visible jump, vertical parallax, material-panner skies, and the performance budget for a background that covers the whole screen every frame. Use when adding depth to a 2D scene, when a scrolling background seams or pops, or when deciding between actor-driven and material-driven parallax. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Parallax Backgrounds

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Parallax is one idea — far things move less — plus the tiling arithmetic that keeps it
seamless. The arithmetic is where it goes wrong.

> Written from general 2D practice rather than verified end to end in one Unreal project.

## Before you start

1. **The camera is the driver.** Parallax offsets follow the *camera*, not the player; a
   camera with a dead zone already decouples the two.
2. **Author tileable art.** A layer that does not tile cannot be wrapped, only stretched.
3. **Decide actor-driven or material-driven** (section 4). Mixing both in one scene makes
   depth inconsistent.

## 1. Factors

A factor of 0 is painted on the screen; 1 moves with the world.

| Layer | Factor | Reads as |
|-------|--------|----------|
| Sky / gradient | 0.0 – 0.05 | Infinitely far |
| Far mountains | 0.15 | Kilometres |
| Hills | 0.35 | Hundreds of metres |
| Tree line | 0.55 | Tens of metres |
| Gameplay | 1.0 | The world |
| Foreground | 1.3 – 1.6 | In front of the camera |

Foreground factors above 1 are what sell depth, more than any number of background
layers — grass or pillars sweeping past faster than the world is an immediate read.

Space the factors roughly geometrically. Evenly spaced factors read as flat cards.

## 2. Driving the layers

```cpp
void AParallaxLayer::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!Camera.IsValid()) return;

    const FVector Cam = Camera->GetActorLocation();
    const FVector Delta = Cam - InitialCameraLocation;

    FVector P = InitialLocation;
    P.X += Delta.X * ParallaxFactor;
    P.Z += Delta.Z * ParallaxFactor * VerticalScale;   // often 0.3-0.5 of horizontal
    P.Y = InitialLocation.Y;                           // depth never changes

    SetActorLocation(P);
}
```

Vertical parallax usually wants to be weaker than horizontal, or a jump makes the whole
sky lurch.

## 3. Seamless tiling

Place at least three copies, each one texture width apart, and wrap whichever leaves the
view:

```cpp
const float RelativeX = GetActorLocation().X - Camera->GetActorLocation().X;
if (RelativeX < -TileWidth)
{
    AddActorWorldOffset(FVector(TileWidth * TileCount, 0.0f, 0.0f));
}
else if (RelativeX > TileWidth * (TileCount - 1))
{
    AddActorWorldOffset(FVector(-TileWidth * TileCount, 0.0f, 0.0f));
}
```

`TileWidth` must be the **exact** rendered width of one tile — sprite pixels times pixels
per unit. A rounding error of a fraction of a unit accumulates into a visible gap after a
few hundred wraps, which presents as "the background tears after playing a while".

Three copies is the minimum for a view one tile wide; use four if the view is wider or
the camera moves fast enough to cross a tile in one frame.

## 4. Material-driven skies

For distant layers that only need to scroll, a panner in the material beats moving actors:

```
TexCoord -> Panner (Speed X driven by a Material Parameter Collection) -> Texture Sample
```

Write the camera X into the MPC once per frame and every sky layer scrolls with zero
actor ticks. The texture must be set to **Wrap**, not Clamp, or it smears at the edge.

Prefer material panning for anything that is purely visual and never interacts; prefer
actors when a layer needs collision, spawning or gameplay meaning.

## 5. Budget

A full-screen background layer is a full-screen quad of overdraw. Six opaque layers means
six screens of fill every frame, which on a modest GPU is a real cost.

- Mark layers **opaque** unless they genuinely need alpha; translucent layers do not
  z-cull and are far more expensive.
- Put the sky in one opaque layer rather than stacking translucent gradients.
- Cull layers that are off screen; a parallax layer two screens away still renders unless
  you disable it.
- Watch overdraw directly rather than guessing — the shader complexity view shows it.

## 6. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Visible seam or jump when wrapping | `TileWidth` not the exact rendered width | Recompute from sprite pixels × pixels per unit |
| Gap appears after long play | Accumulated float error from repeated offsets | Recompute absolute position from the camera instead of accumulating |
| Layers look like flat cards | Evenly spaced factors | Space them geometrically; add a foreground above 1.0 |
| Sky lurches on every jump | Vertical factor equals horizontal | Scale vertical to 0.3–0.5 |
| Background tears at one edge | Texture set to Clamp | Set Wrap |
| Frame rate drops with many layers | Translucent full-screen overdraw | Make layers opaque; cull off-screen |
| Parallax stutters | Layers tick before the camera moves | Drive layers from the camera's final position, or set tick dependency |

Related: [[ue2d-camera-2d]], [[ue2d-paper2d-foundations]], [[ue2d-sprite-lighting]].
