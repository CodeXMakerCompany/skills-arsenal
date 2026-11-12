---
name: ue-loop-systems
description: Structure gameplay loops in Unreal Engine 5 - the moment the player repeats, the session that contains it, and the meta loop that survives the session. Includes a time loop, where a reset list and a persist list are one transaction. Use when designing a core loop, a run, a day cycle, a roguelike, or a Groundhog-day reset, or when restarting the level deletes the wrong state or keeps it. On UE 5.8, place the loop's actors and data assets through Unreal MCP. The phase change belongs to GameMode or a state machine, not to Tick.
---

# Gameplay loops

A loop is a repeat with a reason. Name it before spawning actors: what the player does, what changes, why they do it again, and how they leave. "The game loops" is not a design. Three nested loops that each have an owner is a design.

| Loop | Length you can say out loud | Owner in UE | Dies when |
|------|-----------------------------|-------------|-----------|
| Moment | One attack, one jump, one conversation choice | The character, the combo graph, the interaction | The action ends |
| Session | One run, one day, one match. Minutes to an hour | `GameMode` / `GameState` | The match ends, the player extracts, or the day closes |
| Meta | The career, the unlocks, the save | `GameInstance` subsystem and the save object | The player deletes the save |

The moment loop does not grant meta rewards. The meta loop does not tick movement. The session loop starts and ends the world they both use. If two owners can restart the session, they will, and one of them will be wrong.

On 5.8, create the data assets, the level, and the placed loop bounds through `unreal-mcp`. The phase machine is code or a State Tree. See `ue-state-machines`. Do not poll "should the loop end?" in `Tick`.

## Write the loop as four lines

For each loop, fill these in before the Blueprint:

1. **Start.** The condition that enters the repeat. Not "BeginPlay" unless the session truly starts there.
2. **Action.** The verb the player repeats. One verb. A second verb is a second loop or a branch inside this one.
3. **Change.** What is different after the action. Loot, a clock, a relationship, a tile. If nothing changes, the player has no reason to repeat and you have a treadmill.
4. **Exit.** A success, a failure, and a quit. All three are specified. A loop with no exit is a softlock the player will call a bug.

The session's length is a number (a 12-minute run, a day that ends at dusk). When playtests run long, change that number or the action. Do not add a second reward currency to hide a loop that does not end.

## Where the reward is granted

The reward is a transaction at the boundary, the same way `ue-merge-objects` grants an item. The session decides it ended. Then the meta system grants the unlock, the currency, or the unlock tag. Granting on the kill, and also on the extract, doubles the reward the first time both fire.

Failure ends the session without the success grant. Say so. A roguelike that keeps the loot from a failed run has made a different game. Write which list it is on.

Live session state (health, enemy positions, the day's clock) lives on the world and is gone when the world is gone. Meta state lives on the save and on a GameInstance subsystem. A float on the `PlayerController` is a trap: the controller often survives a map change, so "it reset" is sometimes "the pawn died and the controller remembered".

## Phases

Use a match state or a small session machine: `Waiting`, `Playing`, `Resolving`, `Ended`. Enter on `Playing` enables spawning and the player's verbs. Enter on `Resolving` stops input that can still change the outcome, then runs the transaction. Enter on `Ended` shows the result and offers the next session or the exit. `Resolving` that never arrives at `Ended` is a stuck reward screen. Time it out to `Ended` with the failure grant.

`GameState` replicates the phase. Clients do not decide that the run ended. They play the presentation the phase tells them to play.

Spawns, waves and the day clock subscribe to the phase. They do not start themselves in `BeginPlay` if the session is still `Waiting`. See `ue-actor-spawner` and `ue-timers-and-triggers`.

## Time loop

A time loop is a session that restarts on purpose. It is still the four lines. The change that matters is the persist list. Everything not on that list returns to the start snapshot.

Write two lists on a data asset:

- **Persist.** Knowledge, a single item the fiction keeps, a flag, a relationship. Small.
- **Reset.** Everyone else, positions, inventory, the clock, dead enemies, spent pickups.

The restart is one transaction:

1. Copy the persist list out of the world into the GameInstance or the save.
2. Load the start level, or rebuild from a snapshot taken at the loop start. Prefer a fresh world over trying to rewind every actor. Rewinding actors in place misses the one you spawned after the snapshot.
3. Apply the persist list onto the new world.
4. Only then set the phase to `Playing`.

If step 3 fails, do not start play on a half-applied world. Stay in `Resolving` and surface the error.

Do not `DestroyAllActors` and expect `BeginPlay` to restore the start. Actors placed after the loop began, and actors that moved, do not return. A snapshot or a new load does.

`GameInstance` subsystems and the `PlayerController` survive travel. After a reset, initialize the pawn and the controller from the persist list and the start snapshot. Do not assume a new controller. Anything that must reset and was stored on the controller will leak into the next loop. Move it to the world, or clear it explicitly in the transaction.

Seamless travel keeps more of the old world than `OpenLevel`. Use it only if the persist list is "almost everything" and you have named what still has to die. For a strict loop, open the start level.

## Quit and fail are exits

Quitting to desktop during `Playing` does not grant the success reward. Save the meta state you are willing to keep, using the same transaction rules, or save nothing from the open session. A crash mid-run that reloads as a victory is the transaction running in the wrong phase.

The moment loop's failure (a whiff, a dropped combo) does not end the session. The session's failure (death, timer, collapse) does not delete the meta save. Wire those to the owners above. A single `OnDied` that restarts the level, grants currency, and clears the save is three loops in one callback.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| The run never ends | No exit, or `Resolving` does not reach `Ended` | Write the three exits. Time out `Resolving` |
| Rewards double | Granted on the kill and again on extract | One grant, in the session transaction |
| The reset kept the player's inventory | Inventory lived on the controller, which survived travel | Persist list only. Clear or replace the controller state |
| Enemies stay dead after the loop | Destroyed actors were never in a start snapshot | Load the start level or rebuild from the snapshot |
| A new run starts during the reward screen | A spawner starts in `BeginPlay` | Spawners wait for `Playing` |
| Two systems restart the day | GameMode and a volume both open the level | The session owner is the only restarter |

Related: `ue-state-machines`, `ue-contracts-types`, `ue-gameplay-tags`, `ue-actor-spawner`, `ue-timers-and-triggers`, `ue-merge-objects`.
