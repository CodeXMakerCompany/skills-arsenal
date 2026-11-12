---
name: ue-3d-architect
description: Design and structure a 3D indie game in Unreal Engine as an architect - shapes before assets, always. Derives every world dimension from the character's measured metrics (capsule, step height, jump apex, reach), scripts a colour-coded greybox out of BasicShapes primitives, validates it by playing the box, and only then swaps meshes in while keeping the blockout as the collision and metric source of truth. Also maps the spatial blockout onto the actor and class architecture that implements it. Use when starting a 3D level or game, planning scope and structure, greyboxing, whiteboxing, blocking out a space, deciding spatial metrics, or when a level built straight from art assets no longer plays correctly. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 3D Architect

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


An architect does not start with marble. You start with the grid, the dimensions and the
volumes, and you prove the space works while it is still free to destroy.

**The law of this skill: no imported art until the greybox plays.** Shapes are not a
sketch of the level — they *are* the level. The mesh pass is a skin applied later over a
structure that already works.

Why this is not optional:

| Starting with art | Starting with shapes |
|-------------------|----------------------|
| A corridor is wrong → remodel, re-UV, re-import | Change one scale value |
| Scale errors hide behind detail until playtest | Scale errors are the only thing visible |
| You defend the asset you spent hours on | Nothing is precious, so it gets fixed |
| Frame cost unknown until it is too late | Frame budget measured on an empty frame |

## 1. The metric contract

Everything in the level is derived from the pawn. Measure the pawn first; never guess.
In Unreal **1 uu = 1 cm**, and that convention must hold everywhere or physics, speeds
and cameras all drift.

```python
# In the editor, against the real character
c = actor.get_editor_property('capsule_component')
print(c.get_editor_property('capsule_radius'), c.get_editor_property('capsule_half_height'))
m = actor.get_editor_property('character_movement')
print(m.get_editor_property('max_walk_speed'), m.get_editor_property('jump_z_velocity'),
      m.get_editor_property('max_step_height'), m.get_editor_property('gravity_scale'))
```

Defaults for `ACharacter`, as the baseline to compare against:

| Property | Default | Meaning for the architecture |
|----------|---------|------------------------------|
| Capsule radius | 34 uu | Minimum gap the pawn can physically enter |
| Capsule half height | 88 uu | Pawn is 176 uu tall; crouch clearance below that |
| `MaxStepHeight` | 45 uu | Anything under this is free to walk over; at 46 it is a wall |
| `WalkableFloorAngle` | 44.77° | Steeper than this is not a ramp, it is scenery |
| `JumpZVelocity` | 420 uu/s | Apex = v² / (2 · 980) |

Derive the apex once and write it down — it sets every ledge, ceiling and gap in the
level:

```
apex (cm) = JumpZVelocity² / (2 · 980 · GravityScale)

420 → 90 cm        560 → 160 cm        700 → 250 cm
```

Then the whole dimension sheet falls out of three numbers:

| Element | Rule | With a 170 uu character, jump 560 |
|---------|------|-----------------------------------|
| Doorway width | ≥ 3 × capsule radius | 120 uu tight, 200 uu comfortable |
| Doorway height | character + 40 | 210 uu |
| Corridor | 1 pawn 150, 2 abreast 300 | 250 uu for combat movement |
| Ceiling in a fight room | character + apex + 50 | 380 uu minimum |
| Climbable ledge | ≤ apex − 20 safety | 140 uu |
| Hard wall | > apex + character | 350 uu (this project used 300 + collision) |
| Cover, crouch-high | ~0.55 × character | 95 uu |
| Cover, chest-high | ~0.75 × character | 128 uu |
| Walkable step | ≤ `MaxStepHeight` − 5 | 40 uu |

Keep the sheet in the repo (`docs/METRICS.md`). It is the single thing every later
decision — animation, camera, art, collision — has to agree with.

## 2. Snap discipline

Pick the grid before the first box and never fight it:

