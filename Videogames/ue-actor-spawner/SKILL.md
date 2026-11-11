---
name: ue-actor-spawner
description: A reusable timed spawner actor for Unreal Engine 5 that drops mobs, pickups, rewards or hazards into a level in waves - timer driven with no per-frame cost, a hard cap on live actors so a long session cannot grow unbounded, weak pointers so collected or killed actors are not kept alive, uniform spawn distribution over a disc, a minimum distance from the player, and a difficulty counter that rises each wave. Use when building a wave spawner, a reward or pickup generator, a mob generator, or any system that periodically adds actors to a running level.
---

# UE5 Timed Actor Spawner

One actor whose only job is to put other actors in the world on a schedule. Mobs, coins,
hazards and power-ups are the same system with a different class and different tuning, so
build it once.

## Before you start

1. **Decide the lifetime contract.** Who destroys a spawned actor — itself on pickup, the
   spawner on a timer, or a pool? Everything below assumes the actor destroys itself, which
   is why the spawner holds weak references.
2. **Decide the cap.** "Eight every twenty seconds" with no ceiling is an actor leak with
   extra steps.
3. **Decide who owns the spawner.** A level-placed actor is fine; spawning it from the
   GameMode means the level needs no setup and cannot be shipped without it.

## 1. The class

```cpp
UCLASS()
class MYGAME_API ARandomRewardsGenerator : public AActor
{
    GENERATED_BODY()

public:
    ARandomRewardsGenerator();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

    /** Spawns one batch. Returns how many actually spawned. */
    UFUNCTION(BlueprintCallable, Category = "Rewards")
    int32 GenerateRandomRewards();

    float GetSecondsUntilNextBatch() const;
    float GetInterval() const { return Interval; }
    int32 GetDifficultyMultiplier() const { return DifficultyMultiplier; }

protected:
    UPROPERTY(EditAnywhere, Category = "Rewards")
    TSubclassOf<AActor> RewardClass;

    UPROPERTY(EditAnywhere, Category = "Rewards", meta = (ClampMin = "1"))
    int32 BatchSize = 8;

    /** Hard ceiling on live actors. */
    UPROPERTY(EditAnywhere, Category = "Rewards", meta = (ClampMin = "1"))
    int32 MaxAliveRewards = 24;

    UPROPERTY(EditAnywhere, Category = "Rewards", meta = (ClampMin = "1.0"))
    float Interval = 20.0f;

    UPROPERTY(EditAnywhere, Category = "Rewards")
    float SpawnRadius = 1600.0f;

    UPROPERTY(EditAnywhere, Category = "Rewards")
    float MinPlayerDistance = 400.0f;

private:
    void HandleBatchTimer();           // SetTimer needs a void signature
    void PruneCollected();
    FVector PickSpawnPoint(const FVector& PlayerLocation) const;

    FTimerHandle BatchTimer;
    int32 DifficultyMultiplier = 1;

    /** Weak on purpose: a collected reward destroys itself. */
    TArray<TWeakObjectPtr<AActor>> AliveRewards;
};
```

## 2. No Tick

```cpp
ARandomRewardsGenerator::ARandomRewardsGenerator()
{
    PrimaryActorTick.bCanEverTick = false;     // timer driven
    RewardClass = AWanderingCube::StaticClass();
}

void ARandomRewardsGenerator::BeginPlay()
{
    Super::BeginPlay();
    GenerateRandomRewards();                   // one batch immediately
    GetWorldTimerManager().SetTimer(
        BatchTimer, this, &ARandomRewardsGenerator::HandleBatchTimer, Interval, true);
}

void ARandomRewardsGenerator::EndPlay(const EEndPlayReason::Type Reason)
{
    GetWorldTimerManager().ClearTimer(BatchTimer);
    Super::EndPlay(Reason);
}
```

A spawner that ticks to count down its own interval is burning a frame callback to do
what `FTimerManager` already does. Clear the timer in `EndPlay` — it is tied to the world,
and leaving it set across a PIE restart is a classic stale-callback crash.

`SetTimer` requires a `void()` handler. `GenerateRandomRewards` returns `int32` for
callers and tests, so route the timer through a thin wrapper:

```cpp
void ARandomRewardsGenerator::HandleBatchTimer()
{
    ++DifficultyMultiplier;        // a loop just closed
    GenerateRandomRewards();
}
```

## 3. Weak pointers and the cap

```cpp
void ARandomRewardsGenerator::PruneCollected()
{
    AliveRewards.RemoveAll([](const TWeakObjectPtr<AActor>& R) { return !R.IsValid(); });
}
```

