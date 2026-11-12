---
name: ue-timers-and-triggers
description: Timers and collision triggers in Unreal Engine 5 C++ - FTimerManager for looping waves, one-shot delays and cooldowns instead of counting down in Tick, the void signature requirement, clearing timers in EndPlay, exposing remaining time to a HUD, and overlap setup for pickups and trigger volumes including the collision response rules that decide whether an overlap fires at all. Use when adding a wave timer, a cooldown, a pickup the player walks into, a trigger volume, or when an overlap event never fires. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Timers and Triggers

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Two systems that account for most "it didn't happen" bugs: work scheduled on a clock, and
work fired by actors touching. Both fail silently when set up wrong, which is why the
rules below are worth knowing exactly rather than approximately.

## Before you start

1. **If you are counting down a float in `Tick`, you want a timer.** `Tick` is for work
   that must happen every frame; a 20 second wave is not that.
2. **Decide blocking or overlapping.** A pickup that stops the player is a bug; a wall
   that the player walks through is a different bug. They are different collision setups.
3. **Know who destroys what.** A pickup that destroys itself and a spawner that tracks it
   must agree, or you get dangling references.

## 1. Timers instead of Tick

```cpp
// Looping
GetWorldTimerManager().SetTimer(
    BatchTimer, this, &AMyActor::HandleBatchTimer, Interval, /*bLoop=*/true);

// One shot
GetWorldTimerManager().SetTimer(
    OneShotTimer, this, &AMyActor::EndAction, Duration, false);

// Lambda, when the work is trivial and local
FTimerHandle Handle;
GetWorldTimerManager().SetTimer(Handle, [this]()
{
    SetActorHiddenInGame(false);
}, 0.5f, false);
```

**The handler must be `void()`.** A function returning anything will not compile against
`SetTimer`, with an error that points at the overload set rather than at your signature.
When the function is useful to callers with a return value, keep it and add a wrapper:

```cpp
int32 AMySpawner::GenerateRandomRewards();     // real API, returns a count

void AMySpawner::HandleBatchTimer()            // timer entry point
{
    ++DifficultyMultiplier;
    GenerateRandomRewards();
}
```

That wrapper is also the natural home for per-loop side effects — difficulty, analytics,
a sound — keeping them out of the function that callers and tests use.

## 2. Always clear in EndPlay

```cpp
void AMyActor::EndPlay(const EEndPlayReason::Type Reason)
{
    GetWorldTimerManager().ClearTimer(BatchTimer);
    Super::EndPlay(Reason);
}
```

Timers live on the world. A timer left set when the actor goes away is a callback into a
destroyed object; in PIE it usually shows up as a crash on the *second* play, which is
exactly when you are not thinking about timers.

## 3. Useful queries

```cpp
GetWorldTimerManager().GetTimerRemaining(BatchTimer);   // < 0 when not running
GetWorldTimerManager().GetTimerElapsed(BatchTimer);
GetWorldTimerManager().IsTimerActive(BatchTimer);
GetWorldTimerManager().PauseTimer(BatchTimer);
```

Expose remaining time from the owner rather than letting a HUD run its own clock:

```cpp
float AMySpawner::GetSecondsUntilNextBatch() const
{
    const float Remaining = GetWorldTimerManager().GetTimerRemaining(BatchTimer);
    return Remaining > 0.0f ? Remaining : 0.0f;
}
```

Two clocks drift. One source of truth cannot.

## 4. Cooldowns without a timer

For a cooldown you only ever *query*, a timestamp is simpler than a timer and needs no
handle, no clearing and no callback:

```cpp
if (GetWorld()->GetTimeSeconds() < NextDashTime) return;
NextDashTime = GetWorld()->GetTimeSeconds() + DashCooldown;
```

Use a timer when something must *happen* at the end, a timestamp when something merely
becomes *allowed*.

## 5. Overlap triggers: the rules that decide whether it fires

An overlap needs three things to be true, and the third is the one people miss:

1. Both components have collision enabled (`QueryOnly` is enough).
2. **At least one** has `SetGenerateOverlapEvents(true)`.
3. Their mutual response resolves to Overlap, not Ignore.

The response is the **weaker** of the two: `Ignore` beats `Overlap` beats `Block`. So a
`Block` on one side and `Overlap` on the other produces an overlap, but an `Ignore` on
either side produces nothing at all. A pickup that "doesn't work" is almost always an
`Ignore` on one side.

```cpp
// A pickup: notices the player, never pushes her.
MeshComp->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
MeshComp->SetCollisionObjectType(ECC_WorldDynamic);
MeshComp->SetCollisionResponseToAllChannels(ECR_Ignore);
MeshComp->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
MeshComp->SetGenerateOverlapEvents(true);
```

`QueryOnly` matters: with `QueryAndPhysics` the pickup participates in physics and can
shove the character off a ledge.

## 6. Handling the overlap

```cpp
// Header - UFUNCTION is required for the dynamic delegate
UFUNCTION()
void HandleOverlap(AActor* OverlappedActor, AActor* OtherActor);

// BeginPlay
OnActorBeginOverlap.AddDynamic(this, &AWanderingCube::HandleOverlap);

// Implementation
void AWanderingCube::HandleOverlap(AActor* /*OverlappedActor*/, AActor* OtherActor)
{
    if (APunkGirlCharacter* Collector = Cast<APunkGirlCharacter>(OtherActor))
    {
        Collector->CollectCube();
        Destroy();
    }
}
```

Forgetting `UFUNCTION()` compiles the function and fails to bind at runtime, with no
error — the overlap simply never arrives.

Avoid naming the local `Player` if the class has a `Player` member: UE builds with
`-Wshadow -Werror` and the error points at the local, not at the collision setup.

Use `OnActorBeginOverlap` for "anything touched this actor" and the component's
`OnComponentBeginOverlap` when a specific component is the trigger — a sword blade rather
than the whole character.

## 7. Blocking collision for level bounds

```cpp
MeshComp->SetCollisionProfileName(TEXT("BlockAll"));
MeshComp->SetMobility(EComponentMobility::Static);
```

Set the profile by name. Confirm that name against the collision profiles in this
project. Do not copy a Python enum spelling into C++.

For walls around a floor, overlap them at the corners. Four walls at exactly the floor
extent leave four square gaps where the player falls through — make each wall longer than
the span by twice its thickness.

## 8. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Overlap never fires | One side responds `Ignore`, or neither generates events | Fix the response; `SetGenerateOverlapEvents(true)` |
| Overlap never fires, compiles fine | Handler missing `UFUNCTION()` | Add it |
| Pickup pushes the player | `QueryAndPhysics` | `QueryOnly` |
| Crash on second PIE run | Timer not cleared in `EndPlay` | Clear it |
| `SetTimer` will not compile | Handler returns a value | Thin `void` wrapper |
| Timer fires once instead of looping | `bLoop` left false | Pass `true` |
| HUD countdown disagrees with the spawner | Two clocks | Expose `GetTimerRemaining` from the owner |
| Player falls through a corner | Walls exactly the floor span | Overlap them |

Related: [[ue-actor-spawner]], [[ue-canvas-hud]], [[ue-sprint-and-dash]].
