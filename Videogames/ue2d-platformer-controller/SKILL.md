---
name: ue2d-platformer-controller
description: A 2D platformer character controller in Unreal Engine 5 that feels right - plane-constrained movement, asymmetric jump gravity, variable jump height on button release, coyote time, jump buffering, apex hang, ledge nudging and one-way platforms. Covers the tuning numbers that make a jump read as responsive and why each forgiveness mechanic exists. Use when building a platformer character, when jumping feels floaty, heavy or unresponsive, or when players complain that jumps "don't register".
---

# UE5 2D Platformer Controller

Platformer feel is almost entirely forgiveness mechanics. The raw physics is twenty lines;
the difference between "unresponsive" and "tight" is coyote time, jump buffering and
asymmetric gravity.

> Written from general platformer practice rather than verified end to end in one
> Unreal project. The numbers assume 1 pixel = 1 unreal unit.

## Before you start

1. **Constrain the plane** or the character drifts in depth on any angled collision.
2. **Decide the jump by its shape, not its velocity**: how high, and how long to the apex.
   Derive gravity and velocity from those (section 2).
3. **Budget for forgiveness.** Players do not notice coyote time; they notice its absence.

## 1. Plane constraint and base setup

```cpp
AHero::AHero()
{
    UCharacterMovementComponent* Move = GetCharacterMovement();
    Move->SetPlaneConstraintEnabled(true);
    Move->SetPlaneConstraintNormal(FVector(0.0f, 1.0f, 0.0f));   // lock Y, play on XZ

    Move->bOrientRotationToMovement = false;    // facing is a sprite flip, not a rotation
    Move->bConstrainToPlane = true;
    Move->bSnapToPlaneAtStart = true;

    Move->MaxWalkSpeed = 300.0f;
    Move->GroundFriction = 8.0f;
    Move->MaxAcceleration = 2400.0f;            // high: platformers want instant response
    Move->BrakingDecelerationWalking = 2400.0f;
    Move->AirControl = 0.9f;                    // near full air control is normal in 2D
}
```

Low `MaxAcceleration` is the usual cause of "sluggish" ground movement. A platformer is
not a simulation: reaching full speed in two frames is correct.

## 2. Jump arc from shape, not guesswork

Pick the height and the time to apex, then solve:

```
gravity          = 2 * JumpHeight / (TimeToApex ^ 2)
initial velocity = gravity * TimeToApex
```

For a 120 uu jump with a 0.35 s rise: gravity ≈ 1959, velocity ≈ 686.

```cpp
const float Gravity = 2.0f * JumpHeight / FMath::Square(TimeToApex);
Move->JumpZVelocity = Gravity * TimeToApex;
Move->GravityScale  = Gravity / 980.0f;        // 980 is UE's default
```

Now tuning is in units a designer can describe — "a bit higher", "snappier" — instead of
two numbers that interact.

## 3. Asymmetric gravity

Falling faster than rising is the single biggest feel improvement:

```cpp
void AHero::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    UCharacterMovementComponent* Move = GetCharacterMovement();
    const float VelZ = GetVelocity().Z;

    if (VelZ < 0.0f)
    {
        Move->GravityScale = BaseGravityScale * FallMultiplier;      // ~1.9
    }
    else if (VelZ > 0.0f && !bJumpHeld)
    {
        Move->GravityScale = BaseGravityScale * LowJumpMultiplier;   // ~2.5, variable height
    }
    else
    {
        Move->GravityScale = BaseGravityScale;
    }
}
```

The second branch is variable jump height: release early and the rise is cut short, so a
tap is a small hop and a hold is a full jump — from one jump, with no second input.

**Apex hang**, optional but loved: scale gravity down to about 0.6 while `|VelZ|` is under
roughly 80, giving a brief float at the top that makes mid-air aiming feel fair.

## 4. Coyote time and jump buffering

These two account for most "the jump didn't register" complaints.

```cpp
// Coyote: still jumpable shortly after walking off an edge.
if (Move->IsMovingOnGround())
{
    CoyoteTimer = CoyoteTime;        // ~0.10 s
}
else
{
    CoyoteTimer = FMath::Max(0.0f, CoyoteTimer - DeltaSeconds);
}

// Buffer: a jump pressed just before landing still fires.
JumpBufferTimer = FMath::Max(0.0f, JumpBufferTimer - DeltaSeconds);

if (JumpBufferTimer > 0.0f && (Move->IsMovingOnGround() || CoyoteTimer > 0.0f))
{
    Jump();
    JumpBufferTimer = 0.0f;
    CoyoteTimer = 0.0f;
}
```

where the input handler only records intent:

```cpp
void AHero::OnJumpPressed()  { JumpBufferTimer = JumpBufferTime; bJumpHeld = true; }   // ~0.12 s
void AHero::OnJumpReleased() { bJumpHeld = false; StopJumping(); }
```

Both windows in the 0.08–0.15 s range. Past about 0.2 s players start noticing the game
jumping on its own.

## 5. Ledge nudging and one-way platforms

**Ledge nudge**: when a jump clips a corner, sweep a short horizontal test and offset the
character by a few units instead of killing the jump. Without it, players feel they were
robbed by a pixel.

**One-way platforms**: give them their own collision channel that the character blocks
only while falling.

```cpp
const bool bFalling = GetVelocity().Z <= 0.0f && !bDropRequested;
GetCapsuleComponent()->SetCollisionResponseToChannel(
    ECC_OneWayPlatform, bFalling ? ECR_Block : ECR_Overlap);
```

Drop-through is then "press down + jump sets `bDropRequested` for 0.2 s".

## 6. Starting numbers

| Property | Value | Note |
|----------|-------|------|
| `MaxWalkSpeed` | 300 | Run, before any sprint |
| `MaxAcceleration` | 2400 | Deliberately high |
| `GroundFriction` | 8 | Lower for ice |
| `AirControl` | 0.9 | 2D expects near-full control |
| `JumpHeight` | 120 | ~3.5 tiles at 32 px |
| `TimeToApex` | 0.35 s | |
| `FallMultiplier` | 1.9 | Fall faster than rise |
| `LowJumpMultiplier` | 2.5 | Variable height |
| `CoyoteTime` | 0.10 s | |
| `JumpBufferTime` | 0.12 s | |

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| "My jump didn't register" | No coyote time or buffer | Add both |
| Jump feels floaty | Symmetric gravity | `FallMultiplier` around 1.9 |
| Every jump is maximum height | No variable height | Scale gravity while rising unheld |
| Movement sluggish | `MaxAcceleration` too low | Raise to ~2400 |
| Character drifts in depth | No plane constraint | Constrain the Y normal |
| Jumps clip corners and die | No ledge nudge | Sweep and offset |
| Falls through one-way platforms while rising | Single collision response | Separate channel, flip by velocity |
| Air control feels wrong | Using 3D defaults | 2D wants 0.8–1.0 |

Related: [[ue2d-paper2d-foundations]], [[ue2d-flipbook-animation]], [[ue2d-camera-2d]],
[[ue-enhanced-input-cpp]].
