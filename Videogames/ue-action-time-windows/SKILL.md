---
name: ue-action-time-windows
description: Time windows for Unreal Engine 5 action games - startup, active and recovery in milliseconds, input buffer, cancel windows, hitstop and invulnerability, sampled from montage position so a missed notify does not drop the move. Use when building melee or action combat, when attacks hit too early or too late, when a cancel feels random, or when frame data lives in Tick booleans. On UE 5.8, author the montage and notifies through Unreal MCP. The window numbers stay in data. Pairs with ue-anim-montages-notifies, ue-combo-systems and ue-gas-abilities. For 2D Paper2D collision setup use ue2d-hitboxes-and-combat.
---

# Action time windows

A move is three spans of time, plus the spans during which the player may do something else. Those spans are data in milliseconds. They are not booleans flipped in `Tick` because the animation "looks about right".

Startup: the move has begun and cannot hit.
Active: the hitbox is on, or the projectile may spawn.
Recovery: the hitbox is off and the body is still committed, except where a cancel window says otherwise.

Author the montage and its notify states through `unreal-mcp`. The numbers below live on the move's data asset so gameplay can sample them even when the mesh is not drawing.

## The clock

Sample `UAnimInstance::Montage_GetPosition` (seconds) on the montage that was played for this move. Convert to milliseconds. Compare to the windows on the move asset.

Do not open the hitbox from an AnimBP event graph, and do not use wall-clock `GetTimeSeconds` for a window that is supposed to match the animation. A hitched frame then lands the hit at the wrong pose. Montage position stays with the pose.

Notify states are a sync aid and a way for designers to see the span on the montage. The data asset is the authority. If a notify is skipped because the skeleton did not tick, the sample from montage position still opens and closes the window. If you later prove the notify and the data disagree, fix the data or the montage. Do not let both be authority.

Lock the design to a tick you can explain (for example a 60 Hz simulation, so 1 frame is about 16.7 ms). Store milliseconds anyway. Frame counts go stale the moment the game runs at another rate.

## What to store on the move

| Field | Meaning |
|-------|---------|
| `StartupMs`, `ActiveMs`, `RecoveryMs` | The three spans, in order. Active begins when startup ends. |
| `CancelWindows` | List of `{StartMs, EndMs, AllowedMoveTags}`. Empty means no cancel. |
| `BufferOpenMs` | How early the next input is remembered. Often the last part of recovery, sometimes a few frames before the move is even legal. |
| `InvulnMs` | Optional span where the hurtbox is off. |
| `HitstopMs` | Freeze applied on a confirmed hit. Typical starting point 60–100 ms. Tune it. Do not leave it at 0 and call the hit "meaty". |

`Startup + Active + Recovery` equals the committed length of the move. A montage that is longer than that is still playing after the gameplay move ended, and something else will cut it off. Make them match, or document the extra tail as cosmetic.

## Buffer

Store at most one desired next move, with the time it was pressed. Accept it only if `now - pressed <= BufferMs` and the move is legal (a combo edge, or neutral). A buffer that never expires turns a mis-press from a second ago into an attack. A buffer of zero drops inputs that arrived one frame early, which players read as "the button does nothing".

Jump coyote time and jump buffering in `ue2d-platformer-controller` are the same idea for jumps. Do not invent a second, conflicting buffer for the jump key inside this system.

## Cancels

A cancel is an edge, not a special case in `Tick`. It is legal when montage position is inside a `CancelWindow` and the desired move's tag is in that window's set. Whiff and hit can use different windows. Say which in the data (`bOnlyOnHit`). There is no third hidden rule in C++.

Leaving the window closes it the same frame. Do not leave a cancel open until recovery ends "to feel better" without writing that span down. The written span is what you can tune.

## Hitstop

On a confirmed hit, pause the attacker's montage and the defender's relevant montage for `HitstopMs`, then resume. Pause both or the poses diverge and the next active frame is a lie. Do not pause the whole world unless the design is a full-game hit pause and you have listed what else freezes (projectiles, timers, UI).

Hitstop is presentation of a hit that already landed. It does not extend the active window. Sample windows with a clock that does not advance during hitstop, or the active frames slide later on every hit.

## Invulnerability

If the design has throw invuln or dodge i-frames, it is a span on the dodge move, and the hurtbox (or the damage interface) checks that span. A bool `bInvulnerable` set in `BeginPlay` of the dodge and cleared "after a delay" will drift from the animation. Use the same millisecond sample.

## Multi-hit

One active window deals one hit per target unless the move says otherwise. A `TSet` of actors already hit, cleared when the active window opens. A multi-hit move stores a list of sub-windows, each with its own clear. Do not rely on the overlap event firing once. It will not.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hit lands after the swing | Active is a `Tick` bool, or a timer from `PlayMontage` | Sample montage position against data |
| Window never opens off screen | Notify was the only authority and the mesh stopped ticking | Data plus montage position |
| Cancel feels random | Extra condition in C++ | Only the window and the tag set |
| Button "does nothing" | Buffer is 0 | Open a real buffer span and show it in the data |
| Hits add extra active time | Hitstop advanced the combat clock | Freeze the sample clock with the montage |
| One swing hits twice | No per-target set for this active span | Clear the set when the span opens |

Related: `ue-anim-montages-notifies`, `ue-combo-systems`, `ue-gas-abilities`, `ue2d-hitboxes-and-combat`.
