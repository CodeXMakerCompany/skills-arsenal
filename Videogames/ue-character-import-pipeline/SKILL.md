---
name: ue-character-import-pipeline
description: Import a rigged character FBX into Unreal Engine 5 correctly and prove it worked - choosing between several candidate files by inspecting their skeletons rather than their names, scripted AssetImportTask settings, the save trap that leaves a SkeletalMesh on disk without its Skeleton, scale and axis conversion, measuring which way the mesh faces instead of guessing, and a clean asset naming pass with reference fixup. Use when importing a character, when a skeletal mesh imports broken or sideways, when a character walks backwards, or when deciding which of several exported FBX files to use. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Character Import Pipeline

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Importing a character is three jobs: pick the right source file, import it with settings
that survive contact with a real rig, and verify the result instead of assuming. Most
character import bugs are decided before the import runs, by picking the wrong file.

## Before you start

1. **Close nothing, but know where the editor is.** Importing into a running editor is
   fine and preferable; importing headless while the editor is open desynchronises the
   content browser from disk.
2. **Expect the exporter's naming.** Meshy, Mixamo, Character Creator and friends emit
   60-character filenames. Plan a rename pass (section 6) from the start.
3. **Never pick the source file by its name.** Inspect it (section 1).

## 1. Choose the file by inspecting its skeleton

Given several exports of "the same" character, the differences that matter are invisible
in the filename. Parse the FBX and compare:

| Signal | What it means |
|--------|---------------|
| `LimbNode` count | Bone count. **Zero bones means a static mesh**, not a character, whatever it is called |
| `Deformer` of type `Skin` | The mesh is actually bound to the skeleton |
| `AnimationStack` names | Which clips are inside, if any |
| `Content` node under `Video` | Textures are **embedded**; no missing-texture hunt after import |
| Bone names | `Hips`, `LeftUpLeg`, `LeftToeBase`… is the Mixamo convention and retargets cleanly |

A worked example of the decision: of three exports, a 51 MB "character" file had **0
bones and no skin deformer** — a prop, useless as a character — while a 19 MB file had 24
bones, a skin deformer and a real `walking_man` clip. The small file was the right one.

FBX binary stores node names in plain text but compresses array payloads, so `strings`
alone under-reports. Parse the record tree, or import a candidate into a scratch folder
and inspect it in the editor before committing.

## 2. Import settings that matter

```python
import unreal

def options(skeleton=None):
    o = unreal.FbxImportUI()
    o.set_editor_property('import_mesh', True)
    o.set_editor_property('import_as_skeletal', True)
    o.set_editor_property('import_animations', True)
    o.set_editor_property('import_materials', True)
    o.set_editor_property('import_textures', True)
    o.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    if skeleton:
        o.set_editor_property('skeleton', skeleton)   # reuse, do not create a second one

    sk = o.skeletal_mesh_import_data
    sk.set_editor_property('convert_scene', True)         # Y-up source -> Z-up UE
    sk.set_editor_property('use_t0_as_ref_pose', False)   # ref pose = bind pose
    sk.set_editor_property('import_morph_targets', True)

    an = o.anim_sequence_import_data
    an.set_editor_property('convert_scene', True)
    an.set_editor_property('remove_redundant_keys', True)
    return o
```

Two of these decide whether the result is usable:

- **`convert_scene`** handles the axis conversion. Most DCC and AI generators export Y-up;
  UE is Z-up. With it on, a 170 cm character imports at 170 units and needs no rescale.
- **`use_t0_as_ref_pose = False`**. When the FBX carries both mesh and animation, `True`
  makes frame 0 of that animation the reference pose. For a walk cycle that means the bind
  pose is a mid-stride pose, and every retarget afterwards is subtly wrong.

## 3. The save trap

```python
task = unreal.AssetImportTask()
task.set_editor_property('filename', FBX)
task.set_editor_property('destination_path', '/Game/Characters/MyChar')
task.set_editor_property('automated', True)
task.set_editor_property('replace_existing', True)
task.set_editor_property('save', False)          # <- deliberately False
task.set_editor_property('options', options())
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

# Save everything the import produced, not just the imported object.
unreal.EditorAssetLibrary.save_directory(
    '/Game/Characters/MyChar', only_if_is_dirty=False, recursive=True)
```