| Grid | Use for |
|------|---------|
| 500 uu | Room and building footprints |
| 100 uu | Walls, floors, major volumes |
| 50 uu | Doors, cover, platforms |
| 10 uu | Props and trim only |

Everything structural lands on 100 uu. Off-grid geometry is the main cause of the
unfixable 3 uu gap you find three weeks later with light leaking through it.

## 3. Build the box

Primitives live in `/Engine/BasicShapes/`: `Cube`, `Plane`, `Cylinder`, `Sphere`, `Cone`.
The `Cube` is 100 uu per side, so **scale = desired size / 100** and the `Plane` is also
100 uu, which makes a floor trivially `size/100`.

Drive it from a table, not by hand. A table is diffable, reviewable and regenerable:

```python
import unreal

ACTOR_LIB = unreal.EditorActorSubsystem()
CUBE = unreal.load_asset('/Engine/BasicShapes/Cube')

# name,              centre (x,y,z),        size (x,y,z)
BLOCKOUT = [
    ('Floor_Arena',  (0, 0, -5),            (4000, 4000, 10)),
    ('Wall_N',       (2020, 0, 150),        (40, 4080, 300)),
    ('Wall_S',       (-2020, 0, 150),       (40, 4080, 300)),
    ('Cover_A',      (600, -300, 47),       (200, 60, 95)),
    ('Plat_01',      (1200, 400, 70),       (300, 300, 20)),
]

for name, (x, y, z), (sx, sy, sz) in BLOCKOUT:
    a = ACTOR_LIB.spawn_actor_from_object(CUBE, unreal.Vector(x, y, z))
    a.set_actor_label(name)
    a.set_actor_scale3d(unreal.Vector(sx / 100.0, sy / 100.0, sz / 100.0))
```

Two things that save hours:

- **Centre, not corner.** Spawn positions are centres, so a 300 uu wall sits at `z = 150`.
  Half the misaligned blockouts in existence are a forgotten `/2`.
- **Overlap the corners.** Four walls at exactly the footprint leave four corner gaps.
  Make each wall `footprint + thickness` long, as `Wall_N` above does (4080 for a 4000
  arena with 40 thick walls).

Place that blockout through the actor toolset in the open editor. The Python is the
metric contract: centres, scale, corner overlap. Do not generate the level from a
commandlet unless the level tools fail. On 5.2, remote `new_level` could crash the
editor with a world GC leak; that is a fallback hazard, not the default path.

## 4. Make the box readable

A uniformly grey greybox cannot be reviewed. Colour is function, and this is the step
most people skip:

| Colour | Means | Becomes |
|--------|-------|---------|
| Grey | Walkable floor, neutral | Environment mesh |
| Dark grey / black | Hard blocking, no traversal | Walls, cliffs |
| Blue | Interactive, player-usable | Doors, levers, pickups |
| Red | Hazard or enemy volume | Damage, spawners |
| Yellow | Objective, goal, reward | Goal actor, chests |
| Green | Spawn and checkpoint | PlayerStart, respawn |

One unlit master material with a `Color` parameter plus six instances is enough. Unlit
matters: you are judging **shape and reach**, and lighting at this stage lies to you.

Leave the lighting rig minimal and fixed — one directional sun, SkyLight, atmosphere —
so that every review of the box is a review of the same box.

## 5. Play the box, then fix the box

The greybox has to be playable within the first session. Required loop: possess the pawn
and move through the whole space before any mesh exists.

Checklist, all answered by playing and measuring, not by looking:

- Can the pawn enter every gap it should, and none it should not?
- Is every ledge marked "climbable" actually reachable from where the player stands?
- Does any 45–50 uu step read as walkable but block? (Classic `MaxStepHeight` cliff.)
- Can you tell where to go, from the start position, with no art and no HUD?
- Is the longest sightline intentional, or did you just build a stadium?
- Does the camera collide anywhere it pulls in and shows the void?

Measure distances instead of eyeballing them:

