---
name: ue2d-sprite-lighting
description: Lighting and materials for 2D sprites in Unreal Engine 5 - choosing between unlit and lit sprite materials, normal maps on sprites for dynamic light, 2D-friendly light setups, emissive glow and rim effects, masked versus translucent alpha and what each costs, and flash and dissolve material parameters driven from gameplay. Use when 2D art looks flat, when sprites ignore lights, when alpha edges look wrong, or when adding hit flashes and glow effects to a 2D game. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 2D Sprite Lighting and Materials

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Paper2D defaults to **unlit**, which is correct for most pixel art and wrong the moment
you want dynamic light. Both are valid; the decision drives everything else.

> Written from general practice rather than verified end to end in one Unreal project.

## Before you start

1. **Decide unlit or lit, per project not per sprite.** Mixing them in one scene makes
   the lit sprites look like stickers next to the unlit ones.
2. **Know your alpha mode.** Masked and translucent behave very differently for sorting
   and cost (section 3).
3. **If you want normal maps, author them with the art.** Generating them from a diffuse
   afterwards rarely survives contact with pixel art.

## 1. Unlit, lit, and the middle ground

| Approach | Use when | Cost |
|----------|----------|------|
| `DefaultSpriteMaterial` (unlit) | Pixel art with baked lighting | Cheapest |
| `DefaultLitSpriteMaterial` | Sprites must react to dynamic light | Moderate |
| Lit + normal map | 2.5D look, moving lights | Highest, usually worth it |
| Unlit + emissive-only highlights | Retro look with glow | Cheap, very controllable |

The last row is underrated: keep everything unlit and fake "light" with emissive masks
and additive sprites. It is cheap, art-directable, and never fights the renderer.

## 2. Normal maps on sprites

A sprite is a quad facing the camera, so a normal map gives it apparent surface relief.
Make a master material with `BaseColorTexture` and `NormalTexture` parameters, derive an
instance per character, and keep the normal map the same dimensions and alignment as the
diffuse — any offset reads as lighting sliding across the sprite.

With an orthographic camera and a directional light, the sprite's normal must point at
the camera (`-X` on the XZ plane, with the camera looking down `+X`) for the tangent
space to behave.

## 3. Masked or translucent

| | Masked | Translucent |
|---|--------|-------------|
| Alpha | Binary, cut by an opacity mask | Continuous |
| Depth write | Yes | No |
| Sorting | Automatic | Manual, by sort order |
| Cost | Lower | Higher, and no z-cull |
| Right for | Pixel art, hard edges | Soft edges, fades, glows |

**Masked for pixel art, always.** Pixel art alpha is binary anyway, and masked keeps
automatic depth sorting, which removes a whole class of ordering bugs.

Translucent is correct for smoke, glows and fades — accept that you now own the sort
order. A full-screen translucent layer also does not z-cull, which is the usual cause of
a 2D game being unexpectedly fill-bound.

## 4. Gameplay-driven parameters

Expose parameters and drive them from a dynamic material instance:

| Parameter | Type | Use |
|-----------|------|-----|
| `FlashAmount` | Scalar 0–1 | White flash on hit |
| `FlashColor` | Vector | Red for damage, white for parry |
| `Dissolve` | Scalar 0–1 | Death and spawn |
| `Tint` | Vector | Team colour, status |
| `EmissiveStrength` | Scalar | Charge-up, pickups |

```cpp
// Lerp base colour toward FlashColor by FlashAmount in the material.
FlashMID->SetScalarParameterValue(TEXT("FlashAmount"), 1.0f);
GetWorldTimerManager().SetTimer(FlashTimer, [this]()
{
    FlashMID->SetScalarParameterValue(TEXT("FlashAmount"), 0.0f);
}, 0.08f, false);
```

Create the instance once in `BeginPlay`, never per frame, and only push a parameter when
the value actually changed — the same discipline as [[ue-proximity-reactions]], which has
the full reasoning and the material-authoring script.

## 5. Lighting a 2D scene

- **Point lights** with a large attenuation radius and low intensity read as ambient
  pools; keep them in the gameplay plane or they light the sprite's edge oddly.
- **A single directional light** at a shallow angle plus a skylight for fill is enough
  for most lit 2D.
- **Shadows**: sprites casting real shadows onto other sprites usually looks wrong.
  Disable shadow casting and fake contact shadows with a blob sprite under the character.
- **Post process**: bloom on emissive highlights is the one post effect that reliably
  improves 2D. Keep the rest off — see [[ue2d-paper2d-foundations]].

## 6. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Sprites ignore every light | Unlit material | Switch to a lit sprite material |
| Lit sprites look like flat cards | No normal map | Add one, aligned to the diffuse |
| Lighting slides across the sprite | Normal map offset or wrong dimensions | Match the diffuse exactly |
| Soft halo around pixel art | Translucent with bilinear filtering | Masked material, nearest filter |
| Sprites sort unpredictably | Translucent where masked would do | Use masked, or set sort order explicitly |
| Fill-bound with few objects | Full-screen translucent layers | Make them opaque or masked |
| Flash effect stutters | Creating a dynamic instance per flash | Create once in `BeginPlay` |
| Shadows look wrong | Sprites casting real shadows | Disable casting; fake a blob shadow |

Related: [[ue2d-paper2d-foundations]], [[ue-proximity-reactions]],
[[ue-material-instance-builder]], [[ue2d-parallax-backgrounds]].
