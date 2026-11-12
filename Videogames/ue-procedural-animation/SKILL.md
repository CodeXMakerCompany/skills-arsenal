---
name: ue-procedural-animation
description: Author an AnimSequence from scratch in Unreal Engine 5 when the animation you need does not exist - creating the asset, writing bone tracks, reading a reference pose from a live skeletal mesh component, deriving rotation axes from rig geometry instead of guessing, shaping an easing envelope, and verifying each iteration with a screenshot. Use when a required clip is missing from the assets, when building a punch, wave or gesture from a rig, or when scripting animation data in the editor. On UE 5.8, prefer the Sequencer and animation toolsets; the Python write path below is the fallback, and pose reads that returned empty on 5.2 must be re-checked against the described tools before you trust them.
---

# UE5 Procedural Animation from Python

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Sometimes the clip you need simply is not in the project. You can author one: create an
`AnimSequence`, write bone tracks, and iterate against screenshots. The result will not
match a captured clip, but a readable 0.8 second gesture is very achievable and beats
blocking on an asset that does not exist.

## Before you start

1. **Confirm the clip really is missing.** Parse every FBX in the project for
   `AnimationStack` entries, and remember that an FBX whose only stack is a static bind
   clip imports as a duplicate `SkeletalMesh` and **no** `AnimSequence` at all.
2. **Get the bone names.** `data_model_interface.get_bone_track_names()` on any existing
   clip on the same skeleton.
3. **Budget for iteration.** Expect two or three passes with a screenshot between each.
   Reasoning about quaternion signs is slower and less reliable than looking.

## 1. Prefer the animation tools, and do not trust 5.2 reads

Describe the Sequencer and animation toolsets and use them when they can create the
clip and write bone keys. The Python below is the fallback.

On 5.2 the read side of the Python animation API returned empty against the
sequencer-backed data model. Re-test those calls on 5.8 before trusting them. Until a
call returns real keys, read poses from a live skeletal mesh component and write
through the controller.

| Call | Result on 5.2 |
|------|---------------|
| `AnimationLibrary.get_raw_track_rotation_data` | **empty** |
| `AnimDataModel.get_bone_animation_tracks()` | **empty** |
| `AnimationLibrary.get_bone_poses_for_frame` (plural) | **empty** |
| `AnimationLibrary.get_bone_pose_for_frame` (singular) | **identity transforms** |
| `AnimSequence.get_controller()` | **does not exist** |
| `data_model_interface.get_bone_track_names()` | works |
| `anim.get_editor_property('controller')` | works — this is the write path |
| `SkeletalMeshComponent.get_socket_transform(bone, space)` | works — this is the read path |

So: **read poses from a live component**, write through the controller.

## 2. Read the reference pose from a component

```python
RTS_P = unreal.RelativeTransformSpace.RTS_PARENT_BONE_SPACE
RTS_C = unreal.RelativeTransformSpace.RTS_COMPONENT

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tmp = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 9000))
comp = tmp.skeletal_mesh_component
comp.set_editor_property('skeletal_mesh_asset', mesh)

base = {bone: comp.get_socket_transform(bone, RTS_P) for bone in bones}
```

Parent-bone space is what bone tracks store. Park the probe actor far from anything, and
destroy it as soon as the measurements are taken.

## 3. Derive the rotation axis; do not guess it

Guessing a bone's local rotation axis wastes iterations. Compute it from the geometry.
To swing an arm forward, the axis is perpendicular to both the arm and the facing
direction:

```python
def dir_between(a, b):
    pa = comp.get_socket_transform(a, RTS_C).translation
    pb = comp.get_socket_transform(b, RTS_C).translation
    return norm(unreal.Vector(pb.x - pa.x, pb.y - pa.y, pb.z - pa.z))

forward = unreal.Vector(0.0, 1.0, 0.0)      # the mesh's facing, measured beforehand
punch_axis = norm(cross(dir_between('RightArm', 'RightForeArm'), forward))

# A torso twist is a different axis: vertical, not the swing axis.
right = unreal.Vector(-1.0, 0.0, 0.0)
twist_axis = norm(cross(right, forward))    # comes out (0, 0, -1)
```

Then take each axis into the bone's parent space:

```python
def to_local(bone, axis_component):
    parent = comp.get_parent_bone(bone)
    xf = comp.get_socket_transform(parent, RTS_C) if parent else unreal.Transform()
    return norm(unreal.MathLibrary.inverse_transform_direction(xf, axis_component))
```

**Use a separate axis per body part.** Rotating shoulder and spine on the *same* axis as
the arm does not add weight, it adds lift: a punch becomes a raised-hand wave. The arm
swings on the perpendicular; the torso twists on the vertical.

