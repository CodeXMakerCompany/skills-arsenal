---
name: mixamo-auto-rig-mapper
description: Auto-rigging and animation retargeting for humanoid 3D meshes using Mixamo, Tripo or Meshy rigging, then importing into Unreal Engine 5 (also Unity, Godot). Use when turning a static character mesh into an animated skeletal mesh, downloading locomotion and combat animation sets, or retargeting animations with IK Retargeter.
---

# Auto-Rig & Animation Retargeting

Auto-riggers solve humanoid skeletons well and everything else poorly. Decide first whether the character is a fit, prepare the mesh, rig, download a consistent animation set, then retarget and verify in-engine.

## Before you start

1. Is the character humanoid (head, torso, two arms, two legs)? If not (quadruped, insect, blob, extra limbs), Mixamo will fail or produce junk. Use a custom rig, a creature-specific rigger, or hand-rig in Blender.
2. Check current tool terms: Mixamo is an Adobe service; confirm the license for commercial use and the current upload limits (format, file size, polygon count). Limits have changed over time and sources disagree, so check Adobe's help page.
3. Pick the target skeleton: Mixamo skeleton as-is, or retarget onto the Unreal Mannequin / your project skeleton.

## 1. Mesh preparation

- Pose: T-pose (best) or A-pose, arms away from the body, palms down, fingers slightly separated, legs shoulder width apart. Gaps between arms and torso and between legs matter.
- Facing: front facing the engine-neutral forward direction the rigger expects (Mixamo expects the character looking along +Z in a Y-up view; the upload preview shows it). Verify in the preview and rotate before uploading rather than trusting a rule.
- One mesh, one material set. Join eyes, teeth, hair cards and small accessories into the body mesh or plan to parent them separately (props to sockets, not skinned to the body).
- Remove: loose geometry, internal faces, hidden helper meshes, cameras, lights, empty nodes.
- Clean topology: no non-manifold edges, no inverted normals, no overlapping interior shells. Apply transforms (scale 1, rotation 0).
- Triangle count: keep it moderate. Heavy AI meshes (100k+ tris) fail or deform poorly; remesh to roughly 10k to 40k for the rigger and use LODs in engine.
- Export FBX (or OBJ) with textures embedded or in the same ZIP. Keep the file size within the service limit.
- Dense hands and loose clothing (long coats, capes, skirts) deform poorly. Plan secondary physics or cloth for those parts.

## 2. Marker placement (Mixamo auto-rigger)

| Marker | Place at |
|--------|----------|
| Chin | Bottom of the jaw, center |
| Wrists | Center of the wrist, where the hand starts |
| Elbows | Outer side of the elbow bend |
| Knees | Front center of the knee |
| Groin | Base of the pelvis, between the legs |

- Use the symmetry option and check both sides.
- Finger skeleton: choose 5 fingers if the hands are detailed, or fewer/none for mitts or claws.
- Check the rig preview with the sample animation. Look at shoulders, hips, hands, jaw. If deformation is broken, fix the mesh or marker, do not accept and hope.

## 3. Animation set to download

Define the set per game, not per habit. A starter set for an action character:

| Clip | Options |
|------|---------|
| `Idle` | With Skin (once per character), 30 FPS |
| `Walk_InPlace` | Without Skin, In Place on |
| `Run_InPlace` | Without Skin, In Place on |
| `Turn` / `Strafe` variants | Without Skin, In Place on |
| `Jump` (start, loop, land) | Without Skin, root motion decision below |
| `Attack_*` | Without Skin |
| `Hit_Reaction` | Without Skin |
| `Death` | Without Skin |

- Download the skinned file once (Idle with skin) as the skeletal mesh source. Download all other animations Without Skin.
- Settings: FBX Binary, 30 FPS, Keyframe Reduction none (or uniform), Skin: With Skin only for the first file.
- "In Place" gives locomotion cycles that the movement component drives. For attacks with forward lunge or dodge, keep root motion (do not use In Place) and enable root motion in the engine only for those clips.
- Name files consistently: `<Char>_Idle`, `<Char>_Walk_IP`, `<Char>_Attack_Slash01`. Keep the source of each clip in a manifest.

