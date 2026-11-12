---
name: ue-gameplay-tags
description: Design Gameplay Tags as the shared vocabulary of an Unreal Engine 5 game - hierarchies, native tags versus ini, MatchesTag versus exact match, tags on data assets, and what tags must not be used for. Use when adding states, damage types, item families, ability names, or when two systems need to agree on a fact without including each other's headers. On UE 5.8, author tags through Unreal MCP and the Gameplay Tags settings. Pairs with ue-contracts-types, ue-gas-abilities, ue-combo-systems and ue-merge-objects.
---

# Gameplay Tags in UE 5.8

A Gameplay Tag is a hierarchical name for a fact. `Item.Potion.Minor` says what something is. It does not say what the game should do about it. Behavior stays in code or in a data asset that lists the tags it cares about.

Author the tag list through `unreal-mcp` (Gameplay Tags settings, or a tag source asset the described toolset can edit). Do not invent tags in a random Blueprint string.

## Shape of the tree

Tags read from general to specific, dot-separated:

```
Item.Potion
Item.Potion.Minor
Item.Potion.Major
State.Combat
State.Combat.Attacking
Damage.Fire
```

Rules:

- A parent is a real category you will query. `Item.Potion` means "any potion". If you will never ask that, do not add the parent just to look tidy.
- Do not encode values in the tag. `Damage.Fire.10` is a bug. Magnitude is a float next to the tag.
- Do not encode ownership. `Player.Sword` and `Enemy.Sword` split one fact in two and every query pays for it. Who holds it is a pointer. What it is is `Item.Weapon.Sword`.
- Renames break assets. Add a tag, migrate references, then remove the old one. Do not "just rename" a tag that ships in data.

## Where tags live

| Source | Use when |
|--------|----------|
| Native gameplay tags (`UE_DEFINE_GAMEPLAY_TAG`) | Code branches on the tag. The symbol cannot drift from a typo in an asset. |
| `Config/Tags/*.ini` or the project tag list | Designers add facts code only matches by parent. |
| Tags on a data asset (`FGameplayTagContainer`) | This potion is `Item.Potion.Minor` and `Damage.Fire`. The asset is the owner of the fact. |

Code that switches on a specific leaf uses a native tag. Code that asks "any child of `Item.Potion`" can use the ini tag, because the parent is the contract and the leaves are content.

## Matching

- `MatchesTag` is hierarchical. `Item.Potion.Minor` matches a query for `Item.Potion`.
- `MatchesTagExact` does not. Use it when the leaf is the identity, such as a merge recipe key. A parent match there would craft the wrong potion.
- `HasAll` / `HasAny` are for containers. Say which one in the function name. "Has the tags" is ambiguous and becomes a bug.

An empty container matches nothing. Treat "no tags" as a failed lookup, not as a wildcard, unless the function documents the wildcard on purpose.

## What a tag is not

- Not an event bus. `SendGameplayEvent` and GAS events are a delivery mechanism. A tag named `Event.Jump` that every system both sends and listens for, with no owner, becomes untraceable. An event has a sender and a payload struct.
- Not a save file. Loose tags on an actor replicate and reset with the actor. Persistent facts belong to the save game or the inventory entry.
- Not a substitute for a state machine. `State.Attacking` may mirror the current state so other systems can read it. The machine in `ue-state-machines` still owns the transition. Setting the tag from three places means nobody owns it.
- Not a Blueprint class name. Do not parse tag strings.

## Replication and lifetime

Tags on a replicated actor or on an Ability System Component replicate with that object. Add a tag on the server. A client-added loose tag disappears or fights the server.

Remove the tag in the same place that added it. A stun tag added by a Gameplay Effect is removed when the effect ends. A second system must not also `RemoveLooseGameplayTag` on that same tag or it will clear a stun that is still active. One owner per tag.

## Checks

1. Can you say the fact out loud without a verb? If it needs a verb ("do the merge"), it is a function, not a tag.
2. Will a parent query be correct for every child you might add later? If not, the parent is a lie.
3. Is the leaf referenced from C++? Make it native.
4. Does GAS, a combo window, or a merge recipe need this exact tag? Point those skills at the same container. Do not create `Combo.Fire` and `Damage.Fire` for one fact.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Query never hits | Exact match against a parent, or a typo versus a native tag | `MatchesTag`, or one native symbol |
| Wrong recipe crafts | Parent match used as an identity key | `MatchesTagExact` on the leaf |
| Stun ends early | Two systems remove one tag | The effect that added it is the only remover |
| Designers added `Damage.Fire.10` | Magnitude stored in the name | Tag plus a float |
| UI and gameplay disagree on names | Tags typed as strings in the widget | Both read the container on the data asset |

Related: `ue-contracts-types`, `ue-gas-abilities`, `ue-merge-objects`, `ue-state-machines`.