`task.save = True` saves the **imported object** and not its dependencies. A skeletal mesh
import produces seven assets — mesh, skeleton, physics asset, material, textures — and
with `save = True` you can end up with a 47 MB `SkeletalMesh` on disk whose `Skeleton`
was never written. The asset registry reports all seven because they exist in memory; the
breakage only appears after a restart.

Always verify against the filesystem, not the registry:

```bash
ls Content/Characters/MyChar/*.uasset | wc -l
```

## 4. Verify the import

```python
sk = unreal.EditorAssetLibrary.load_asset(f'{D}/SK_MyChar')
print('skeleton:', sk.get_editor_property('skeleton'))          # None means broken
b = sk.get_bounds().box_extent
print('height:', b.z * 2, 'uu')                                 # ~170 for a human
print('materials:', [m.get_editor_property('material_interface') for m
                     in sk.get_editor_property('materials')])
```

A humanoid should land between 150 and 220 units. Far smaller or larger means
`convert_scene` was off or the source unit is wrong — fix the import, do not scale the
actor, or every animation and physics asset downstream inherits the error.

## 5. Which way does the mesh face?

Guessing this costs an hour. Measure it from the rig instead. In component space, read the
hip bones:

```python
comp = actor.skeletal_mesh_component
xf = comp.get_world_transform()
for bone in ('LeftUpLeg', 'RightUpLeg'):
    local = xf.inverse_transform_location(comp.get_socket_location(bone))
    print(bone, local)
```

The hips separate along the character's **lateral** axis, and in UE `+Y` is the
character's right.

| Measurement | Mesh faces | Mesh component yaw |
|-------------|-----------|--------------------|
| `LeftUpLeg.y < RightUpLeg.y` | `+X` | `0` |
| `LeftUpLeg.x > RightUpLeg.x` | `+Y` | `-90` (the UE mannequin convention) |
| `LeftUpLeg.x < RightUpLeg.x` | `-Y` | `+90` |

Reading this off a screenshot is unreliable — a braid or a ponytail reads as "behind" and
flips your conclusion by 180°, which presents as the character walking backwards while
still moving forwards. Measure, then confirm with a screenshot; do not substitute one for
the other.

## 6. Rename with reference fixup

A 58-character generated name is unusable in a `FObjectFinder` path or a details panel.
`rename_asset` fixes up references, so do it immediately after import and before anything
else points at the assets:

```python
PLAN = [
    (f'{BASE}',              'SK_MyChar'),
    (f'{BASE}_Skeleton',     'SK_MyChar_Skeleton'),
    (f'{BASE}_Anim',         'A_MyChar_Walk'),
    (f'{BASE}_PhysicsAsset', 'PHYS_MyChar'),
    ('Material_1',           'M_MyChar'),
    ('texture_0',            'T_MyChar_BC'),
]
for old, new in PLAN:
    unreal.EditorAssetLibrary.rename_asset(f'{D}/{old}', f'{D}/{new}')
unreal.EditorAssetLibrary.save_directory(D, only_if_is_dirty=False, recursive=True)
```

Then re-check that the mesh still points at its skeleton and the animation at the same
one. A rename that silently drops a reference looks fine until play.

## 7. Importing animation onto an existing skeleton

Set `skeleton` in the options and `mesh_type_to_import` to `FBXIT_ANIMATION`, with
`import_mesh = False`. Be warned that an FBX whose only `AnimationStack` is a static bind
clip produces **no** `AnimSequence` at all — the import appears to succeed and silently
delivers a duplicate `SkeletalMesh` and physics asset instead. Check what class actually
appeared before assuming you gained an animation.

## 8. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| One `.uasset` on disk, seven in the registry | `task.save = True` | `save_directory(..., only_if_is_dirty=False, recursive=True)` |
| Character 100× too large or small | `convert_scene` off, or source units wrong | Fix the import, never the actor scale |
| Walks backwards | Mesh component yaw 180° off | Measure the hips (section 5) |
| Bind pose is a mid-stride pose | `use_t0_as_ref_pose = True` on an animated FBX | Set it False and reimport |
| Grey or pink materials | Textures referenced by absolute path from the exporter's temp dir | Prefer FBX with embedded `Content`; otherwise import textures separately |
| A second skeleton appears | `skeleton` not set when importing more clips | Set it to the existing one |
| New assets invisible in the editor | Imported headless while the editor was open | Import through the running editor, or restart it |

Related: [[mixamo-auto-rig-mapper]], [[ue-character-movement]], [[ue-third-person-camera]],
[[ue-procedural-animation]].
