---
name: ue-third-person-camera
description: Build a third person follow camera in Unreal Engine 5 from C++ - spring arm and camera components, control rotation versus actor rotation, camera-relative movement so WASD means what the player expects, orient-to-movement body turning, collision pull-in, and tuning lag, distance and shoulder offset. Covers why the camera appears frozen when only movement is bound, and the capsule/mesh offsets a non-mannequin character needs. Use when adding a follow camera, when movement goes the wrong way relative to the view, when the camera clips through walls, or when setting up a playable character from scratch. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Third Person Camera

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


A follow camera is two components and one rule: **the camera owns the control rotation,
the body follows the movement**. Get that relationship right and everything else is
tuning.

## Before you start

1. Decide the scheme. Third person action: body turns toward travel, camera orbits free.
   Over-the-shoulder shooter: body yaw locked to the camera. They need opposite flags.
2. Know your character's real height. The UE mannequin is 180 uu with an 88 uu capsule
   half height; an imported character is usually neither.
3. Input must already work. A camera with no look binding appears frozen — see section 5.

## 1. Components

```cpp
AMyCharacter::AMyCharacter()
{
    // Capsule sized to the actual mesh, not left at the mannequin default.
    GetCapsuleComponent()->InitCapsuleSize(34.0f, 85.0f);   // 170 uu character

    // Feet sit at the mesh pivot, so drop the mesh by the capsule half height.
    // The yaw lines the mesh's forward up with the actor's +X; measure it, do not guess.
    if (USkeletalMeshComponent* Mesh = GetMesh())
    {
        Mesh->SetRelativeLocationAndRotation(
            FVector(0.0f, 0.0f, -85.0f), FRotator(0.0f, -90.0f, 0.0f));
    }

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 400.0f;
    CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 90.0f);
    CameraBoom->bUsePawnControlRotation = true;    // the mouse orbits the boom

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false; // the boom already did the rotating
}
```

`bUsePawnControlRotation` on **both** is the single most common mistake: the camera then
applies the control rotation twice and the view doubles its pitch and yaw.

## 2. Who rotates: the three flags

```cpp
bUseControllerRotationYaw = false;     // the body does not snap to the camera
bUseControllerRotationPitch = false;
bUseControllerRotationRoll = false;

GetCharacterMovement()->bOrientRotationToMovement = true;
GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);
```

| Scheme | `bUseControllerRotationYaw` | `bOrientRotationToMovement` |
|--------|------------------------------|------------------------------|
| Third person action | `false` | `true` |
| Over-the-shoulder / aiming | `true` | `false` |
| Top-down, body faces cursor | `false` | `false`, rotate manually |

Setting both `true` fights itself: the body is told to face the camera and the travel
direction in the same frame, and it jitters.

## 3. Camera-relative movement

This is what makes WASD feel right. Project the input onto the **control rotation's yaw**,
never onto the actor's own axes:

```cpp
void AMyCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    if (!Controller || Axis.IsNearlyZero())
    {
        return;
    }

    // Yaw only. Including pitch tilts the movement plane and the character
    // walks into the floor when you look down.
    const FRotator YawOnly(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
    const FRotationMatrix Basis(YawOnly);

    AddMovementInput(Basis.GetUnitAxis(EAxis::X), Axis.X);   // W / S
    AddMovementInput(Basis.GetUnitAxis(EAxis::Y), Axis.Y);   // D / A
}
```

With `bOrientRotationToMovement`, the character then turns to face wherever that input
sent her — which is the behaviour players read as "correct" without being able to name it.

## 4. Look

```cpp
void AMyCharacter::Look(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    AddControllerYawInput(Axis.X * LookSensitivity);
    AddControllerPitchInput(-Axis.Y * LookSensitivity);   // screen Y is inverted
}
```

Pitch clamping is the `APlayerController`'s job, not yours: `ViewPitchMin` / `ViewPitchMax`
default to ±89°. Do not clamp again in the pawn, or the two limits fight at the extremes.

## 5. The camera that appears frozen

If you bind movement but not look, camera-relative movement still works — and it all
points one fixed way forever, because nothing ever changes the control rotation. The
symptom reported is "I can't turn" or "the camera is stuck", and the cause is a missing
look binding, not the camera setup. A follow camera is not finished until look is bound.

## 6. Collision, lag and feel

```cpp
CameraBoom->bDoCollisionTest = true;        // default; pulls in through geometry
CameraBoom->ProbeSize = 12.0f;

CameraBoom->bEnableCameraLag = true;
CameraBoom->CameraLagSpeed = 10.0f;         // lower is floatier
CameraBoom->bEnableCameraRotationLag = true;
CameraBoom->CameraRotationLagSpeed = 12.0f;
```

| Knob | Effect | Sane range |
|------|--------|-----------|
| `TargetArmLength` | Distance behind | 300–500 action, 150–250 over-the-shoulder |
| `SocketOffset.Z` | Height above the pivot | 60–120 |
| `SocketOffset.Y` | Shoulder offset | 0 action, 40–70 over-the-shoulder |
| `CameraLagSpeed` | Position smoothing | 8–15; below 5 feels seasick |
| `ProbeSize` | Collision probe radius | 10–15 |

Camera lag plus collision pull-in can interact badly in tight corridors: the lagged
target is still inside the wall while the probe pulls the camera in, which reads as
stutter. Reduce lag before reducing `ProbeSize`.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| View pitches and yaws twice as fast | `bUsePawnControlRotation` true on both boom and camera | Only on the boom |
| Camera never turns | No look action bound | Bind one; see [[ue-enhanced-input-cpp]] |
| Character walks into the floor when looking down | Movement basis uses full control rotation | Yaw only |
| Body jitters while moving | `bUseControllerRotationYaw` and `bOrientRotationToMovement` both true | Pick one |
| Character floats or sinks | Mesh relative Z does not match capsule half height | Set it to `-HalfHeight` |
| Camera inside the character's head | `TargetArmLength` too short or the boom is parented to the mesh | Parent the boom to `RootComponent` |
| Movement feels inverted | Mesh yaw offset wrong, so the body renders backwards while moving correctly | Measure the facing; see [[ue-character-import-pipeline]] |

Related: [[ue-enhanced-input-cpp]], [[ue-character-movement]], [[ue-sprint-and-dash]].
