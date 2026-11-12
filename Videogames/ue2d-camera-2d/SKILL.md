---
name: ue2d-camera-2d
description: A 2D follow camera in Unreal Engine 5 that does not make players seasick - orthographic setup on the XZ plane, dead zones so small movements do not move the view, look-ahead biased toward travel direction, asymmetric vertical damping for jumps, clamping to level or room bounds, camera shake, and pixel snapping to stop sub-pixel shimmer. Use when the 2D camera feels jittery or nauseating, when the player cannot see far enough ahead, or when setting up room-based or bounded camera behaviour. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 2D Camera

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


A 2D camera that rigidly tracks the player is uncomfortable to look at: every small hop
shakes the whole screen. Everything below exists to decouple the view from the character
without losing track of them.

> Written from general 2D camera practice rather than verified end to end in one Unreal
> project.

## Before you start

1. **Orthographic, on the XZ plane**, with `OrthoWidth` derived from your target
   resolution and zoom — see [[ue2d-paper2d-foundations]].
2. **Decide the model**: continuous follow (most platformers), room-snapped (Metroidvania),
   or locked per screen (puzzle).
3. **Own the camera in one actor.** A camera written to from several systems fights
   itself in a way that is very hard to read.

## 1. Dead zone

Only move when the player leaves a rectangle around the current centre. This is the
single biggest comfort win:

```cpp
void A2DCameraRig::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!Target.IsValid()) return;

    const FVector T = Target->GetActorLocation();
    FVector C = GetActorLocation();

    const float DX = T.X - C.X;
    if (FMath::Abs(DX) > DeadZone.X)
    {
        C.X += DX - FMath::Sign(DX) * DeadZone.X;
    }

    const float DZ = T.Z - C.Z;
    if (FMath::Abs(DZ) > DeadZone.Y)
    {
        C.Z += DZ - FMath::Sign(DZ) * DeadZone.Y;
    }
    /* ... look-ahead, damping, clamping, snapping ... */
}
```

A dead zone of roughly 60 × 40 units at 1 uu per pixel means small hops and footsteps do
not move the view at all.

## 2. Look-ahead

Bias the view toward where the player is going, so they see what they are running into:

```cpp
const float VelX = Target->GetVelocity().X;
const float DesiredLead = FMath::Clamp(VelX / MaxRunSpeed, -1.0f, 1.0f) * LookAheadDistance;
CurrentLead = FMath::FInterpTo(CurrentLead, DesiredLead, DeltaSeconds, LookAheadSpeed);
C.X += CurrentLead;
```

`LookAheadDistance` around 100 uu, `LookAheadSpeed` around 2. Interpolating the lead
rather than applying it directly is what stops the camera snapping back and forth when
the player changes direction repeatedly.

## 3. Asymmetric vertical damping

Vertical motion is where 2D cameras cause nausea. Follow jumps lazily and landings
promptly:

```cpp
const bool bFalling = Target->GetVelocity().Z < 0.0f;
const float VerticalSpeed = bFalling ? FallFollowSpeed : RiseFollowSpeed;   // e.g. 8 vs 3
Smoothed.Z = FMath::FInterpTo(Smoothed.Z, C.Z, DeltaSeconds, VerticalSpeed);
Smoothed.X = FMath::FInterpTo(Smoothed.X, C.X, DeltaSeconds, HorizontalFollowSpeed);
```

Better still for platformers: do not follow vertically at all while the player is
airborne, and only catch up once they are grounded. The view then stays still through a
jump, which is exactly what players want and rarely ask for by name.

## 4. Clamp to bounds

```cpp
const float HalfW = Camera->OrthoWidth * 0.5f;
const float HalfH = HalfW / AspectRatio;

Smoothed.X = FMath::Clamp(Smoothed.X, Bounds.Min.X + HalfW, Bounds.Max.X - HalfW);
Smoothed.Z = FMath::Clamp(Smoothed.Z, Bounds.Min.Y + HalfH, Bounds.Max.Y - HalfH);
```

Guard the degenerate case: when a room is **narrower** than the view, the clamp inverts
and the camera jitters between two impossible limits. Centre on the room instead:

```cpp
if (Bounds.Max.X - Bounds.Min.X < HalfW * 2.0f)
{
    Smoothed.X = (Bounds.Min.X + Bounds.Max.X) * 0.5f;
}
```

For room-based games, store bounds on trigger volumes and swap them on overlap, blending
over about 0.3 s rather than cutting.

## 5. Pixel snapping

Sub-pixel camera positions make every sprite edge shimmer. Snap last, after all smoothing:

```cpp
if (bPixelSnap)
{
    Smoothed.X = FMath::RoundToFloat(Smoothed.X / UnitsPerPixel) * UnitsPerPixel;
    Smoothed.Z = FMath::RoundToFloat(Smoothed.Z / UnitsPerPixel) * UnitsPerPixel;
}
SetActorLocation(Smoothed);
```

Snapping before smoothing quantises the smoothing itself and produces visible stepping.

## 6. Shake

```cpp
UGameplayStatics::GetPlayerCameraManager(this, 0)->StartCameraShake(HitShakeClass, 1.0f);
```

Keep 2D shake small and short — 2–4 units, under 0.2 s. Scale the magnitude by the event
rather than playing the same shake for a footstep and a boss slam. If pixel snapping is
on, shake in whole pixels or the snapping fights it.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| View shakes on every small hop | No dead zone | Add one, ~60 × 40 |
| Nauseating during jumps | Camera tracks Z rigidly | Asymmetric damping, or do not follow while airborne |
| Camera snaps back and forth | Look-ahead applied directly | Interpolate the lead |
| Edges shimmer | Sub-pixel camera position | Snap after smoothing |
| Jitter in small rooms | Clamp inverted when the room is narrower than the view | Centre on the room |
| Player runs off screen | Follow speed below run speed | Raise it, or widen the dead zone |
| Hard cut between rooms | Bounds swapped instantly | Blend over ~0.3 s |

Related: [[ue2d-paper2d-foundations]], [[ue2d-platformer-controller]],
[[ue2d-parallax-backgrounds]], [[ue-third-person-camera]].
