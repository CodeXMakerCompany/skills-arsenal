---
name: ue-state-machines
description: Choose and structure state machines in Unreal Engine 5.8 - AnimBP for locomotion looks, State Tree for AI and mission flow, GAS for abilities, and a small C++ FSM for frame-tight character modes. Use when adding states, when gameplay rules were written into an animation graph, when an AI needs a State Tree, or when several machines fight over the same actor. Pairs with state-machine-architect for the language-agnostic table, and with ue-gas-abilities, ue-anim-montages-notifies and ue-combo-systems.
---

# State machines in UE 5.8

An actor is in one mode of a given machine at a time, and each machine has one owner. Unreal already has several machines. Picking the wrong one is the bug this skill exists to prevent.

The transition table itself (names, allowed edges, enter/exit) is `state-machine-architect`. This skill decides which Unreal machine stores that table.

On 5.8, inspect and edit State Trees, AnimBPs and GAS assets through `unreal-mcp` after describing those toolsets. Do not rebuild a machine in Python because the asset editor is unfamiliar.

## Which machine owns the state

| Machine | Owns | Does not own |
|---------|------|----------------|
| AnimBP state machine | What the mesh looks like while moving: idle, walk, fall | Damage, combo legality, AI goals |
| State Tree | AI, NPC routines, mission or dialogue flow. Evaluators read the world. Tasks do one thing and finish. | Per-frame combat windows, character movement integration |
| GAS ability | One verb that starts, runs and ends: attack, dash, heal. Tags say it is active. | The locomotion cycle, the AI's long-term plan |
| C++ FSM on the character | Modes that must change on the same frame as movement: grounded, dashing, attacking, dead | Content a designer must retune every day without a programmer |

Use more than one machine when the axes are independent. Locomotion (AnimBP) and "which attack is playing" (GAS or the C++ mode) are independent. "Stunned" is not a third locomotion state that duplicates the stun already applied by a Gameplay Effect. Mirror it with a tag if the AnimBP needs to read it. One owner writes the tag.

## Rules that hold for all of them

- States are nouns (`Attacking`), transitions are events (`AttackPressed`, `MontageEnded`, `Landed`).
- Write the allowed edges down before creating assets. An edge that is not in the table does not happen. Log the rejection in non-shipping builds.
- Enter sets something up. Exit undoes that same thing. A montage started on enter is stopped on exit, including when the exit is a stun.
- One writer. If both the AnimBP and the character call `SetMovementMode`, they will fight.
- Past about eight states, or when the same edge is copied onto every child, make it hierarchical (`Grounded` over `Idle` and `Walk`) or split an axis out. Do not add `IdleFire`, `WalkFire`, `IdleIce`, `WalkFireIce`.

## AnimBP

The graph may blend. It may not decide that an attack is legal. It reads speed, movement mode, and a tag or enum the character already set. Notifies and montage sections are how an animation reports time. They are specified in `ue-anim-montages-notifies`. A transition condition that calls gameplay code to apply damage is in the wrong graph.

## State Tree

Use it for "what is this NPC trying to do" and for scripted flows with clear tasks. Describe the State Tree toolset and edit the asset there.

- A task ends. It does not tick a 16 ms combat window.
- Evaluators gather data (distance, target). Transitions read that data. They do not search the world themselves with `GetAllActorsOfClass`.
- The tree does not set capsule movement every frame. It asks the character to enter a mode. The C++ mode or GAS performs it.

## GAS and the C++ mode

An ability is a state with a start and an end. If the only modes in the game are abilities, GAS is the machine. See `ue-gas-abilities`. Do not also keep a C++ enum that copies `Ability.Attack` and can disagree with it.

A C++ machine is worth it when the mode changes movement for a few frames and GAS would be a second framework for three states. Put the table in one place:

```cpp
bool FCharacterMode::CanEnter(EMode Next) const
{
    switch (Current)
    {
    case EMode::Grounded: return Next == EMode::Dashing || Next == EMode::Attacking;
    case EMode::Attacking: return Next == EMode::Grounded; // cancel edges live in the combo graph, not here
    default: return Next == EMode::Dead;
    }
}
```

Combo cancel edges are data in `ue-combo-systems`. The mode machine only knows "an attack is happening". The combo graph knows which attack may replace it.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Attack plays, damage never applies | Rule lived in an AnimBP transition that did not run | Gameplay machine owns the rule. AnimBP reads the result |
| NPC freezes in a task | Task never finishes, tree never transitions | Tasks complete. Continuous work is a mode on the character |
| Stun and attack both true | Two writers, no table | One owner. The other reads a tag |
| State Tree ticks hit windows | Combat timing stuffed into an evaluator | `ue-action-time-windows` |
| Designer cannot change a transition without C++ | Content edges hardcoded | Those edges move to the State Tree or the combo graph |

Related: `state-machine-architect`, `ue-gas-abilities`, `ue-combo-systems`, `ue-anim-montages-notifies`, `ue-gameplay-tags`.