`TArray<TObjectPtr<AActor>>` under a `UPROPERTY` would keep every collected reward alive
forever: the actor is destroyed but the strong reference stops it being collected, and
the array grows for the whole session. Weak pointers go null on destruction and the prune
is a cheap sweep once per batch, not per frame.

```cpp
PruneCollected();
const int32 Room = FMath::Max(0, MaxAliveRewards - AliveRewards.Num());
const int32 ToSpawn = FMath::Min(BatchSize, Room);
```

Topping up to a ceiling, rather than blindly adding a batch, is what keeps a twenty-minute
session at a stable actor count and a stable frame time.

## 4. Spawn points that look random

```cpp
FVector ARandomRewardsGenerator::PickSpawnPoint(const FVector& PlayerLocation) const
{
    const FVector Origin = GetActorLocation();
    FVector Point = Origin;

    for (int32 Attempt = 0; Attempt < 8; ++Attempt)
    {
        const float Angle = FMath::FRandRange(0.0f, 2.0f * PI);
        const float Radius = FMath::Sqrt(FMath::FRand()) * SpawnRadius;   // uniform over the disc
        Point = Origin + FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.0f);
        Point.Z = SpawnHeight;

        if (FVector::Dist2D(Point, PlayerLocation) >= MinPlayerDistance)
        {
            break;
        }
    }
    return Point;
}
```

Two details that matter more than they look:

- **`Sqrt(FRand())`**, not `FRand()`. A disc's area grows with r², so a linear radius
  clumps everything near the centre. The square root spreads them evenly, which is what
  "random" is expected to look like.
- **Bounded retries.** Rejection sampling with a `while` can spin forever when the player
  stands in the middle of a small spawn radius. Try a handful of times and accept the last
  one; a reward occasionally near the player is better than a hang.

Keep `SpawnRadius` inside the playable bounds. With walls at ±2000 and a radius of 1600,
nothing spawns inside geometry.

## 5. Spawning

```cpp
FActorSpawnParameters Params;
Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

for (int32 i = 0; i < ToSpawn; ++i)
{
    const FRotator Rotation(0.0f, FMath::FRandRange(0.0f, 360.0f), 0.0f);
    if (AActor* Reward = World->SpawnActor<AActor>(
            RewardClass, PickSpawnPoint(PlayerLocation), Rotation, Params))
    {
        AliveRewards.Add(Reward);
        ++Spawned;
    }
}
```

`AlwaysSpawn` is deliberate for pickups that do not block. For mobs that must not overlap
geometry, use `AdjustIfPossibleButDontSpawnIfColliding` and accept that some spawns fail —
then report the shortfall rather than silently under-spawning a wave.

## 6. Spawn it from the GameMode

So the level cannot ship without it, and a hand-placed one still wins:

```cpp
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    for (TActorIterator<ARandomRewardsGenerator> It(GetWorld()); It; ++It)
    {
        return;   // respect one placed in the level
    }
    GetWorld()->SpawnActor<ARandomRewardsGenerator>(
        RewardsGeneratorClass, FVector::ZeroVector, FRotator::ZeroRotator);
}
```

## 7. Difficulty, and when to pool

`DifficultyMultiplier` starting at 1 and rising per wave reads as a multiplier rather than
a wave count. Drive real difficulty off it — batch size, drift speed, shrinking interval —
rather than leaving it as a label, or it is decoration.

Pool instead of spawn when you are creating and destroying more than roughly fifty actors
per second, or when the actor is expensive to construct. Below that, `SpawnActor` and
`Destroy` are not the bottleneck and a pool is complexity you will debug for nothing.

## 8. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Actor count climbs all session | No cap, or strong pointers in the live list | Cap plus `TWeakObjectPtr` |
| Spawns clump in the middle | Linear radius | `Sqrt(FRand()) * Radius` |
| Crash on PIE restart | Timer not cleared in `EndPlay` | Clear it |
| `SetTimer` will not compile | Handler is not `void()` | Thin `void` wrapper |
| Rewards appear inside walls | `SpawnRadius` exceeds the playable area | Shrink it, or use a collision-aware spawn method |
| Rewards land on the player | No minimum distance | `MinPlayerDistance` with bounded retries |
| Nothing spawns, no error | `RewardClass` is null | Default it in the constructor |

Related: [[ue-timers-and-triggers]], [[ue-proximity-reactions]], [[ue-canvas-hud]].
