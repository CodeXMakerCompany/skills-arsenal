---
name: ue2d-architect
description: Design and structure a 2D indie game in Unreal (Paper2D) as an architect - shapes before sprites, always. Fixes the pixel-to-unit contract and the tile grid, derives jump arc and reach in tiles, blocks the whole game out of flat colour-tinted rectangles on depth lanes, designs the room graph and the screen-sized composition, validates it by playing the rectangles, then swaps tilemaps and sprites in without moving a single collision edge. Also maps the blockout onto the actor, state and flipbook architecture. Use when starting a 2D level or game, planning its structure, greyboxing or blocking out 2D space, choosing tile size and pixel scale, laying out rooms and progression, or when a level built straight from art no longer plays correctly.
---

# UE 2D Architect

2D hides nothing. There is no depth to distract from a jump that falls one pixel short, so
the structure has to be right before any sprite exists.

**The law of this skill: no sprite art until the rectangles play.** Flat tinted boxes on a
tile grid are the level. Tilemaps and sprites are a skin applied later over geometry that
already works.

In 2D the cost of getting this wrong is worse than in 3D: a tileset bakes a tile size into
every image, and changing your mind means redrawing the art, not rescaling a box.

## 1. The pixel contract

Decide these four numbers before anything else and write them in `docs/METRICS.md`. Every
later decision depends on them, and changing one later invalidates all your art.

| Number | Typical | What it decides |
|--------|---------|-----------------|
| Tile size | 16, 32 px | The unit of all level geometry |
| Pixels per unit | **1** | How pixel coordinates map to world units |
| Internal resolution | 320×180, 384×216, 640×360 | How much the player sees at once |
| Character height | 1.5–2 tiles | Everything else scales from the pawn |

**Set pixels-per-unit to 1 on import.** Paper2D's default is 2.56, which makes one texel
0.39 uu and turns every level coordinate into a fraction. At 1, one pixel is one unreal
unit, the grid is integers, and nothing drifts. Do this on the first sprite you import —
mixing scales inside one project is painful to unwind.

With that convention, a 16 px tile is 16 uu and an orthographic width equal to the
internal resolution shows exactly one screen:

```
OrthoWidth = internal horizontal resolution        # 320 px -> 320
screen in tiles = OrthoWidth / tile size           # 320 / 16 = 20 tiles wide
rows visible    = 180 / 16 = 11.25 tiles
```

Keep `OrthoWidth` an integer multiple of the tile size, or the tile edges land between
screen pixels and the whole image shimmers when the camera moves.

Paper2D works on the **XZ plane**: X is horizontal, Z is vertical, Y is depth. All level
design happens in X and Z; Y is used only for the depth lanes in section 3.

## 2. Reach, in tiles

Express every movement capability in **tiles**, not pixels. Tiles are what the player
reads, and tile counts survive a change of tile size.

```
jump height (uu)  h = v² / (2 · 980 · GravityScale)
velocity for h    v = sqrt(2 · 980 · GravityScale · h)
time to apex      t = v / (980 · GravityScale)
```

With a 16 uu tile and `GravityScale = 1`:

| Jump of | h (uu) | `JumpZVelocity` | Apex time |
|---------|--------|-----------------|-----------|
| 2 tiles | 32 | 250 | 0.26 s |
| 3 tiles | 48 | 307 | 0.31 s |
| 4 tiles | 64 | 354 | 0.36 s |
| 5 tiles | 80 | 396 | 0.40 s |

Aim for an apex between **0.25 s and 0.35 s**. Slower reads as floating, faster reads as a
twitch. If the apex feels wrong at the height you want, raise `GravityScale` and recompute
the velocity — do not change the tile size.

Then derive the geometry vocabulary, and only build out of it:

| Element | Rule | 16 px tile, 3-tile jump |
|---------|------|-------------------------|
| Platform step up | ≤ jump − 1 tile safety | 2 tiles |
| Hard wall | > jump + character | 5 tiles |
| Gap the player must clear | run speed × apex time × 2 × 0.8 | compute once, then round to tiles |
| Passage height | character + 1 tile | 3 tiles |
| Crawl space | character − 1 tile | 1 tile |
| Ceiling over a jump | jump + character + 1 | 6 tiles |

