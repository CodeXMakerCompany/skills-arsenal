---
name: meshy-tripo-3d-pipeline
description: Prompt engineering, API workflow, mesh cleanup and engine import checks for AI 3D generation with Meshy and Tripo (text-to-3D and image-to-3D). Use when generating game-ready props, creatures, characters or environment pieces as GLB/FBX with PBR textures, and when deciding what must be fixed before the asset enters Unreal, Unity, Godot or Blender.
---

# Meshy / Tripo AI Mesh Generation Pipeline

AI generators give a fast first pass, not a finished asset. The pipeline is: concept input, generate, inspect, clean, bake or retopo if needed, import, validate in-engine. Budget for the inspect and clean steps, that is where quality comes from.

## Before you start

1. Confirm the target: engine, platform, camera distance, role (hero, prop, background). This sets triangle budget, texture size and whether it needs a rig.
2. Check current API docs for the service you use. Parameter names and models change often (Meshy and Tripo both ship new model versions). Treat the examples below as the shape, verify field names before scripting.
3. Check the license and ownership terms of the plan you generate on (free tiers often restrict commercial use). Record the plan and date next to each asset.
4. Keep API keys in `.env` and never commit them.

## 1. Picking the input

| Input | Use when | Notes |
|-------|----------|-------|
| Text-to-3D | No reference exists, shape is simple | Fast to iterate, least control over proportions |
| Image-to-3D (single) | You have a concept or AI-generated image | Best control; quality depends on the image |
| Multi-image | You need back/side fidelity | Provide consistent views of the same object |

### Preparing the image
- One subject, centered, fully in frame, with margin around it.
- Plain neutral background (flat grey or white) or a clean alpha cut-out.
- Even, soft, shadowless lighting. Baked shadows and strong highlights get baked into the texture.
- Three-quarter or front view that shows the silhouette. For characters use an A-pose or T-pose with arms and legs separated if you plan to rig.
- High resolution (at least 1024 px on the long side), no compression artifacts, no text or watermark.
- Avoid: multiple objects, motion blur, extreme perspective, thin transparent parts (glass, wires), heavy occlusion.

## 2. Prompting (text-to-3D)

Structure: `[object] + [style/material] + [key features] + [pose/orientation] + [constraints]`

- Good: `Stylized wooden treasure chest, brass corners, hand-painted texture, closed lid, centered, neutral pose`
- Add what you want: shape language, materials, era, wear level.
- State the constraints: "single object", "no base or ground", "symmetrical".
- Avoid scenes, lighting words ("dramatic sunset"), camera words and long narrative text.
- Keep a prompt log (prompt, seed or task id, model version, date) so a result is reproducible or iterable.

## 3. Generation workflow (Meshy example)

Meshy separates stages. Text-to-3D uses a `preview` (geometry) then `refine` (texture) pass. Image-to-3D takes geometry and texture options in one request. Verify against the current docs.

```bash
# Create image-to-3D task (key from environment, never hardcode)
curl -s https://api.meshy.ai/openapi/v1/image-to-3d \
  -H "Authorization: Bearer $MESHY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/concept.png",
    "should_texture": true,
    "enable_pbr": true,
    "should_remesh": true,
    "topology": "triangle",
    "target_polycount": 15000,
    "symmetry_mode": "auto"
  }'
# -> returns a task id. Poll GET /openapi/v1/image-to-3d/{id} until status is SUCCEEDED,
#    then download from model_urls (glb, fbx, obj, ...). Do not block the UI thread polling.
```

Parameter guidance:

| Parameter | Guidance |
|-----------|----------|
| `target_polycount` | Set to your budget, not the maximum. Props 2k to 15k tris, hero assets 20k to 60k, mobile props under 5k |
| `topology` | `quad` for assets you will edit, subdivide or sculpt on; `triangle` for direct engine use |
| `symmetry_mode` | `auto` or `on` for symmetric objects; `off` for asymmetric or organic ones |
| `enable_pbr` | On for engine use (gives normal, metallic, roughness) |
| `should_remesh` | On for clean topology; off keeps raw geometry (often heavy and noisy) |
| `pose_mode` | `a-pose` or `t-pose` for characters that will be rigged |

Tripo follows the same task pattern (create task, poll, download). Typical controls: face limit, PBR on/off, quad topology, model version. Use its rig/animation features or a separate rigger (see `mixamo-auto-rig-mapper`) for characters.

