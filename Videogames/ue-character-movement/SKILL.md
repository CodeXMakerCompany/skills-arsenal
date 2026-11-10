---
name: ue-character-movement
description: Production patterns for Unreal Engine 5 character locomotion - UCharacterMovementComponent, movement modes and custom states, AnimInstance data flow, BlendSpaces, root motion, and network prediction. Use when creating or modifying player or AI movement, sprint/crouch/dodge/climb states, or locomotion animation setups, in C++ or Blueprint.
---

# UE5 Character Movement & Locomotion

Patterns for wiring `ACharacter`, `UCharacterMovementComponent` (CMC) and `UAnimInstance` together so movement is responsive, replicated correctly and cheap to animate. Applies to player and AI characters alike.

## Before you start

1. Check the engine version (`.uproject` `EngineAssociation`). Pattern availability differs (e.g. `TObjectPtr`, Mover plugin, Control Rig locomotion).
2. Find the module API macro (`YOURMODULE_API`) and the existing base character/anim classes. Extend them, do not add a parallel hierarchy.
3. Decide the layer for each concern:

| Concern | Lives in |
|---------|----------|
| Speed limits, acceleration, braking, gravity, jump | CMC properties (data) |
| Movement state that changes physics (sprint, crouch, climb, slide) | CMC (custom mode or saved-move flag) |
| Input mapping, intent | Controller / Pawn (Enhanced Input) |
| Pose selection, blending | AnimInstance + AnimGraph |

Rule: gameplay state is owned by the character/CMC. The AnimInstance only reads it.

## 1. Character setup

- `ACharacter` already owns the CMC. Use `GetCharacterMovement()`. Caching a pointer is only worth it for a custom CMC subclass, and then cache it once in the constructor or `PostInitializeComponents()`.
- To use a custom CMC, swap it in the constructor:

```cpp
ABaseCharacter::ABaseCharacter(const FObjectInitializer& OI)
    : Super(OI.SetDefaultSubobjectClass<UBaseCharacterMovementComponent>(
          ACharacter::CharacterMovementComponentName))
{
}
```

- Expose read-only state to Blueprint; keep writes behind functions so replication and validation stay in one place.
- Tune via data, not code: `MaxWalkSpeed`, `MaxAcceleration`, `BrakingDecelerationWalking`, `GroundFriction`, `JumpZVelocity`, `AirControl`, `RotationRate`, `bOrientRotationToMovement` vs `bUseControllerDesiredRotation`.

```cpp
// Public/Core/BaseCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "BaseCharacter.generated.h"

UCLASS(Abstract)
class YOURMODULE_API ABaseCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ABaseCharacter(const FObjectInitializer& ObjectInitializer);

    UFUNCTION(BlueprintPure, Category = "Movement")
    float GetGroundSpeed() const;

    UFUNCTION(BlueprintPure, Category = "Movement")
    bool IsInAir() const;
};
```

```cpp
float ABaseCharacter::GetGroundSpeed() const
{
    return GetVelocity().Size2D();   // ignore vertical component
}

bool ABaseCharacter::IsInAir() const
{
    const UCharacterMovementComponent* MoveComp = GetCharacterMovement();
    return MoveComp && MoveComp->IsFalling();
}
```

## 2. Movement states and custom modes

Choose the lightest mechanism that fits:

| Need | Approach |
|------|----------|
| Change speed only (walk/run/aim) | Set `MaxWalkSpeed` from a replicated state; it must change identically on client and server |
| Crouch / prone | Built-in `Crouch()` / `UnCrouch()`, `bCanCrouch`, `CrouchedHalfHeight` |
| New physics (climb, swim variant, wall-run, slide) | `MOVE_Custom` + `CustomMovementMode`, implement `PhysCustom()` |
| Action that overrides movement for a short time (dash, dodge) | Root motion source or root-motion montage |

Rules:
- Custom modes: define a `UENUM` for sub-modes, switch with `SetMovementMode(MOVE_Custom, SubMode)`, and handle transitions in `OnMovementModeChanged()`.
- Movement-affecting input (sprint, dash) on a networked player must go through the CMC's saved-move flow (`FSavedMove_Character`, `GetCompressedFlags`, `UpdateFromCompressedFlags`, `FNetworkPredictionData_Client_Character`). Setting `MaxWalkSpeed` on the client only from an RPC causes corrections and rubber-banding.
- Never move the actor by `SetActorLocation` every tick for locomotion. It bypasses collision, floor handling and prediction.
- Use `AddMovementInput` (or the AI path-following request) as the single entry point for intent.

## 3. AnimInstance data flow

- Compute locomotion variables from cached data, not by calling into gameplay code each frame.
- `NativeInitializeAnimation()`: cache `TObjectPtr<ABaseCharacter>` and its CMC (`TryGetPawnOwner()` can be null in editor previews, always null-check).
- `NativeUpdateAnimation()` (game thread): safe to read the owner and CMC; copy values into plain members.
- `NativeThreadSafeUpdateAnimation()` (worker thread, needs "Use Multi-threaded Animation Update"): only touch members of the AnimInstance. Do not call `UObject` getters, spawn, or read components here unless the call is marked thread safe. Feed it from values copied on the game thread.
- Keep per-frame work to arithmetic. No traces, no casts in the update, no allocations.