It also pays to compute the angle rather than tune it blind. The angle between the
resting arm direction and the facing direction is how far the arm must rotate to end up
horizontal and forward — about 92° for a typical A-pose.

## 4. The envelope

```python
def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def envelope(k):
    """wind up -> strike -> hold -> recover, as a signed 0..1."""
    t = k / float(FRAMES)
    if t < 0.25: return -0.30 * smooth(t / 0.25)                  # anticipation
    if t < 0.42: u = (t - 0.25) / 0.17; return -0.30 + 1.30*(u*u) # accelerating strike
    if t < 0.55: return 1.0                                        # impact hold
    return 1.0 * (1.0 - smooth((t - 0.55) / 0.45))                 # recovery
```

Anticipation and a quadratic strike are what separate a gesture from a slide. Linear
interpolation between four poses reads as robotic however good the poses are.

## 5. Write the tracks

```python
fac = unreal.AnimSequenceFactory()
fac.set_editor_property('target_skeleton', skeleton)
anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    'A_Char_Punch', '/Game/Characters', unreal.AnimSequence, fac)

ctrl = anim.get_editor_property('controller')
ctrl.open_bracket('build punch')
ctrl.set_frame_rate(unreal.FrameRate(30, 1))
ctrl.set_number_of_frames(unreal.FrameNumber(FRAMES))     # FrameNumber, not int

ML = unreal.MathLibrary
for bone in bones:
    t = base[bone]
    pos = [t.translation] * (FRAMES + 1)                  # keys = frames + 1
    scale = [t.scale3d] * (FRAMES + 1)
    if bone in PLAN:
        axis, amplitude = PLAN[bone]
        rot = [ML.compose_rotators(
                   t.rotation.rotator(),
                   ML.rotator_from_axis_and_angle(axis, amplitude * envelope(k))
               ).quaternion() for k in range(FRAMES + 1)]
    else:
        rot = [t.rotation] * (FRAMES + 1)
    ctrl.add_bone_curve(bone)
    ctrl.set_bone_track_keys(bone, pos, rot, scale)

ctrl.close_bracket()
unreal.EditorAssetLibrary.save_asset('/Game/Characters/A_Char_Punch')
```

Details that cost a round trip each if missed: `set_number_of_frames` takes a
`FrameNumber` struct and rejects a plain int; key count is frames **+ 1**;
`add_bone_track` is deprecated in favour of `add_bone_curve`; and `compose_rotators(A, B)`
applies A then B, which is what you want for a parent-space delta over a base pose.

Write a track for **every** bone, not only the animated ones, so the clip carries the
whole pose rather than falling back to a reference pose that does not match.

## 6. Verify with a screenshot, every pass

```python
comp.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_SINGLE_NODE)
d = unreal.SingleAnimationPlayData()
d.set_editor_property('anim_to_play', anim)
d.set_editor_property('saved_playing', False)
d.set_editor_property('saved_position', 0.40)      # the impact frame
comp.set_editor_property('animation_data', d)

unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(-330, 1200, 110), unreal.Rotator(roll=0, pitch=-3, yaw=0))
unreal.SystemLibrary.execute_console_command(None, 'HighResShot 1280x720')
```

Place the probe **away from other characters** — overlapping meshes make the frame
unreadable — and frame it side-on, where limb extension is visible. Screenshots land in
`Saved/Screenshots/<Platform>/` a moment later.

## 7. Playing a one-shot without an AnimBP

```cpp
Mesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
Mesh->SetAnimation(Clip);
Mesh->SetPlayRate(Rate);
Mesh->SetPosition(Rate < 0.f ? Clip->GetPlayLength() : 0.f);   // negative plays backwards
Mesh->Play(false);

GetWorldTimerManager().SetTimer(OneShotTimer, this, &AMyChar::EndAction,
                                Clip->GetPlayLength() / FMath::Abs(Rate), false);
```

Guard your locomotion logic with a `bPlayingOneShot` flag so `Tick` does not fight the
one-shot for the mesh.

## 8. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| All pose reads return zero or identity | The Python read API is still empty on this engine | Read from a live component, or use the animation tool that returned real keys |
| `set_number_of_frames` type error | Passing an int | `unreal.FrameNumber(n)` |
| Gesture lifts instead of swinging | One axis shared across arm, shoulder and spine | Separate swing and twist axes |
| Motion is robotic | Linear envelope | Smoothstep plus an accelerating strike |
| Character snaps to T-pose mid-clip | Only some bones have tracks | Write a track for every bone |
| Arm swings the wrong way | Axis sign | Flip it; confirm with a screenshot |
| Screenshot unreadable | Probe spawned on top of another character | Move it well clear |

Related: [[ue-character-import-pipeline]], [[mixamo-auto-rig-mapper]], [[ue-character-movement]].