```python
import unreal
al = unreal.EditorActorSubsystem().get_all_level_actors()
d = {a.get_actor_label(): a.get_actor_location() for a in al}
print((d['Plat_01'] - d['Cover_A']).length())   # uu between two volumes
```

When something is wrong, fix the **table** and re-run, not the actor in the viewport.
The table stays the source; hand edits in the viewport lose the next time it regenerates.

## 6. Spatial composition for an indie scope

Indie means the level cannot afford breadth, so it has to work on structure.

- **One landmark, visible from most of the space.** It replaces a minimap for free.
- **Three-beat loop.** Teach → test → twist. One mechanic introduced in a safe room,
  used under pressure, then recombined. This is a level structure, not a tutorial.
- **Pacing in volumes.** Alternate tight (≤300 uu wide) and open (≥1500 uu). A level of
  uniform width feels the same for its whole length regardless of the art.
- **Gates, not corridors.** Progression reads better as a thing opening than as a long
  walk. A gate is one blue box.
- **Build the smallest closed loop first.** Start → one obstacle → reward → back to start.
  If that is not fun as grey boxes, no amount of art will rescue it, and you have lost one
  afternoon instead of three weeks.

## 7. The code architecture under the box

The coloured volumes are the class diagram. Map them one-to-one and the project stays
navigable:

| Blockout element | Class | Owns |
|------------------|-------|------|
| Green spawn | `PlayerStart` + `AGameModeBase` | Rules, score, spawn policy |
| Blue interactive | `AActor` with overlap + interface | Its own behaviour only |
| Red hazard / spawner | A spawner actor with a timer | Spawn cadence, live cap |
| Yellow objective | A pickup actor | Its own state, reports upward |
| The pawn | `ACharacter` subclass | Movement, input, self-knowledge |
| The readout | `AHUD` subclass | Reads state, writes nothing |

Three rules that keep an indie C++ project from collapsing on itself:

1. **State flows up, never sideways.** A pickup tells the character it was collected; it
   does not reach into the HUD. The HUD reads. Actors that know about each other are the
   thing that makes a jam project unmergeable on day three.
2. **No `Tick` for anything with a period.** Waves, cooldowns, respawns and timed glows
   are `FTimerManager`. Tick is for per-frame interpolation only.
3. **Expose every tuning number as `EditAnywhere`.** Speeds, radii, counts, intervals.
   The metrics sheet lives in the header; the balance pass happens in the editor without
   a rebuild.

## 8. The swap pass

Only now does art enter. The blockout stays, demoted to reference and collision:

1. **Freeze the metrics.** The art fits the box. If a mesh requires a wider door, that is
   a metrics change, reviewed as such — not a quiet nudge of one wall.
2. **Collision from the box, not the mesh.** Keep simple primitives for collision and set
   the art mesh to no collision where possible. Per-poly collision on decorative meshes is
   a frame-cost and gameplay-feel mistake at the same time.
3. **One category at a time.** All floors, then all walls, then props. Play after each
   category. A level that broke somewhere in a 40-mesh swap is much harder to diagnose.
4. **Keep the greybox in a hidden layer.** It is the diff: when the space stops playing
   right, toggle it back on and find which mesh moved the effective geometry.
5. **Re-measure the frame.** Shapes cost nothing; the art is the whole budget. Take the
   before number on the greybox so the after number means something.

## Anti-patterns

- **Downloading a mega-pack on day one.** The level then gets designed around what is in
  the pack. Scope and structure get decided by a store page.
- **Starting from a full template map.** Open World ships over a million primitives of
  somebody else's decisions. Save it aside, build the minimal level, measure the empty
  frame.
- **Greyboxing in a modelling tool.** It has to be playable to be judged. Build it in
  engine, with the real pawn.
- **Off-grid "just for now".** It is never just for now.
- **Beautiful lighting on a greybox.** Mood hides broken reach and broken scale. Flat and
  unlit until the box plays.
- **One `BP_Everything`.** If the blockout has six colours and the project has one actor
  class, the architecture does not exist yet.