That last column is the only legal vocabulary for the level. A level built from "2, 3 and
5 tiles" is readable; a level built from arbitrary pixel heights teaches the player
nothing and plays by trial and error.

## 3. Depth lanes

2D has one axis of structure that is pure architecture: Y. Assign it up front, in bands,
and never improvise.

| Lane (Y) | Contents | Collides |
|----------|----------|----------|
| −300 | Sky / far parallax | no |
| −200 | Mid background | no |
| −100 | Near background, decoration behind play | no |
| **0** | **Gameplay: pawn, enemies, platforms, pickups** | yes |
| +100 | Foreground decoration, overdraw | no |
| +200 | Vignette, weather, screen effects | no |

One rule: **collision exists on lane 0 only.** The moment a background element collides,
or a gameplay element drifts off 0, you get bugs that are invisible on screen and
impossible to reason about. Sort order within a lane is a separate control; the lanes
prevent the fight in the first place.

## 4. Block it out with rectangles

You need exactly one art asset: a solid white sprite, 8×8 px, imported with
pixels-per-unit 1. Everything in the blockout is that sprite, scaled and tinted.

```python
import unreal

SUB   = unreal.EditorActorSubsystem()
WHITE = unreal.load_asset('/Game/Blockout/S_White')
TILE  = 16.0

PALETTE = {                       # function, not decoration
    'floor':  unreal.LinearColor(0.35, 0.35, 0.35, 1),
    'wall':   unreal.LinearColor(0.10, 0.10, 0.10, 1),
    'moving': unreal.LinearColor(0.20, 0.45, 0.95, 1),
    'hazard': unreal.LinearColor(0.90, 0.15, 0.15, 1),
    'goal':   unreal.LinearColor(0.95, 0.85, 0.15, 1),
    'spawn':  unreal.LinearColor(0.20, 0.85, 0.30, 1),
}

# kind,      tile x, tile z, tiles wide, tiles tall
ROOM = [
    ('floor',  0,  0, 20, 1),
    ('wall',   0,  1,  1, 10),
    ('floor',  6,  3,  3, 1),
    ('hazard', 10, 1,  2, 1),
    ('goal',   18, 4,  1, 1),
    ('spawn',  1,  1,  1, 2),
]

for kind, tx, tz, w, h in ROOM:
    loc = unreal.Vector(tx * TILE + w * TILE / 2, 0.0, tz * TILE + h * TILE / 2)
    a = SUB.spawn_actor_from_class(unreal.Actor, loc)
    sc = unreal.PaperSpriteComponent()                    # or a sprite actor class
    a.set_actor_label(f'{kind}_{tx}_{tz}')
    a.set_actor_scale3d(unreal.Vector(w * TILE / 8.0, 1.0, h * TILE / 8.0))
```

What matters in that snippet, regardless of how you spawn the actors:

- **Coordinates are tile indices**, converted once. Never type a pixel coordinate by hand.
- **Spawn location is the rectangle's centre**, hence the `+ size/2`. The missing `/2` is
  the single most common blockout bug.
- **The table is the level.** It is diffable, reviewable and regenerable. Fix the table and
  re-run; never hand-move a rectangle in the viewport, because the next run loses it.
- **Colour is function**, with the same palette as the 3D blockout so reviews transfer.

Keep the blockout **unlit**. You are judging reach and readability, and a lit greybox lies
about both.

## 5. Structure above the room: the graph

Before building the second room, draw the whole game as a graph — in a markdown file, not
in the engine:

```
[start] --> [teach: jump] --> [teach: hazard] --+--> [key A] --+
                                                 |             |
                                                 +--> [gate A] --> [boss] --> [end]
```

Rules that make an indie 2D game hold together:

- **One screen, one idea.** If a screen teaches two things, the player learns neither.
- **Rooms are whole screens.** Size rooms in multiples of the screen (1×1, 2×1, 1×2). The
  camera then has natural clamp bounds and never shows the void.
