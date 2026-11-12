---
name: ue2d-hitboxes-and-combat
description: 2D combat in Unreal Engine 5 - separating hitboxes from hurtboxes on their own collision channels, enabling them for exact animation windows with notifies, frame data as a startup/active/recovery contract, hit confirmation with knockback, hitstop and invulnerability, and preventing multi-hits from one swing. Use when building 2D melee or projectile combat, when attacks hit multiple times or miss unfairly, or when combat lacks impact. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 2D Hitboxes and Combat

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Readable 2D combat is a contract between animation and collision: an attack is active for
a known window and nothing else. Vague windows produce attacks that feel unfair in both
directions.

> Written from general 2D combat practice rather than verified end to end in one Unreal
> project.

## Before you start

1. **Separate hitbox from hurtbox.** A hitbox deals damage; a hurtbox receives it. One
   volume doing both makes every exchange ambiguous.
2. **Add collision channels**: `Hitbox` and `Hurtbox`, in Project Settings → Collision.
   Reusing `WorldDynamic` means hitboxes collide with scenery.
3. **Decide the time base.** Frames at a fixed animation rate are easier to reason about
   and to communicate than seconds.

## 1. Channels

| Volume | Object type | Responses |
|--------|-------------|-----------|
| Hitbox | `Hitbox` | Overlap `Hurtbox`, Ignore everything else |
| Hurtbox | `Hurtbox` | Overlap `Hitbox`, Ignore everything else |
| Body | `Pawn` | Block world, Ignore both |

Keeping the body separate is what lets a character pass through an enemy while still
trading hits — or not — as a design choice rather than a collision accident.

```cpp
HitBox->SetCollisionEnabled(ECollisionEnabled::NoCollision);   // off until the active window
HitBox->SetCollisionObjectType(ECC_Hitbox);
HitBox->SetCollisionResponseToAllChannels(ECR_Ignore);
HitBox->SetCollisionResponseToChannel(ECC_Hurtbox, ECR_Overlap);
HitBox->SetGenerateOverlapEvents(true);
```

Remember the overlap rule: the response is the **weaker** of the two sides, and an
`Ignore` on either side means nothing fires at all.

## 2. Frame data

Describe every attack the same way:

| Phase | Meaning | Light | Heavy |
|-------|---------|-------|-------|
| Startup | Before the hitbox turns on | 4 f | 10 f |
| Active | Hitbox enabled | 3 f | 5 f |
| Recovery | Locked out after | 8 f | 20 f |

```cpp
USTRUCT(BlueprintType)
struct FAttackData
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) int32 StartupFrames = 4;
    UPROPERTY(EditAnywhere) int32 ActiveFrames = 3;
    UPROPERTY(EditAnywhere) int32 RecoveryFrames = 8;
    UPROPERTY(EditAnywhere) float Damage = 10.0f;
    UPROPERTY(EditAnywhere) FVector2D Knockback = FVector2D(300.0f, 150.0f);
    UPROPERTY(EditAnywhere) float HitstopSeconds = 0.08f;
};
```

Having this as data rather than scattered timers is what makes an attack tunable by
someone who is not reading the code.

## 3. Driving the window from the animation

Animation notifies are the right driver: the window then stays correct when the
animation is retimed, which hard-coded timers do not.

```cpp
void AHero::OnHitboxEnable()  { HitBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly); AlreadyHit.Reset(); }
void AHero::OnHitboxDisable() { HitBox->SetCollisionEnabled(ECollisionEnabled::NoCollision); }
```

Without notifies, derive the window from the frame data and the flipbook's frame rate so
there is still a single source of truth.

## 4. One hit per swing

```cpp
void AHero::OnHitboxOverlap(UPrimitiveComponent*, AActor* OtherActor, ...)
{
    if (!OtherActor || OtherActor == this) return;
    if (AlreadyHit.Contains(OtherActor)) return;    // reset on each enable
    AlreadyHit.Add(OtherActor);

    ApplyHit(OtherActor);
}
```

`TSet<TWeakObjectPtr<AActor>> AlreadyHit`, cleared when the hitbox turns on. Without it a
3-frame active window overlapping at 60 FPS applies damage three times, which reads as a
damage bug rather than a collision one.

## 5. Impact

Three cheap things, in order of value:

**Hitstop.** Freeze both parties for 60–100 ms. More than anything else this is what
makes a hit land.

```cpp
CustomTimeDilation = 0.0f;
GetWorldTimerManager().SetTimer(HitstopTimer, [this]()
{
    CustomTimeDilation = 1.0f;
}, Attack.HitstopSeconds, false);
```

**Knockback**, away from the attacker, with a vertical component:

```cpp
const float Dir = FMath::Sign(Victim->GetActorLocation().X - GetActorLocation().X);
Victim->LaunchCharacter(FVector(Dir * Attack.Knockback.X, 0.0f, Attack.Knockback.Y), true, true);
```

**Invulnerability** after being hit, so a single swing cannot chain-lock. Disable the
hurtbox for the duration rather than tracking a flag in the damage code — the collision
system then enforces it.

## 6. Projectiles

The same contract with a lifetime. Give projectiles their own pooled class, destroy on
first hit unless piercing, and always set a maximum lifetime: a projectile that misses
everything and flies forever is a slow actor leak. See [[ue-actor-spawner]] for the
pooling and cap patterns.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| One swing deals damage several times | No per-swing hit list | `TSet`, cleared on enable |
| Attacks hit scenery | Hitbox on `WorldDynamic` | Dedicated channel |
| Hits land but feel weightless | No hitstop | 60–100 ms freeze |
| Attack connects after the animation ends | Hitbox disabled too late, or never | Notify-driven disable |
| Hitbox never fires | `Ignore` on one side, or events not generated | Check both responses |
| Character can be stunlocked forever | No invulnerability window | Disable the hurtbox after a hit |
| Combat retimes wrongly after an animation change | Hard-coded timers | Drive from notifies |

Related: [[ue2d-flipbook-animation]], [[ue2d-platformer-controller]],
[[ue-timers-and-triggers]], [[ue-actor-spawner]]. For 3D and action games, the timing
contract is `ue-action-time-windows` and the chain is `ue-combo-systems`. This skill
stays the 2D collision setup.