Generate 3 to 4 variants and pick the best silhouette. Rerolling is cheaper than repairing.

## 4. Inspection checklist (do before anything else)

- [ ] Silhouette matches the concept from the main gameplay camera angle.
- [ ] No holes, floating islands, inverted normals, or non-manifold edges (Blender: Select > Select All by Trait > Non Manifold).
- [ ] Watertight if the mesh will be 3D printed, boolean-ed or used for physics; otherwise only confirm no open boundary in visible areas.
- [ ] Triangle count within budget.
- [ ] UVs present, no heavy stretching, no large overlapping islands, margins at least 4 px at 2K.
- [ ] Texture matches intent: no baked lighting, no seams on visible faces, no melted details at hands/faces/text.
- [ ] Scale and pivot sensible (see below).
- [ ] PBR maps present: BaseColor, Normal, Roughness, Metallic (and AO or Emissive if used).

## 5. Cleanup

1. Import into Blender (or similar). Apply transforms. Recalculate normals outward.
2. Remove loose geometry and internal faces. Merge by distance (small threshold).
3. Fix hot spots by hand: hands, eyes, thin parts, symmetry seams.
4. Reduce: Decimate (planar/collapse) only on non-deformable props; for deformable characters retopologize with edge loops at joints.
5. LODs: generate LOD1 to LOD3 by reduction (50%, 25%, 10%) or engine auto LOD. Check silhouette at each.
6. Retexture or touch up in a texture tool if the AI texture is soft; bake high-poly to low-poly normal map if you kept a dense source.
7. Collision: build simple collision (box, capsule, convex hull), never use AI mesh complexity as collision.

## 6. Scale, axes and import

| Space | Up | Forward | Unit |
|-------|----|---------|------|
| glTF / GLB | +Y | +Z | meters |
| Blender | +Z | -Y | meters (scene scale) |
| Unreal | +Z | +X | centimeters |
| Unity | +Y | +Z | meters |

- Export from Blender with the right axis settings for the target (FBX: forward -Z or -Y, up Y or Z per engine importer) or let the engine importer convert (Unreal Interchange handles glTF).
- Real-world size: set object size in the DCC first (a chair is about 0.9 m tall), then export. Do not fix scale with an engine multiplier.
- Pivot: bottom center for props that sit on ground; center for pickups; hand socket location for held items.
- Naming: `SM_` static mesh, `SK_` skeletal mesh, `T_<Name>_BC/N/R/M`, `M_`/`MI_` for materials. Keep a consistent prefix scheme per project.

## 7. Engine validation

- Imports without warnings; materials map to the right slots.
- Correct texture settings: BaseColor sRGB on; Normal as normal map; Roughness/Metallic/AO sRGB off. Pack ORM if the pipeline expects it.
- Flip the green channel if the normal map looks inverted (DirectX vs OpenGL).
- Lighting test: view under three lights (neutral, warm, dark) to find baked-in shadows.
- Performance: check draw calls, material instruction count, triangle count at expected on-screen density.

## 8. Best practices for better results

- Generate at the concept stage with a consistent art style guide; reuse the same style image or prompt prefix across assets.
- Treat each asset as a kit: generate parts separately (body, weapon, base) when you need modularity.
- Keep the original generated files (raw GLB, input image, prompt, task id) next to the cleaned asset for rework.
- Batch: script the create-poll-download loop with retries, rate limiting and a manifest (JSON) listing asset, prompt, params, status.
- Never ship an AI asset unreviewed. Review shapes at gameplay camera distance, in motion, under real lighting.
- Check content rights: do not input copyrighted characters or third-party art you do not own.

## Failure patterns

| Symptom | Fix |
|---------|-----|
| Blobby or melted details | Cleaner input image, higher polycount, or sculpt/repair manually |
| Lighting baked into texture | Re-shoot input with flat lighting, or paint out and re-bake |
| Asymmetric or lopsided result | `symmetry_mode: on`, front-facing symmetric input |
| Mesh too heavy | Lower `target_polycount`, remesh, then LODs |
| Rig deforms badly | Retopologize with loops at joints, A/T-pose input |
| Normal map looks inverted | Flip green channel on import |
| Wrong size in engine | Fix unit scale in DCC, re-export |
