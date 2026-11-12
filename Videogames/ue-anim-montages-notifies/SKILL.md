---
name: ue-anim-montages-notifies
description: Play one-shot animation in Unreal Engine 5 with montages - sections, slots, blend in and out, AnimNotify versus AnimNotifyState, and branch notifies for moments that must line up with gameplay. Use when an attack, dodge, hit reaction or emote should play once, when a looping AnimBP is fighting a one-shot, or when a notify never fires. On UE 5.8, create the montage and the notifies through Unreal MCP animation toolsets. Window authority lives in ue-action-time-windows.
---

# Montages and notifies

A montage is one shot: an attack, a dodge, a hit reaction, an emote. Looping locomotion stays in the AnimBP state machine. Playing a one-shot by setting a bool the AnimBP might blend away is how attacks get cut off by a walk cycle.

Create and section the montage through the animation toolset after `describe_toolsets`. The runtime below is C++ or Blueprint on the character.

## Play it on a slot

The skeleton's AnimBP has a slot node (commonly `DefaultSlot` or an upper-body slot) on the blend path that is allowed to override the body. `PlayAnimMontage` / `Montage_Play` targets that slot.

- Full-body attacks use a slot that overrides the whole pose.
- Attacks that should keep the legs use an upper-body slot and a layered blend. Do not full-body an upper-body swing or the character plants their feet in the air.
- Blend-in shorter than the startup makes the swing pop. Blend-out during the active window makes the hitbox lie about the pose. Match blend to the spans in `ue-action-time-windows`, or keep blends short and outside the active span.

Stop the montage on interrupt (stun, death, cancel into another move) with `Montage_Stop` or by playing the next montage on the same slot. Leaving the old one running blends two attacks.

## Sections

Name sections for the gameplay spans: `Startup`, `Active`, `Recovery`, and one section per extra hit if the move is a multi-hit. Branching points are how a combo links to the next section without restarting from zero. The combo graph in `ue-combo-systems` decides whether the branch is taken. The montage only contains the section.

`Montage_GetPosition` is the clock the windows sample. Section names are for jumps and for designers. Do not parse the section name in `Tick` to decide if the hitbox is on.

Root motion: decide per move. A dash that must move the capsule uses root motion, and the movement component is told to accept it for that montage only. An attack that must not slide leaves root motion off. Do not enable it on the mesh globally because one move needed it.

## Notifies

| Kind | Use |
|------|-----|
| `AnimNotify` | A point: spawn a projectile, play a whoosh, footstep. Missing one is cosmetic or is retried from data. |
| `AnimNotifyState` | A span a designer can see on the timeline: trail VFX, the drawn active window. Begin and end match the data span. |
| Branching-point notify | A moment that must occur at that animation time even when the montage is about to branch. Use it sparingly. |

Gameplay-critical windows are still the millisecond fields on the move asset, sampled from montage position. A notify state that enables a hitbox is a second writer. Prefer the sample. Use the notify state to drive VFX and to show the designer the same span. If you do enable collision from a notify, the data sample is still allowed to force it closed, so a stuck notify cannot leave the hitbox on.

Notifies do not run if the skeletal mesh stops ticking. That includes "animation not rendered" on some setups. Do not put the only copy of "spawn the projectile" in a notify on a mesh that can be off screen, unless you have set the mesh to update when not rendered and you have checked it. Spawning from the data clock avoids that class of bug.

## What the AnimBP is allowed to do

Blend locomotion. Read a tag or a speed. It does not `ApplyDamage` from a transition. It does not own combo state. See `ue-state-machines`.

One-shot and locomotion fight when both write the same slot. The montage wins while it plays. Guard movement code so it does not also call `PlayAnimation` on that mesh for the same interval.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Attack blends back to idle mid-swing | Played as an AnimBP state with a weak condition | Montage on a slot |
| Legs freeze during a jab | Full-body slot | Upper-body slot |
| Next combo restarts the whole swing | No section branch, `Montage_Play` from time 0 | Branch to the next section |
| Notify never fires | Mesh not ticking, or the play position skipped the frame | Sample the data clock. Check update-when-not-rendered only if you still need the notify |
| Character slides on every attack | Root motion left on for the mesh | Enable it per montage that is a real displacement |
| Hitbox stays on | Notify end did not run | Data clock closes the window |

Related: `ue-action-time-windows`, `ue-combo-systems`, `ue-state-machines`, `ue-procedural-animation`.
