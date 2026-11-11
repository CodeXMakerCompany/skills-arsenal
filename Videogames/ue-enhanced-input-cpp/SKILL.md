---
name: ue-enhanced-input-cpp
description: Wire Enhanced Input entirely from C++ in Unreal Engine 5, including building InputActions and an InputMappingContext in code so there are no input assets to keep in sync with the class. Covers the WASD swizzle/negate modifier recipe for a 2D axis, mouse look, press-and-hold actions like sprint, one-shot actions, and the ordering bug that silently kills every key - registering the mapping context in BeginPlay, before the pawn has a controller. Use when keys do nothing, when setting up player input for a character or pawn, or when choosing between input assets and code-built mappings.
---

# UE5 Enhanced Input from C++

Enhanced Input is normally driven by `UInputAction` and `UInputMappingContext` assets
wired up in a Blueprint. You can build both in code instead, which removes the class/asset
drift that bites when someone renames an asset and the binding quietly stops working.

## Before you start

1. Add `"EnhancedInput"` to `PublicDependencyModuleNames` in your `.Build.cs`.
2. Confirm the project is actually on Enhanced Input:
   `Config/DefaultInput.ini` should contain
   `DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput`.
   UE5 templates set this; a project converted from UE4 may not have it.
3. Decide assets vs code. Assets win when designers must rebind in the editor; code wins
   when the bindings belong to one class and nothing else should touch them. You can have
   both: expose the keys as `FKey` `UPROPERTY`s and build the context from them.

## 1. The bug that kills every key

Register the mapping context on **possession**, not in `BeginPlay`:

```cpp
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // WRONG. The pawn is not possessed yet, so GetController() is null, the whole
    // block is skipped, no mapping context is ever added and every key is dead.
    if (const APlayerController* PC = Cast<APlayerController>(GetController()))
    {
        /* ... AddMappingContext ... */
    }
}
```

`BeginPlay` runs when the pawn is spawned. Possession happens afterwards. There is no
warning — the `if` simply does not enter, and you are left debugging the bindings instead
of the registration. Use `NotifyControllerChanged`, which is called on possession:

```cpp
void AMyCharacter::NotifyControllerChanged()
{
    Super::NotifyControllerChanged();

    BuildInput();   // idempotent; see below

    if (const APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            Subsystem->AddMappingContext(MappingContext, /*Priority=*/0);
        }
    }
}
```

## 2. Building actions and mappings in code

Keep it in one idempotent function and call it from both `NotifyControllerChanged` and
`SetupPlayerInputComponent`, because their order is not guaranteed across spawn paths.

```cpp
void AMyCharacter::BuildInput()
{
    if (MoveAction)
    {
        return;   // already built
    }

    MoveAction = NewObject<UInputAction>(this, TEXT("IA_Move"));
    MoveAction->ValueType = EInputActionValueType::Axis2D;

    LookAction = NewObject<UInputAction>(this, TEXT("IA_Look"));
    LookAction->ValueType = EInputActionValueType::Axis2D;

    MappingContext = NewObject<UInputMappingContext>(this, TEXT("IMC_Player"));
    /* ... key mappings, below ... */
}
```

Hold every one of these in a `UPROPERTY(Transient)`. They are `NewObject`s with no other
referencer; without the `UPROPERTY` they are garbage collected and the bindings die at a
random later frame, which is a miserable bug to chase.

## 3. WASD into one 2D axis

A key press feeds `1.0` into **X**. Modifiers reshape that into the vector you want.
`Swizzle` defaults to `YXZ`, which moves the value from X into Y; `Negate` flips the sign.

