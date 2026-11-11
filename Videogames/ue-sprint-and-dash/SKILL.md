---
name: ue-sprint-and-dash
description: Sprint, dash and burst movement for an Unreal Engine 5 character in C++ - hold-to-run speed switching, driving animation play rate from actual velocity so one walk clip covers every speed and the feet stop sliding, impulse and timed dash variants, cooldowns, i-frames, air control during a dash, and stamina gating. Use when adding a run or sprint key, a dash or dodge roll, when feet slide during locomotion, or when movement needs a burst that the standard character movement component does not provide.
---

# UE5 Sprint and Dash

Sprint is a speed change. Dash is a displacement with a cooldown. They share one problem:
the animation has to agree with what the movement component is actually doing, or the
feet slide and nothing feels grounded.

## Before you start

1. Decide whether you have separate clips. With a walk **and** a run, blend between them.
   With only a walk, drive the play rate (section 2) — that is a legitimate technique, not
   a workaround, and it fixes foot sliding for free.
2. Decide the dash shape: instant impulse, timed constant velocity, or a root-motion
   montage. They feel very different and need different code.
3. Confirm input is bound with `Started` / `Completed`, not `Triggered` — a sprint on
   `Triggered` re-applies the speed every frame and fights any other system touching it.

## 1. Hold to sprint

```cpp
void AMyCharacter::StartRunning(const FInputActionValue&)
{
    GetCharacterMovement()->MaxWalkSpeed = RunSpeed;    // e.g. 420
}

void AMyCharacter::StopRunning(const FInputActionValue&)
{
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;   // e.g. 160
}
```

Expose both as `UPROPERTY(EditAnywhere)` and set `MaxWalkSpeed = WalkSpeed` in the
constructor from the same variable, so the editor value and the runtime default cannot
drift apart.

For a smooth ramp instead of a step, interpolate in `Tick`:

```cpp
const float Target = bWantsToRun ? RunSpeed : WalkSpeed;
Movement->MaxWalkSpeed = FMath::FInterpTo(Movement->MaxWalkSpeed, Target, DeltaSeconds, 6.0f);
```

## 2. One clip, every speed: play rate from velocity

This is the part that makes a single walk cycle carry a sprint convincingly.

```cpp
const float Speed = GetVelocity().Size2D();
const bool bMoving = Speed > MoveThreshold && GetCharacterMovement()->IsMovingOnGround();

if (bMoving)
{
    // Stride matched to the ground: no foot sliding at any speed.
    const float Rate = FMath::Clamp(Speed / FMath::Max(1.0f, WalkSpeed), 0.6f, 2.6f);
    Mesh->SetPlayRate(Rate);

    if (!Mesh->IsPlaying())
    {
        Mesh->SetPosition(0.0f);
        Mesh->Play(true);
    }
}
else if (Mesh->IsPlaying())
{
    Mesh->Stop();
    Mesh->SetPlayRate(1.0f);
}
```

Three things worth noting:

- **Gate on velocity, not on the key.** It then also covers braking, knockback, conveyor
  belts and anything else that moves the character later.
- **`IsMovingOnGround()`** stops the walk cycle playing mid-jump, which otherwise looks
  like running through the air.
- **Clamp the rate.** Past roughly 2.6× a walk cycle stops reading as locomotion and
  starts reading as a glitch.

With a real run clip, blend on the same normalised speed instead — a 1D BlendSpace on
`Speed / RunSpeed`. See [[ue-character-movement]] for the AnimInstance plumbing.

## 3. Dash: pick a shape

| Shape | How | Feels like |
|-------|-----|-----------|
| **Impulse** | `LaunchCharacter` once | A shove; distance varies with friction and slope |
| **Timed velocity** | Hold a velocity for N seconds | Predictable distance; the usual choice |
| **Root motion** | A montage carries the movement | Most polished, needs the animation |

Timed velocity, which is predictable and needs no new animation:

```cpp
void AMyCharacter::Dash(const FInputActionValue&)
{
    if (bDashing || GetWorld()->GetTimeSeconds() < NextDashTime)
    {
        return;
    }

    // Dash where the player is steering, or straight ahead when standing still.
    FVector Direction = GetLastMovementInputVector().GetSafeNormal2D();
    if (Direction.IsNearlyZero())
    {
        Direction = GetActorForwardVector();
    }

    bDashing = true;
    DashDirection = Direction;
    NextDashTime = GetWorld()->GetTimeSeconds() + DashCooldown;

    UCharacterMovementComponent* Movement = GetCharacterMovement();
    CachedBrakingFriction = Movement->BrakingFrictionFactor;
    Movement->BrakingFrictionFactor = 0.0f;      // friction must not eat the dash

    GetWorldTimerManager().SetTimer(
        DashTimer, this, &AMyCharacter::EndDash, DashDuration, false);
}

void AMyCharacter::EndDash()
{
    bDashing = false;
    GetCharacterMovement()->BrakingFrictionFactor = CachedBrakingFriction;
}
```

and in `Tick`, while `bDashing`:

```cpp
GetCharacterMovement()->Velocity =
    DashDirection * DashSpeed + FVector(0.0f, 0.0f, GetCharacterMovement()->Velocity.Z);
```

Keeping the existing Z preserves gravity, so a dash off a ledge arcs instead of flying.

Starting values: `DashSpeed = 1800`, `DashDuration = 0.18`, `DashCooldown = 0.8`. Distance
is roughly `DashSpeed × DashDuration`, so about 320 uu — just under two character heights.

## 4. Cooldown, i-frames and stamina

```cpp
float GetDashCooldownRemaining() const
{
    return FMath::Max(0.0f, NextDashTime - GetWorld()->GetTimeSeconds());
}
```

Expose that for the HUD rather than letting the HUD keep its own clock — one source of
truth. See [[ue-canvas-hud]] for drawing it as a ring.

Invulnerability frames for a dodge: flip collision response to the damage channel for the
dash duration and restore it in `EndDash`, in the same place the friction is restored, so
the two cannot get out of sync.

Stamina gating is one more condition in the same early return. Keep it there rather than
scattering checks — a dash that can fail for three reasons should fail in one place.

## 5. Air dash

`CanDash()` deserves to be its own function the moment there is more than one rule:

```cpp
bool AMyCharacter::CanDash() const
{
    if (bDashing || GetWorld()->GetTimeSeconds() < NextDashTime) return false;
    if (!bAllowAirDash && !GetCharacterMovement()->IsMovingOnGround()) return false;
    if (Stamina < DashStaminaCost) return false;
    return true;
}
```

For an air dash, also zero the vertical velocity at the start, or an upward dash stacks
with jump velocity and launches the character far further than intended.

## 6. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Feet slide while sprinting | Play rate fixed at 1.0 | Drive it from `GetVelocity().Size2D()` |
| Walk cycle plays in mid-air | Gate checks speed only | Add `IsMovingOnGround()` |
| Dash barely moves | Braking friction eats the velocity | Zero `BrakingFrictionFactor` for the duration |
| Dash distance varies by surface | Impulse-based dash | Use timed velocity |
| Dash off a ledge flies flat | Z velocity overwritten | Preserve the existing Z |
| Sprint speed sticks after release | Bound to `Triggered` instead of `Started`/`Completed` | Rebind |
| Speed resets unexpectedly | Something else writes `MaxWalkSpeed` | Make one system own it |

Related: [[ue-character-movement]], [[ue-enhanced-input-cpp]], [[ue-third-person-camera]],
[[ue-timers-and-triggers]].
