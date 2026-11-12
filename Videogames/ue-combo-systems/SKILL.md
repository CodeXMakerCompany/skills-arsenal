---
name: ue-combo-systems
description: Combo systems for Unreal Engine 5 action games - a graph of moves, an input buffer, cancel edges that open only inside a time window, whiff versus hit routes, and montage sections per hit. Use when chaining attacks, when a button mash should become a specific string, when a combo drops or loops, or when combo logic is an integer counter. On UE 5.8, create the move assets and montages through Unreal MCP. Pairs with ue-action-time-windows, ue-anim-montages-notifies, ue-gas-abilities and ue-gameplay-tags.
---

# Combos

A combo is a directed graph of moves. The current node is the move that is playing. An edge is "this input, during this window, goes to that move". A counter of how many times light-attack was pressed is not a combo. It cannot express a branch, a finisher, or a different route on hit and on whiff.

## Data

One data asset per move, and one graph asset (or rows) for the edges.

Move:

- Identity tag (`Move.Light1`, `Move.Light2`, `Move.Heavy`).
- Montage and the section to play. See `ue-anim-montages-notifies`.
- The time windows from `ue-action-time-windows`.
- Optional GAS ability to activate. If every move is an ability, the ability is the move and this asset points at it. Do not also switch on an integer inside the ability.

Edge:

- `From` move tag
- `Input` tag (`Input.Light`, `Input.Heavy`, `Input.Forward`)
- `To` move tag
- `Window` (which cancel window on `From` may take this edge)
- `bRequiresHit` or `bRequiresWhiff`, if the route differs. Default is "either".

Lookup is exact on `(From, Input)` plus the window test. Order of buttons in a string is whatever path the edges form. You do not store `"Light,Light,Heavy"` as a string to parse.

Neutral has edges too. `From = None` is the first hit of a string. Standing light and a combo light can be different moves. That is two edges, not a special case.

## Runtime

One component, or the ability that owns the current move. One owner.

1. On input, if a move is legal right now (neutral, or a window that accepts this input), remember it as the buffered desire with `GetWorld()->GetTimeSeconds()` converted the same way as the combat clock. One slot. A new press replaces the old desire.
2. Each sample, while a montage is playing: if the buffer is younger than `BufferOpenMs` and an edge matches the current move, the input, and the open window, start the `To` move and clear the buffer.
3. Starting a move plays its section (or activates its ability), resets the per-target hit set, and sets the current node.
4. When the move ends and nothing was buffered, return to neutral. Do not automatically play the next light.

Whiff versus hit: the move records whether its active window confirmed a hit. Edges with `bRequiresHit` fail on a whiff. Write that down. A combo that "sometimes continues" is an edge that forgot this flag.

Cancel into the next move stops or branches the current montage in the same sample the edge is taken. Two montages on the same slot is a blend, not a combo.

## What resets the string

Pick these explicitly and put them on the graph, not in scattered bools:

- Montage ended with an empty buffer → neutral.
- Landed a move that has no outgoing edge for later input → neutral after recovery.
- Hit by the defender, unless this move has super armor covering that time → neutral or a hit-stun move. Hit stun is a move, not `bStunned = true` plus the combo left running.
- Death, or the character leaving the mode that owns combat.

Do not reset on a whiff unless the edges say so. Some strings are whiff confirms and some are not.

## GAS or not

If the project already uses GAS for attacks, each node activates one ability and the combo component only answers "which ability, and is the edge legal". The ability does not contain the graph. See `ue-gas-abilities`.

If the project has three melee strings and no GAS, do not add GAS to store a combo. The graph plus montages is enough. The mode machine in `ue-state-machines` only knows `Attacking` versus `Grounded`.

## Input

Use the Enhanced Input action that already exists. The combo listens for the action and stores a tag. It does not read `WasInputKeyJustPressed` for `EKeys::LeftMouseButton` in parallel or the two paths will disagree.

Directional inputs (`forward+light`) are an input tag, computed once from the movement stick relative to the actor, then treated like any other edge. Do not special-case them after the graph lookup.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Light always does the next light | Integer counter | Graph of edges |
| Combo drops one frame early | Buffer expired, or window shorter than the data says | Log position versus window when a press is rejected |
| Combo continues after a miss | Edge missing `bRequiresWhiff` / hit test | Set the flag and record the hit |
| Both attacks visible | Old montage not stopped on the same slot | Branch or stop, then play |
| Mash skips a node | Buffer replaced and a window accepted the later input | One buffered input, consumed once |
| Finisher plays from neutral | `From` was wrong | Neutral edges are explicit |

Related: `ue-action-time-windows`, `ue-anim-montages-notifies`, `ue-gas-abilities`, `ue-gameplay-tags`, `ue-enhanced-input-cpp`.