- **Teach → test → twist.** Introduce a mechanic with no threat, test it with threat, then
  combine it with an earlier one. This triple is one act.
- **Critical path first.** Build start-to-end as rectangles with zero optional content. If
  the critical path is not fun grey, nothing bolted on later will fix it.
- **Backtracking must be shorter than the way out.** Mark the shortcut on the graph before
  building it, or the level turns into a walk.

Count the rooms on the graph and multiply by your real per-room build time. This is the
moment scope gets decided — while it costs a line in a text file to cut one.

## 6. Play the rectangles

Mandatory before any art. Possess the pawn and traverse the critical path.

- Does every jump marked "2 tiles" actually clear with the real `JumpZVelocity`?
- Is any required jump **exactly** at the maximum? Leave one tile of margin; players do
  not play at frame-perfect precision.
- From a standing start, is the next destination visible on screen? If not, the player is
  jumping on faith.
- Can the player tell hazard from floor by **shape and position alone**? Colour is not
  enough; a hazard whose silhouette matches the floor will keep killing people after the
  art pass.
- Does the camera ever show outside the room bounds?
- Walk the whole path backwards. Many 2D levels are only solvable in one direction by
  accident.

Fix the table, re-run, play again. The loop should take under a minute.

## 7. The code architecture under the rectangles

The palette is the class list:

| Blockout kind | Class | Owns |
|---------------|-------|------|
| `spawn` | `PlayerStart` + GameMode | Rules, lives, checkpoint policy |
| `floor` / `wall` | Tilemap collision layer (one, later) | Nothing — geometry only |
| `moving` | A platform actor with a timeline or timer | Its own path |
| `hazard` | A hazard actor with an overlap hurtbox | Damage, nothing else |
| `goal` | A pickup / trigger actor | Reports upward, does not open doors itself |
| pawn | `APaperCharacter` subclass | Movement, input, its own state |
| the look | An AnimInstance / PaperZD state machine | Reads state, never writes it |

Three rules specific to 2D:

1. **State decides the flipbook; the flipbook never decides state.** The animation layer is
   a pure reader of velocity, grounded-ness and an action enum. A flipbook that sets
   gameplay state produces bugs that look like animation glitches.
2. **Separate hitbox and hurtbox channels** from the start, even in the blockout. Retrofitting
   collision channels after 40 actors exist is a day of work.
3. **One collision layer in the tilemap.** Per-tile collision on multiple layers produces
   invisible double walls and pawns that stick on nothing.

## 8. The swap pass

The rectangles stay; the art arrives on top of geometry that already plays.

1. **Tilemap first, then characters, then decoration.** Play after each stage.
2. **The art fits the grid.** A tileset drawn at 16 px must stay at 16 px. If art needs a
   different tile size, that is a metrics decision for the whole project, not a per-asset
   nudge.
3. **Collision stays where the rectangles were.** Author tile collision flush with the tile
   bounds and compare against the blockout: if a jump that cleared grey now fails, the
   collision moved, not the player.
4. **Keep the blockout in a hidden layer** as the diff. Toggling it back on and seeing a
   platform offset by three pixels takes seconds; finding it in the tilemap takes an hour.
5. **Re-check the pixel grid after art.** Non-integer camera positions or a non-multiple
   `OrthoWidth` only become visible once there is real texture detail — and then it looks
   like the art is broken when it is the camera.

## Anti-patterns

- **Buying a tileset first.** The tile size, the palette and the level vocabulary all get
  decided by someone else's asset pack.
- **Designing in a drawing tool.** A level has to be played to be judged. Rectangles in
  engine, with the real pawn.
- **Pixel coordinates by hand.** Everything is tile indices converted once, or the level
  slowly goes off-grid.
- **Collision on a background lane.** Invisible walls that cannot be found by looking.
- **Maximum-distance jumps as required path.** Feels unfair even when it is possible.
- **Lighting and post on a blockout.** Hides exactly the problems the blockout exists to
  expose.
- **Building all rooms before playing one.** The critical path end to end, as rectangles,
  comes first.
