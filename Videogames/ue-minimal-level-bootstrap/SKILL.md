---
name: ue-minimal-level-bootstrap
description: Create a minimal, cheap, ready-to-play Unreal Engine 5 level - floor, sun, SkyLight, atmosphere, height fog, a reflection capture and a PlayerStart - and make it the project's default map. Use when replacing a heavyweight template level, starting a jam project, needing a clean test or greybox level, or when asked for a minimal or blank level setup. On UE 5.8, create and save that level through Unreal MCP level tools with the editor open. The pythonscript commandlet is only the fallback if those tools fail.
---

# UE5 Minimal Level Bootstrap

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


A small level with exactly the actors a playable scene needs and nothing else. Eight
actors, no landscape, no streaming, no volumetric clouds. It opens instantly and it is the
right starting point for a jam or a greybox.

The whole point of this skill is the *how*: generating a level by script has two traps
that will cost you a crashed editor and a silently empty log if you meet them cold.

## Before you start

1. **Save whatever level is currently open.** A level named `Untitled_*` lives in `/Temp`
   and has never touched disk. Creating a new level discards it permanently.

   ```python
   w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
   print(w.get_path_name())      # /Temp/Untitled_1.Untitled_1  -> unsaved
   unreal.EditorLoadingAndSavingUtils.save_map(w, '/Game/Maps/L_OpenWorld')
   ```

2. **Keep the editor open.** Create, open and save the map with the level toolset. The
   actor list below is the content of that level.
3. **Decide the playspace size.** The floor below is 40 × 40 m (a 100 unit `Plane` scaled
   40×). Scale it to the game, not to the template.

## 1. Create the level in the open editor

The eight actors are the level. Spawn them through the actor toolset after the level
toolset has created and opened the map.

On 5.2, creating or loading a level from Python remote execution crashed the editor with
`World Memory Leaks` inside `CheckForWorldGCLeaks`. A map change from inside the ticker
is reentrant, and a `UWorld` left in a Python module global keeps the old world alive
until the editor asserts. That is why this skill used to demand a commandlet.

On 5.8 that is the fallback, not the path:

- Do not hold worlds, levels or actors in module globals.
- Do not create or load a level from remote Python while a level tool exists.
- If the tools fail and you must use the `pythonscript` commandlet, close the editor
  first. Its prints go to `Saved/Logs`, not stdout. `new_level` creates and opens in one
  call. Splitting that into `create_asset` then `load_level` was the leak.

## 2. The build script

```python
import unreal

def log(*a): unreal.log('[L_MAIN] ' + ' '.join(str(x) for x in a))

RUTA = '/Game/Maps/L_Main'

def limpiar():
    eal = unreal.EditorAssetLibrary
    if eal.does_asset_exist(RUTA):
        log('exists, deleting to regenerate')
        eal.delete_asset(RUTA)

def crear():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    log('new_level ->', les.new_level(RUTA))

def poblar():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    eal = unreal.EditorAssetLibrary
    V, R = unreal.Vector, unreal.Rotator

    def spawn(cls, loc, rot=None, label=None):
        a = eas.spawn_actor_from_class(cls, loc, rot or R(0.0, 0.0, 0.0))
        if label: a.set_actor_label(label)
        log('  +', label)
        return a

    # floor: 100-unit Plane scaled to 40 x 40 m, static so it can be baked
    f = spawn(unreal.StaticMeshActor, V(0,0,0), label='Floor')
    f.static_mesh_component.set_static_mesh(eal.load_asset('/Engine/BasicShapes/Plane'))
    f.set_actor_scale3d(V(40.0, 40.0, 1.0))
    f.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)

    # sun: movable so no bake is required to see something
    s = spawn(unreal.DirectionalLight, V(0,0,1000),
              R(roll=0.0, pitch=-42.0, yaw=-35.0), label='Sun')
    s.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    s.light_component.set_editor_property('intensity', 4.0)
    s.light_component.set_editor_property('dynamic_shadow_cascades', 3)

    spawn(unreal.SkyAtmosphere, V(0,0,0), label='SkyAtmosphere')

    # SkyLight without real-time capture: ambient light for free
    k = spawn(unreal.SkyLight, V(0,0,500), label='SkyLight')
    k.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    k.light_component.set_editor_property('real_time_capture', False)

    spawn(unreal.ExponentialHeightFog, V(0,0,0), label='HeightFog')

    # reflection capture by hand: the intended workflow with Lumen off
    r = spawn(unreal.SphereReflectionCapture, V(0,0,400), label='ReflectionCapture')
    r.capture_component.set_editor_property('influence_radius', 3000.0)

    c = spawn(unreal.StaticMeshActor, V(0,0,100), label='Cube_Ref')
    c.static_mesh_component.set_static_mesh(eal.load_asset('/Engine/BasicShapes/Cube'))

    spawn(unreal.PlayerStart, V(-600,0,200),
          R(roll=0.0, pitch=-10.0, yaw=0.0), label='PlayerStart')

def guardar():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    log('save_current_level ->', les.save_current_level())

limpiar(); crear(); poblar(); guardar(); log('DONE')
```

