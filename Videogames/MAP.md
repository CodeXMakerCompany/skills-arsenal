# Videogames

Thirty-five skills, mostly Unreal Engine 5. Two tracks that share a spine: 3D and 2D.

## Start here

**Before the first asset, run the architect.** [`ue-3d-architect`](ue-3d-architect/SKILL.md) for 3D, [`ue2d-architect`](ue2d-architect/SKILL.md) for 2D. Both derive every dimension from the pawn and let you play a box before any art exists. Skipping this is how a project gets art it then has to rebuild around.

## Project setup

| Need | Skill |
|---|---|
| A clean, playable, minimal level by script | [ue-minimal-level-bootstrap](ue-minimal-level-bootstrap/SKILL.md) |
| The project runs slow, or the template is heavy | [ue-indie-game-setup](ue-indie-game-setup/SKILL.md) |
| Adding C++ to a Blueprint-only project | [ue-cpp-module-bootstrap](ue-cpp-module-bootstrap/SKILL.md) |
| Compiling, Live Coding, cooking, packaging (5.8) | [ue-project-build](ue-project-build/SKILL.md) |

## 3D: moving and seeing

| Need | Skill |
|---|---|
| Locomotion, CMC, AnimInstance, BlendSpaces | [ue-character-movement](ue-character-movement/SKILL.md) |
| Input in C++, keys that do nothing | [ue-enhanced-input-cpp](ue-enhanced-input-cpp/SKILL.md) |
| Follow camera, camera-relative movement, clipping | [ue-third-person-camera](ue-third-person-camera/SKILL.md) |
| Sprint, dash, dodge, feet sliding | [ue-sprint-and-dash](ue-sprint-and-dash/SKILL.md) |
| Importing a rigged character FBX | [ue-character-import-pipeline](ue-character-import-pipeline/SKILL.md) |
| An animation clip that does not exist | [ue-procedural-animation](ue-procedural-animation/SKILL.md) |
| Counters, health bars, countdowns, a title screen | [ue-canvas-hud](ue-canvas-hud/SKILL.md) |

## 3D: systems and architecture

| Need | Skill |
|---|---|
| Interfaces and data assets instead of `Cast` | [ue-contracts-types](ue-contracts-types/SKILL.md) |
| A tag vocabulary for items, damage, states | [ue-gameplay-tags](ue-gameplay-tags/SKILL.md) |
| AnimBP vs State Tree vs GAS vs a C++ mode machine | [ue-state-machines](ue-state-machines/SKILL.md) |
| Moment, session and meta loops, a time loop | [ue-loop-systems](ue-loop-systems/SKILL.md) |
| Waves, cooldowns, pickups, overlaps not firing | [ue-timers-and-triggers](ue-timers-and-triggers/SKILL.md) |
| A spawner with a cap and a difficulty curve | [ue-actor-spawner](ue-actor-spawner/SKILL.md) |
| Two items of one family combine into a third | [ue-merge-objects](ue-merge-objects/SKILL.md) |
| Material instances, rarity and dissolve effects | [ue-material-instance-builder](ue-material-instance-builder/SKILL.md) |
| Pickups that glow near the player | [ue-proximity-reactions](ue-proximity-reactions/SKILL.md) |
| The game acknowledges the player, the keybind, the save | [ue-breaking-the-4th-wall](ue-breaking-the-4th-wall/SKILL.md) |

## Combat and action timing

Four skills, one subject, and they compose in this order:

```
ue-action-time-windows      startup / active / recovery / buffer / cancel
        |
ue-anim-montages-notifies   the montage, its sections, the notifies that open the windows
        |
ue-combo-systems            the graph of edges between those windows
        |
ue2d-hitboxes-and-combat    the hitbox and hurtbox contract (2D, but the model is general)
```

A combo edge is only legal inside a window on a montage. Reaching for the combo graph before the windows exist is the common mistake.

## 2D track

| Need | Skill |
|---|---|
| Starting or structuring a 2D game | [ue2d-architect](ue2d-architect/SKILL.md) |
| Project setup, blurry pixel art, sort order | [ue2d-paper2d-foundations](ue2d-paper2d-foundations/SKILL.md) |
| Flipbooks and PaperZD state machines | [ue2d-flipbook-animation](ue2d-flipbook-animation/SKILL.md) |
| Jump feel, coyote time, variable height | [ue2d-platformer-controller](ue2d-platformer-controller/SKILL.md) |
| Tile maps, Tiled import, snagging on seams | [ue2d-tilemap-levels](ue2d-tilemap-levels/SKILL.md) |
| Camera feel, jitter, room bounds | [ue2d-camera-2d](ue2d-camera-2d/SKILL.md) |
| Scrolling backgrounds and depth | [ue2d-parallax-backgrounds](ue2d-parallax-backgrounds/SKILL.md) |
| Melee, projectiles, multi-hits, impact | [ue2d-hitboxes-and-combat](ue2d-hitboxes-and-combat/SKILL.md) |
| Flat-looking art, sprites ignoring lights | [ue2d-sprite-lighting](ue2d-sprite-lighting/SKILL.md) |

## Engine-agnostic

[`drag-drop-raycaster`](drag-drop-raycaster/SKILL.md) is the math, not the engine: screen-to-world rays, ray-plane intersection, grab offset, slot snapping. TypeScript/Three.js and Unreal C++.

## Reaching out of this category

| Need | Where |
|---|---|
| Sound effects, dialogue, audio pipeline | [`Audio`](../Audio/MAP.md) |
| Characters, props, rigging | [`3DModeling`](../3DModeling/MAP.md) |
| Sprite sheets and SubUV atlases | [`Graphics2D`](../Graphics2D/MAP.md) |
| A devlog or jam writeup from the real record | [`Narrative`](../Narrative/MAP.md) |
| The FSM theory behind the UE state machines | [`state-machine-architect`](../Development/state-machine-architect/SKILL.md) |
| Proving an ordering bug in a game flow | [`statechart`](../Verification/statechart/SKILL.md) |
