---
name: ue2d-tilemap-levels
description: Build 2D levels in Unreal Engine 5 with Paper2D tile maps - tile sets and per-tile collision, layer structure for background, gameplay and foreground, importing Tiled .json/.tmx maps, chunking large levels for streaming, and the collision pitfalls that make a player snag on flat ground. Use when building 2D levels, when a character catches on seams between tiles, when importing from Tiled, or when deciding between tile maps and hand-placed sprites. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Tile Map Levels

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Paper2D tile maps give you a grid editor, batched rendering and per-tile collision. The
two things that go wrong are collision seams and layer discipline, and both are decided
when the tile set is authored.

> Written from general Paper2D tile map practice rather than verified end to end in one
> project.

## Before you start

1. **Enable "Paper2D Tile Map Editor"** — it is a separate plugin from Paper2D.
2. **Fix the tile size first.** 16, 32 or 64 px. Changing it later re-cuts every tile set
   and invalidates every map.
3. **Decide the authoring tool.** The in-engine editor is fine for small maps; past a
   screen or two, Tiled is far faster and imports cleanly.

## 1. Tile set and per-tile collision

Create a Tile Set from the source texture, set tile size and any margin/spacing, then
edit collision **per tile** in the Tile Set Editor.

Keep collision shapes simple and, above all, **flush with the tile bounds**. A box inset
by one pixel on a ground tile creates a one-pixel lip at every tile boundary, and a
character running across flat ground catches on each seam. The symptom is a stutter that
looks like a physics bug and is a collision authoring bug.

Give slopes a single triangle, not a staircase of boxes. Leave decorative tiles with no
collision at all rather than a shape nothing touches.

## 2. Layers

| Layer | Collision | Y offset |
|-------|-----------|----------|
| `BG_Far` | none | +400 |
| `BG_Near` | none | +200 |
| `Collision` | **yes** | 0 |
| `Decoration` | none | 0 |
| `FG_Overlay` | none | -200 |

Exactly one layer owns collision. Two colliding layers produce double contacts and
unpredictable resolution, and the cause is invisible in the viewport.

## 3. Importing from Tiled

Tiled `.json` and `.tmx` import through the Paper2D importer, carrying layers, tile sets
and most properties. The usual friction:

- **Embed, do not link, the tile set** in the export, or the importer cannot resolve it.
- **Match tile size exactly** between Tiled and the UE tile set.
- **Custom properties** come through as metadata; read them to place spawns and triggers
  from the map rather than by hand.
- **Object layers** do not become actors automatically. Write an import script that walks
  the objects and spawns actors from a name-to-class table.

Re-importing replaces tile data and keeps the asset's references, so an iteration loop
through Tiled is practical. Verify once that your spawn-placing script is idempotent
before relying on it.

## 4. Large levels

A single enormous tile map is one actor, one draw batch per layer, and no streaming.
Past roughly 200×200 tiles, split into chunks placed as separate tile map actors in
sub-levels, and stream by distance.

Keep each chunk's origin on a tile boundary; off-grid chunk origins produce a half-pixel
seam at every join, which is the other common source of visible lines between tiles.

## 5. Tile maps or hand-placed sprites?

| Use tile maps | Use sprites |
|---------------|-------------|
| Grid-aligned terrain | Freely placed props |
| Large repeating areas | Unique set pieces |
| Level design that iterates fast | Anything that moves |
| Batched rendering matters | A handful of objects |

Most 2D levels want both: tile map terrain plus sprite actors for anything interactive.
Do not model moving platforms as tiles — they are actors.

## 6. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Character snags on flat ground | Per-tile collision inset from the tile bounds | Make it flush |
| Visible seams between tiles | Texture bleed from filtering or mips, or off-grid chunks | Nearest filter, no mips, add padding, align chunks |
| Double collision responses | More than one layer with collision | One collision layer only |
| Tiled import has no tile set | Tile set linked rather than embedded | Re-export embedded |
| Spawn points missing after import | Object layers are data, not actors | Script actor placement from the objects |
| Editor crawls on a big map | One huge tile map actor | Chunk into sub-levels |
| Tiles render behind the background | Layer Y offsets not separated | Give layers distinct Y |

Related: [[ue2d-paper2d-foundations]], [[ue2d-platformer-controller]], [[ue2d-camera-2d]].
