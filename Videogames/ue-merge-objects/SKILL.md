---
name: ue-merge-objects
description: Merge two gameplay objects of the same kind into one new object in Unreal Engine 5 - two potions become one new potion, two gems become one gem. Covers recipe data, an atomic inventory transaction, preview before commit, and why this is not Merge Actors and not a source-control merge. Use when combining items, crafting within one family, upgrading two copies into a higher tier, or when a merge deletes the inputs but the result never appears. On UE 5.8, create the data assets and the preview widget through Unreal MCP. Pairs with ue-contracts-types and ue-gameplay-tags.
---

# Merge two objects into one

Two objects of the same kind produce one new object. Two minor potions become one major potion. The inputs are consumed only when the result is granted. This is an inventory rule.

It is not the editor Merge Actors tool, and it is not a uasset merge in source control. Those weld meshes or resolve files. They do not know what a potion is.

## Pick one verb per family

Three operations get called "merge". A family gets one of them. Do not overload the verb.

| Verb | Inputs | Result | Example |
|------|--------|--------|---------|
| Stack | Same definition, any count | Same definition, counts added | 2 minor potions become a stack of 2 |
| Upgrade | Two of tier N, same family | One of tier N+1, new identity | 2 minor potions become 1 major potion |
| Recipe | Two specific definitions in the family | One specific output | minor fire + minor frost become one steam potion |

This skill is Upgrade and Recipe. Stacking is a count change and does not create a new identity. If the design is "two potions become a better potion", that is Upgrade. Say so in the data, not in a comment.

"Same kind" means the same family tag (`Item.Potion`), not "any two actors in the level". A potion and a sword do not merge. The family tag is the gate. The specific leaves are the recipe key. See `ue-gameplay-tags`.

## Data, not subclasses

- One item class (or one inventory entry struct). Identity is a Primary Data Asset.
- The definition carries tags (`Item.Potion.Minor`, `Damage.Fire`) and presentation (mesh, icon, sound).
- A merge rule is a data asset or a data table row. Inputs are a multiset of definition ids. Order does not matter: sort the ids before lookup. Output is one definition id and a count, usually 1.
- No `APotionFire` / `APotionFrost` subclasses. A new potion is a new row.

The rule set is the contract. A missing row is a rejection. There is no fallback that "uses the first potion" or deletes the inputs anyway.

## The transaction

Authority is the server, or the single local game. The client sends two item handles and a preview or commit flag. The client does not decide the output.

1. Both handles exist, belong to the requester, sit in the inventory, and are not locked or equipped (unless the design explicitly allows equipped merges).
2. Both definitions carry the family tag. If not, reject.
3. Sort the two definition ids. Look up the rule with an exact match on that pair.
4. No rule: reject, change nothing, return a reason the UI can show (`NoRecipe`, `WrongFamily`, `Locked`).
5. Rule hit: remove one count from each input (or the whole stack entry if the count hits zero), then grant the output. One function. If the grant cannot fit, put the inputs back and reject with `NoRoom`.
6. Presentation (Niagara, sound, widget) plays from the **result** tag after the transaction returns. Presentation does not choose the result and does not destroy actors.

World actors are a view. If potions are meshes on a table, the inventory still owns the truth. Destroying the two meshes and spawning a third in `Tick` will desync the moment a mesh fails to spawn. Update the inventory, then refresh the view from it.

Preview calls the same function with `bCommit = false` and returns the output definition without writing. The confirm button is the commit. Do not maintain a second formula in the widget.

## What the function returns

A small struct, not the new actor:

- `bAccepted`
- `Reason` tag or enum
- `OutputDefinition` (null on failure)
- `OutputCount`

The UI and the tests both read that struct. Tests do not need a world: two ids in, one id out, and the rejection cases (wrong family, unknown pair, no room).

## Do not

- Weld Static Meshes and call it crafting.
- `Cast` through potion classes to decide the child class to spawn.
- Destroy the inputs before the output exists.
- Let a Blueprint on the client spawn the result and then tell the server.
- Store the recipe in a chain of branches in the character. The table is the recipe.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Inputs vanish, no result | Destroy happened before a successful grant | One transaction, roll back on failure |
| Fire+frost and frost+fire differ | Lookup did not sort the pair | Sort ids, exact match |
| Any two potions become the higher tier | Parent tag used as the recipe key | Exact leaves for the pair, family tag only as the gate |
| All minor potions changed | Result written onto the shared data asset | Grant a new stack entry that points at the output asset |
| Merge Actors produced a mesh | Editor mesh weld used for a gameplay rule | This skill, on the inventory |

Related: `ue-contracts-types`, `ue-gameplay-tags`, `ue-gas-abilities` if the result applies an effect when consumed, not when crafted.