```cpp
//   W -> ( 1,  0)      S -> (-1,  0)
//   D -> ( 0,  1)      A -> ( 0, -1)
MappingContext->MapKey(MoveAction, EKeys::W);

{
    FEnhancedActionKeyMapping& Back = MappingContext->MapKey(MoveAction, EKeys::S);
    Back.Modifiers.Add(NewObject<UInputModifierNegate>(this));
}
{
    FEnhancedActionKeyMapping& Right = MappingContext->MapKey(MoveAction, EKeys::D);
    Right.Modifiers.Add(NewObject<UInputModifierSwizzleAxis>(this));
}
{
    FEnhancedActionKeyMapping& Left = MappingContext->MapKey(MoveAction, EKeys::A);
    Left.Modifiers.Add(NewObject<UInputModifierNegate>(this));
    Left.Modifiers.Add(NewObject<UInputModifierSwizzleAxis>(this));
}

// Mouse2D already delivers a 2D delta and needs no modifier.
MappingContext->MapKey(LookAction, EKeys::Mouse2D);
```

Modifier order matters: for A, Negate runs first (X becomes -1), then Swizzle moves it to
Y. Reverse them and you get `(0, +1)`.

Requires `#include "InputModifiers.h"`.

## 4. Binding, and picking the right trigger event

```cpp
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    BuildInput();

    if (UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
        Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);

        // ACharacter already implements both halves of a jump.
        Input->BindAction(JumpAction, ETriggerEvent::Started,   this, &ACharacter::Jump);
        Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);

        // Hold to sprint.
        Input->BindAction(RunAction, ETriggerEvent::Started,   this, &AMyCharacter::StartRunning);
        Input->BindAction(RunAction, ETriggerEvent::Completed, this, &AMyCharacter::StopRunning);

        // Fire once per press, not once per frame.
        Input->BindAction(AttackAction, ETriggerEvent::Started, this, &AMyCharacter::Attack);
    }
}
```

| Event | Fires | Use for |
|-------|-------|---------|
| `Triggered` | Every frame the action is active | Movement, look |
| `Started` | Once, on the press | Jump, attack, dash, sprint on |
| `Completed` | Once, on the release | Stop jumping, sprint off |
| `Canceled` | The trigger gave up before completing | Hold-to-charge abandoned |

Binding movement to `Started` is the classic mistake: the character takes one step and
stops.

## 5. Reading the value

```cpp
void AMyCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    if (!Controller || Axis.IsNearlyZero())
    {
        return;
    }

    // Yaw only: pitch must never tilt the movement plane.
    const FRotator YawOnly(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
    const FRotationMatrix Basis(YawOnly);

    AddMovementInput(Basis.GetUnitAxis(EAxis::X), Axis.X);
    AddMovementInput(Basis.GetUnitAxis(EAxis::Y), Axis.Y);
}
```

`Value.Get<T>()` must match the action's `ValueType`. Asking a Boolean action for a
`FVector2D` returns zero rather than failing, so a wrong `ValueType` presents as "the key
does nothing".

## 6. Rebindable keys without assets

Expose the keys and build the context from them. Designers still rebind in the details
panel, and there is still no asset to lose:

```cpp
UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
FKey ForwardKey = EKeys::W;

UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
FKey RunKey = EKeys::LeftShift;
```

Changing a key at runtime means rebuilding the context and re-adding it; the mapping is
read when the context is registered, not per frame.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Every key dead, camera still moves | Mapping context registered in `BeginPlay` | Move it to `NotifyControllerChanged` |
| Keys work, then stop after a while | `UInputAction` / `UInputMappingContext` not held in a `UPROPERTY` | Add `UPROPERTY(Transient)` |
| A/D move forward and back | Swizzle missing, or ordered after Negate | Negate then Swizzle |
| Character moves one step per press | Movement bound to `Started` | Use `Triggered` |
| Action fires every frame while held | One-shot bound to `Triggered` | Use `Started` |
| Value always zero | `ValueType` does not match `Value.Get<T>()` | Match them |
| Nothing at all, no errors | Project is not on `EnhancedPlayerInput` | Check `DefaultInput.ini` |

Related: [[ue-cpp-module-bootstrap]], [[ue-third-person-camera]], [[ue-sprint-and-dash]],
[[ue-character-movement]].