## 4. Importing into Unreal Engine 5

1. Import the skinned FBX as a Skeletal Mesh. Check "Import Mesh", "Import Skeletal Mesh", and materials/textures.
2. Import all other clips pointing to the same Skeleton asset (uncheck Import Mesh).
3. Verify in the Skeletal Mesh editor: bone count, hierarchy, no extra root, scale 1.
4. Mixamo uses a skeleton with a `mixamorig:` prefix. Keep it consistent. Do not mix skeletons of different prefixes in one project without retargeting.
5. Physics Asset: generate and adjust capsules at head, torso, limbs. Hit and ragdoll depend on it.
6. Create sockets at hands, back and head for weapons, VFX and hats.

### Retargeting (recommended path for a shared project skeleton)

Use the **IK Rig** and **IK Retargeter** assets (UE5):
1. Create an IK Rig for the source skeleton (Mixamo) and the target (Mannequin or custom). Define the retarget root (`pelvis`/`Hips`) and chains: spine, head, arms, legs, fingers.
2. Create an IK Retargeter, set source and target rigs, match the retarget pose (A-pose vs T-pose) by editing the target retarget pose until both look alike.
3. Retarget animations in batch (Export Selected Animations). Check foot sliding, arm penetration and finger poses.
4. Tune: adjust chain settings, IK goals for feet, and the Pelvis Motion settings to keep height correct for different proportions.

For a skeleton used only by one character, direct import to its own skeleton is simpler and has less error.

## 5. Verification checklist

- [ ] Idle, walk, run cycles loop without a pop.
- [ ] Feet match speed (no sliding); stride length matches `MaxWalkSpeed`.
- [ ] No hand/arm penetration through the body at the extremes of attacks.
- [ ] Root motion enabled only on clips meant to drive movement.
- [ ] Capsule size and character mesh offset correct (feet on the floor).
- [ ] Sockets in place; weapons attach correctly during attack frames.
- [ ] Ragdoll or hit reaction looks plausible with the Physics Asset.
- [ ] Rig works with the project's AnimBP and BlendSpaces (see `ue-character-movement`).

## 6. Best practices

- Decide the skeleton and animation naming before the first character, so the whole roster shares one pipeline.
- Keep a single reference character to test every new animation and retarget.
- Layer your own animation over the library: add anticipation and follow-through on hits, and blend with additive aim offsets for gameplay.
- Add facial animation separately (morph targets or a face rig). Mixamo bodies do not include face.
- Use Control Rig or Animation Modifiers for repeating fixes (foot lock, root alignment).
- Store the rigged source (`.blend`/FBX), marker screenshots and the download manifest so a re-rig takes minutes.
- If an AI generator offers built-in rigging (Meshy, Tripo), compare its skeleton and weights against Mixamo on the same mesh and use the better one.

## Failure patterns

| Symptom | Cause / fix |
|---------|-------------|
| Rig fails or twisted limbs | Non-humanoid pose, arms touching body, or bad markers: re-pose to T-pose, redo markers |
| Mesh collapses at shoulders or hips | Heavy mesh or bad topology: remesh, add loops, reduce clothing overlap |
| Character floats or sinks | Pivot not at feet, wrong capsule offset, or pelvis height off after retarget |
| Animation 20 to 100 times too big/small | Unit scale mismatch (cm vs m): fix at import or in the DCC, not by scaling the actor |
| Sliding feet | In Place clip speed does not match movement speed: adjust play rate or movement speed |
| Fingers curl or stretch | Different finger counts or retarget chain mismatch: map chains explicitly |
| Animations will not apply | Imported against different skeleton assets: reimport onto the same skeleton or retarget |