`unreal.Rotator` takes `(roll, pitch, yaw)` — not the pitch-first order the editor's
details panel shows. Pass them as keywords, as above, and the ambiguity disappears.

## 3. Run it

```bash
UE=<engine>/Engine/Binaries/Linux/UnrealEditor-Cmd
"$UE" "<project>/<name>.uproject" \
  -run=pythonscript -script="/abs/path/build_main.py" \
  -unattended -nosplash -nopause
```

On Windows the binary is `UnrealEditor-Cmd.exe` under `Engine\Binaries\Win64`.

## 4. Read the output from the project log, not stdout

**The commandlet does not send Python output to stdout or stderr.** Neither `print()` nor
`unreal.log()` appear in the pipe, even while the log line says `Python script executed
successfully`. They go to the project log:

```bash
grep -ah "\[L_MAIN\]" "<project>/Saved/Logs/<Name>.log" | sed 's/^.*LogPython: //' | awk '!seen[$0]++'
```

A run that prints nothing to your terminal may have worked perfectly. Confirm against the
artifact, not against the pipe:

```bash
ls -la "<project>/Content/Maps/"*.umap
```

If you need to know whether a script executed at all, have it write a witness file — that
is the one signal that cannot be swallowed by log routing.

## 5. Verify the saved level

Load it in a second headless pass and list what is actually in the asset. This catches a
level that saved empty, which the build run cannot tell you.

```python
import unreal
def log(*a): unreal.log('[VERIFY] ' + ' '.join(str(x) for x in a))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/L_Main')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = eas.get_all_level_actors()
log('actors:', len(acts))
for a in acts:
    extra = ''
    if isinstance(a, unreal.StaticMeshActor):
        sm = a.static_mesh_component.static_mesh
        extra = f' mesh={sm.get_name() if sm else None} scale={a.get_actor_scale3d()}'
    log('  -', a.get_class().get_name(), '|', a.get_actor_label(), extra)
```

Expected: 8 actors — `Floor`, `Sun`, `SkyAtmosphere`, `SkyLight`, `HeightFog`,
`ReflectionCapture`, `Cube_Ref`, `PlayerStart`.

## 6. Make it the default map

```ini
[/Script/EngineSettings.GameMapsSettings]
EditorStartupMap=/Game/Maps/L_Main.L_Main
GameDefaultMap=/Game/Maps/L_Main.L_Main
```

`EditorStartupMap` is the one people forget, and without it the editor keeps reopening the
old heavy level while everyone wonders why nothing got faster.

## 7. What each actor is for, and what it costs

| Actor | Why it is here | Cost |
|-------|----------------|------|
| `Floor` (StaticMeshActor, Plane) | Something to stand on; `STATIC` so it can be baked later | Negligible |
| `Sun` (DirectionalLight, Movable) | Directional light and shadows with no bake step | CSM shadows, 3 cascades |
| `SkyAtmosphere` | Physically based sky and horizon | Moderate, worth it |
| `SkyLight` (real-time capture off) | Ambient fill, which matters a lot with Lumen off | Near zero once captured |
| `HeightFog` | Depth and atmosphere | Near zero with volumetric fog off |
| `ReflectionCapture` (Sphere, r=3000) | Reflections without Lumen | One-time capture |
| `Cube_Ref` | Scale and lighting reference while greyboxing | Negligible |
| `PlayerStart` | Makes the level playable with Play In Editor | None |

Deliberately absent: `VolumetricCloud` (raymarched per pixel, the single most expensive
actor in the default sky setup), any landscape, and any World Partition. Set the render
settings to match with the companion skill `ue-indie-game-setup`.

## 8. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Editor dies on `new_level` / `load_level` with "World Memory Leaks" | Level change ran from remote Python, or a stale global holds the old world | Use the level toolset instead. If you already fell back to Python, keep every world reference inside a function |
| Script "executed successfully" but prints nothing | Commandlet Python output goes to the project log, not stdout | `grep` the log; check the artifact on disk |
| "Old world ... not cleaned up by garbage collection while loading new map" | Holding the object returned by `create_asset` across a `load_level` | Use `new_level`, which creates and opens in one call |
| `Failed to find property 'volumetric_fog'` | The per-component property name differs by engine version | Set `r.VolumetricFog=0` project-wide; probe names with `[a for a in dir(comp) if 'volum' in a.lower()]` |
| Unsaved template level vanished | A level transition discarded `/Temp/Untitled_*` | `save_map` to a real path *before* creating anything |
| Light rotated wrongly | `unreal.Rotator` is `(roll, pitch, yaw)` | Pass pitch and yaw as keyword arguments |
