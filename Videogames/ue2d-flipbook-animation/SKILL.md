---
name: ue2d-flipbook-animation
description: Sprite animation in Unreal Engine 5 - building Paper2D flipbooks from sprite sheets, frame timing in flipbook frames rather than seconds, driving animation from gameplay state, and PaperZD animation state machines with transitions, notifies and animation sequences. Covers choosing between a hand-rolled state switch and PaperZD, and keeping the animation layer out of the movement code. Use when animating a 2D character or effect, when animations do not switch correctly, or when deciding how to structure 2D animation state. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Flipbook Animation

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


A flipbook is an ordered list of sprites with per-frame durations. The interesting work is
not making one — it is deciding what drives which flipbook, and keeping that decision out
of the movement code.

> Written from general Paper2D and PaperZD practice rather than verified end to end in
> one project.

## Before you start

1. **Extract sprites first.** From a sheet, use the Sprite Editor's grid extraction and
   confirm the cell size divides the sheet exactly; a one-pixel remainder shifts every
   frame after the first row. See [[sprite-sheet-packer]] for producing clean sheets.
2. **Decide hand-rolled or PaperZD.** Under roughly four states with simple rules, a
   switch in C++ is clearer. Beyond that, or when you need notifies and blended
   transitions, PaperZD pays for itself.
3. **Name consistently**: `FB_Hero_Idle`, `FB_Hero_Run`, `FB_Hero_Jump`,
   `FB_Hero_Fall`, `FB_Hero_Attack`.

## 1. Building a flipbook

Select the sprites in order, right click → Create Flipbook. Then in the Flipbook Editor
set **Frames Per Second** and per-frame durations.

Durations are in **frames, not seconds**. At 12 FPS, a frame with duration 2 lasts
1/6 second. Hold key poses for 2–3 frames and pass through in-betweens in 1; uniform
timing is the main reason hand-made sprite animation reads as stiff.

Typical rates: 8–12 FPS for retro pixel art, 24 for smoother modern 2D.

Scripted construction:

```python
import unreal

fac = unreal.PaperFlipbookFactory()
fb = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    'FB_Hero_Run', '/Game/Characters/Hero', unreal.PaperFlipbook, fac)
# Frames are set through the flipbook editor API or by authoring the asset in the editor;
# verify the frame count afterwards rather than assuming the factory filled it.
```

## 2. Hand-rolled state switching

For a small set of states, one function with one job:

```cpp
void AHero::UpdateAnimation()
{
    UPaperFlipbook* Desired = IdleFlipbook;

    if (!GetCharacterMovement()->IsMovingOnGround())
    {
        Desired = GetVelocity().Z > 0.0f ? JumpFlipbook : FallFlipbook;
    }
    else if (FMath::Abs(GetVelocity().X) > 10.0f)
    {
        Desired = RunFlipbook;
    }

    // Only assign on change: setting the same flipbook restarts it every frame.
    if (GetSprite()->GetFlipbook() != Desired)
    {
        GetSprite()->SetFlipbook(Desired);
    }
}
```

The guard is essential. `SetFlipbook` with the current flipbook resets playback to frame
zero, so without it a running character shows frame 0 forever and looks frozen.

Facing, on the XZ plane, is a yaw flip rather than a sprite swap:

```cpp
if (FMath::Abs(Velocity.X) > 1.0f)
{
    const float Yaw = Velocity.X > 0.0f ? 0.0f : 180.0f;
    GetSprite()->SetRelativeRotation(FRotator(0.0f, Yaw, 0.0f));
}
```

## 3. PaperZD when it grows

PaperZD adds an animation **source** per character, a state machine graph, notifies and
`PlayAnimationOverride` for one-shots. The structure that scales:

- **States**: Idle, Run, Jump, Fall, Attack, Hit, Death
- **Transitions** driven by a handful of exposed variables — `Speed`, `bGrounded`,
  `bAttacking` — not by reading the character directly from the graph
- **Notifies** for footsteps, hitbox enable/disable, and the frame a projectile spawns

```cpp
// Drive the state machine from one place, never from scattered call sites.
AnimInstance->SetSpeed(FMath::Abs(GetVelocity().X));
AnimInstance->SetGrounded(GetCharacterMovement()->IsMovingOnGround());
```

Keeping the animation layer reading *from* gameplay state, never writing *to* it, is what
stops animation bugs from becoming gameplay bugs.

## 4. One-shots over locomotion

An attack has to interrupt the locomotion state and give it back when done:

```cpp
void AHero::Attack()
{
    if (bAttacking) return;
    bAttacking = true;
    GetSprite()->SetFlipbook(AttackFlipbook);
    GetSprite()->SetLooping(false);
    GetSprite()->PlayFromStart();

    GetWorldTimerManager().SetTimer(AttackTimer, this, &AHero::EndAttack,
                                    AttackFlipbook->GetTotalDuration(), false);
}

void AHero::EndAttack()
{
    bAttacking = false;
    GetSprite()->SetLooping(true);
}
```

Guard `UpdateAnimation` with `if (bAttacking) return;` so locomotion does not overwrite
the attack on the next frame. In PaperZD this is `PlayAnimationOverride` with a completion
delegate, which is the same idea with the bookkeeping done for you.

## 5. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Animation stuck on frame 0 | `SetFlipbook` called every frame | Only assign on change |
| Attack animation never plays | Locomotion overwrites it next frame | Guard with a state flag |
| Frames misaligned after the first row | Sheet dimensions not divisible by the cell size | Re-cut the sheet |
| Animation reads as stiff | Uniform frame durations | Hold key poses 2–3 frames |
| Sprite faces the wrong way | Flipping the sprite asset instead of rotating | Yaw 180 on the component |
| Notify fires twice | Notify on a looping flipbook with no guard | Track the last fired frame |
| Flipbook plays too fast everywhere | FPS set on the asset, not the frames | Check both |

Related: [[sprite-sheet-packer]], [[ue2d-paper2d-foundations]],
[[ue2d-platformer-controller]], [[ue2d-hitboxes-and-combat]].
