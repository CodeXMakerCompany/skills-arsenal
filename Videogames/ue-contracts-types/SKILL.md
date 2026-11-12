---
name: ue-contracts-types
description: Define the contracts between Unreal Engine 5 gameplay systems - UINTERFACE for capabilities, Gameplay Tags for facts, Primary Data Assets for designer-owned identity, and instanced structs for plain data. Use when systems reach into each other with Cast, when a new potion or weapon became a new subclass, when UI includes gameplay headers, or when two features cannot change without breaking each other. On UE 5.8, create the assets through Unreal MCP toolsets. Pairs with ue-gameplay-tags and ue-merge-objects.
---

# Contracts and types in UE 5.8

Systems talk through a small set of types. They do not `Cast` to a concrete actor to ask a question, and they do not grow a subclass every time a designer adds a number.

Create the assets (interfaces as Blueprintable classes, data assets, tag tables) through `unreal-mcp` after `describe_toolsets`. The rules below are the design. They apply in C++ and in Blueprint.

## Four kinds of type, and what each is for

| Kind | Holds | Does not hold |
|------|--------|----------------|
| `UINTERFACE` | A capability: "can be damaged", "can be merged", "can be selected" | Stats, asset references, tags |
| Gameplay Tag | A fact: `Item.Potion`, `State.Stunned`, `Damage.Fire` | Behavior, asset pointers |
| Primary Data Asset | Identity and designer data: one potion, one weapon, one enemy | Live state (health, cooldown) |
| Instanced struct / data table row | Plain values passed across a function | `UObject` lifetime |

A subclass is justified when behavior actually differs in code. A fire potion and a frost potion that differ by a tag, a color and a magnitude are one class and two data assets.

## Interfaces

An interface function is a question or a command with a stable signature.

- `CanMergeWith(Other) -> bool` and `BuildMergeResult() -> FItemStack` belong on `IMergeable`. The potion actor implements them by reading its data asset. The merge system never includes `Potion.h`.
- Return data, not the actor. A damage interface returns a result struct (applied, killed, tags). The caller does not then poke the health component.
- Keep interfaces in a module both sides already depend on, usually a small `GameCore` module. Gameplay features depend on `GameCore`. `GameCore` does not depend on features. UI depends on `GameCore` and reads tags and structs. UI does not include the character header.

If the only implementation is one class, you do not have a contract yet. Write the function on that class. Extract the interface when a second implementer appears.

## Identity is data

An item, ability, or enemy definition is a Primary Data Asset:

- A soft reference or primary asset id is how other assets name it. Hard references in both directions load the world.
- Live state (stack count, current cooldown, owner) lives on the inventory entry or the actor, never on the definition. Definitions are shared. Writing runtime state onto one writes it for every user of that asset.
- Numbers designers tune (damage, duration, merge output) are `EditDefaultsOnly` on the data asset or a row in a data table. They are not literals in C++.

`GetActorOfClass` and `GetAllActorsOfClass` are not an API. A system receives the actor it is allowed to touch, or it looks up a registered subsystem. A contract that searches the world will find the wrong instance the day a second one exists.

## What crosses a boundary

Pass structs and tags. Do not pass the actor when the callee only needs "10 fire damage at this location".

```cpp
USTRUCT(BlueprintType)
struct FDamageSpec
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FGameplayTag DamageType;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float Magnitude = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TObjectPtr<AActor> Instigator = nullptr;
};
```

The receiver decides whether it implements damage. The sender does not `Cast<ACharacter>`.

## Dependencies

Allowed:

- Feature -> `GameCore` (interfaces, tags, structs, data asset base)
- Feature -> engine modules it actually uses
- UI -> `GameCore` and a view-model struct

Forbidden:

- `GameCore` -> a feature module
- Gameplay -> UMG, except a module whose only job is presentation
- A data asset -> a widget

When a Blueprint needs a type from another feature, the type is in `GameCore` or the Blueprint is in the wrong feature.

## Checks before you add a class

1. Is the difference data (numbers, tags, meshes, sounds)? Data asset. Stop.
2. Is the difference a capability several actors share? Interface.
3. Is the difference a fact other systems must read without knowing the class? Tag. See `ue-gameplay-tags`.
4. Is the difference real code? Subclass, and keep the subclass thin over the data asset.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Every new item is a new Blueprint class | Identity was stored in the class | One class, one data asset per item |
| UI will not compile without the character module | A widget included the pawn header | Pass a struct or tags |
| Changing one potion changes all of them | Runtime state written on the data asset | State on the inventory entry |
| `Cast` chain in the merge code | The contract was never extracted | `IMergeable`, or a pure function from two ids to a result id |
| Random actor receives the event | `GetAllActorsOfClass` | Pass the target in, or register it |

Related: `ue-gameplay-tags`, `ue-merge-objects`, `ue-gas-abilities`.