```cpp
// Public/Animation/BaseAnimInstance.h
UCLASS()
class YOURMODULE_API UBaseAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
    virtual void NativeThreadSafeUpdateAnimation(float DeltaSeconds) override;

protected:
    UPROPERTY(Transient)
    TObjectPtr<ABaseCharacter> OwnerCharacter;

    UPROPERTY(Transient)
    TObjectPtr<UCharacterMovementComponent> MovementComp;

    // Copied on the game thread
    FVector CachedVelocity = FVector::ZeroVector;
    FVector CachedAcceleration = FVector::ZeroVector;
    FRotator CachedActorRotation = FRotator::ZeroRotator;
    bool bCachedFalling = false;

    // Consumed by the AnimGraph
    UPROPERTY(BlueprintReadOnly, Category = "Movement Data", meta = (BlueprintThreadSafe))
    float GroundSpeed = 0.f;

    UPROPERTY(BlueprintReadOnly, Category = "Movement Data", meta = (BlueprintThreadSafe))
    float Direction = 0.f;   // -180..180, relative to actor facing

    UPROPERTY(BlueprintReadOnly, Category = "Movement Data", meta = (BlueprintThreadSafe))
    bool bShouldMove = false;

    UPROPERTY(BlueprintReadOnly, Category = "Movement Data", meta = (BlueprintThreadSafe))
    bool bIsFalling = false;
};
```

```cpp
void UBaseAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    OwnerCharacter = Cast<ABaseCharacter>(TryGetPawnOwner());
    MovementComp = OwnerCharacter ? OwnerCharacter->GetCharacterMovement() : nullptr;
}

void UBaseAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    if (!OwnerCharacter || !MovementComp) { return; }

    CachedVelocity = MovementComp->Velocity;
    CachedAcceleration = MovementComp->GetCurrentAcceleration();
    CachedActorRotation = OwnerCharacter->GetActorRotation();
    bCachedFalling = MovementComp->IsFalling();
}

void UBaseAnimInstance::NativeThreadSafeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeThreadSafeUpdateAnimation(DeltaSeconds);

    GroundSpeed = CachedVelocity.Size2D();
    bIsFalling = bCachedFalling;
    // Accelerating or still moving; avoids idle flicker on single-frame input gaps
    bShouldMove = GroundSpeed > 3.f && !CachedAcceleration.IsNearlyZero();
    Direction = UKismetAnimationLibrary::CalculateDirection(CachedVelocity, CachedActorRotation);
}
```

Blueprint-only projects: do the same split. Use "Blueprint Thread Safe Update Animation" for math and "Event Blueprint Update Animation" only to copy values from the owner.

## 4. BlendSpaces

Match axes to what the character can actually do, and keep sample points aligned with real speeds from the CMC.

- 1D (Speed): `0` idle, then walk, then run (for example `0 / 200 / 600`). Set the max axis value to the highest `MaxWalkSpeed` you ship.
- 2D (Direction, Speed): Direction `-180..180`, Speed `0..MaxSpeed`. Use for strafing with `bUseControllerDesiredRotation`. For `bOrientRotationToMovement` characters, a 1D speed blend plus turn-in-place is usually enough.
- Enable "Loop" and sync groups (or sync markers) on locomotion cycles so foot phases stay aligned across blends.
- Set axis smoothing (interpolation time) in the BlendSpace, not in per-frame code.
- Check foot sliding at each sample speed. Author or scale animations to the real velocity.
- Add start, stop and pivot as separate states or use Motion Matching when quality targets justify it.

## 5. Root motion

- Default for locomotion: velocity-driven (in-place animations). The CMC decides motion, animation follows.
- Root motion for authored actions only: attacks with lunges, dodges, rolls, vaults, climbs, hit reactions.
- Play root-motion montages through the CMC-aware path (montage with root motion enabled, `RootMotionMode = RootMotionFromMontagesOnly`). On networked games, run them on both server and owning client so the CMC can reconcile.
- Gameplay-driven pushes (dash, knockback, leap): prefer `FRootMotionSource` (`ConstantForce`, `MoveToForce`, `JumpForce`) via `ApplyRootMotionSource`. They are prediction-aware, unlike direct velocity writes.
- Do not mix root-motion and velocity-driven motion in the same state without a defined handoff.

## 6. AI characters

- Drive AI with the same CMC: path following issues move input, so animation code works unchanged.
- Set AI-specific speeds on the character data, not by editing animation.
- Use `bUseRVOAvoidance` / detour crowd avoidance sparingly; test with crowd sizes you actually ship.
- Reduce cost for distant or numerous characters: Animation Budget Allocator, URO (update rate optimization), `VisibilityBasedAnimTickOption`, and lower CMC tick rates where acceptable.

## 7. Networking checklist

- Server authoritative: client prediction through CMC saved moves, not through Actor replication of location.
- State that affects movement: flag in compressed flags or replicate with `OnRep` plus a CMC-side check.
- Cosmetic-only state (look direction, lean): replicate low frequency or derive from existing replicated data (`GetBaseAimRotation()`).
- Test with `Net PktLag=100 PktLoss=2` and watch for corrections (`p.NetShowCorrections 1`).

## 8. Common failures

| Symptom | Likely cause |
|---------|--------------|
| Rubber-banding on sprint | Speed changed on client without saved-move flag |
| Anim twitching at idle | `bShouldMove` derived from velocity only; use acceleration or hysteresis |
| Sliding feet | BlendSpace samples not matching real speeds; no sync markers |
| Crash in anim update | Non-thread-safe call in `NativeThreadSafeUpdateAnimation`, or null owner in editor preview |
| Character jitters on slopes/stairs | `MaxStepHeight`, `WalkableFloorAngle` or capsule size not tuned |
| Double movement with root motion | Velocity input still applied during a root-motion action |

## 9. Verify

- Compile the editor target and confirm no new warnings in the module.
- PIE with 2 clients plus dedicated server (`Net Mode: Play As Client`) for any change that touches movement state.
- Debug tools: `showdebug animation`, `showdebug character`, `p.NetShowCorrections 1`, `stat anim`.
