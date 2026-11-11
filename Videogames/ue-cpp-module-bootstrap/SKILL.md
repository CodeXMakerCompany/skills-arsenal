---
name: ue-cpp-module-bootstrap
description: Turn a Blueprint-only Unreal Engine 5 project into a C++ project and keep the build loop sane - the exact Target/Build/module files, the uproject entry, building from the command line on Linux, macOS and Windows, and the reality of what forces an editor restart. Covers why Live Coding does not exist on Linux, when Hot Reload copes and when it corrupts, and the trap where terminal builds silently disable the editor's Compile button. Use when adding C++ to a Blueprint project, when a new class does not appear in the editor, when the editor must be restarted repeatedly, or when gameplay logic cannot be authored because Blueprint graphs are not scriptable.
---

# UE5 C++ Module Bootstrap

A Blueprint-only project has no `Source/` directory. The moment you need logic that
cannot be authored from a script — and Blueprint event graphs **cannot** be authored
from Python, there is no node-creation API — you need a C++ module. This is the whole
setup, plus the build loop that follows it.

## Before you start

1. **Confirm the project really is Blueprint-only**: no `Source/` directory, and no
   `Modules` array in the `.uproject`.
2. **Close the editor** for the very first build. There is nothing to overwrite yet, so
   a build with the editor open is harmless, but the editor cannot load a module it did
   not have at startup, so you restart either way.
3. **Pick the module name**: it must be a valid C++ identifier and should match the
   project name. The API macro is derived from it in upper snake case.

## 1. The five files

For a project called `my_game`, create:

```
Source/
  my_game.Target.cs
  my_gameEditor.Target.cs
  my_game/
    my_game.Build.cs
    my_game.h
    my_game.cpp
```

`Source/my_game.Target.cs`:

```csharp
using UnrealBuildTool;
using System.Collections.Generic;

public class my_gameTarget : TargetRules
{
	public my_gameTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V2;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_2;
		ExtraModuleNames.Add("my_game");
	}
}
```

`Source/my_gameEditor.Target.cs` is identical except `Type = TargetType.Editor;` and the
class name `my_gameEditorTarget`.

`Source/my_game/my_game.Build.cs`:

```csharp
using UnrealBuildTool;

public class my_game : ModuleRules
{
	public my_game(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput"
		});
	}
}
```

`my_game.h` is just `#pragma once` plus `#include "CoreMinimal.h"`. `my_game.cpp` carries
the module implementation, and the third argument must match the module name exactly:

```cpp
#include "my_game.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, my_game, "my_game");
```

## 2. Register the module in the .uproject

Insert a `Modules` array. Order in the file does not matter, but keep it before
`Plugins` for readability:

```json
"Modules": [
    { "Name": "my_game", "Type": "Runtime", "LoadingPhase": "Default" }
],
```

Edit it as JSON, not with a regex. A malformed `.uproject` fails to open with a message
that does not mention JSON.

## 3. Build from the command line

The engine ships its own toolchain, so a missing system `clang` means nothing.

```bash
# Linux
<Engine>/Engine/Build/BatchFiles/Linux/Build.sh my_gameEditor Linux Development \
  -project="/abs/path/my_game.uproject" -waitmutex

# macOS
<Engine>/Engine/Build/BatchFiles/Mac/Build.sh my_gameEditor Mac Development \
  -project="/abs/path/my_game.uproject" -waitmutex

# Windows
<Engine>\Engine\Build\BatchFiles\Build.bat my_gameEditor Win64 Development ^
  -project="C:\path\my_game.uproject" -waitmutex
```

The first build of a small module takes seconds, not minutes, when the engine's shared
PCH is already cached. Check `Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/` to confirm
the bundled clang exists before blaming the toolchain for anything.

Success produces:

```
Binaries/Linux/libUnrealEditor-my_game.so
Binaries/Linux/UnrealEditor.modules
```

`UnrealEditor.modules` is the manifest the editor reads at startup to find your module.

## 4. What forces a restart, and what does not

This is the part that wastes the most time, so be precise about it with whoever is
driving the editor.

| Change | Restart needed? |
|--------|-----------------|
| Assets, levels, actor placement, config | **No** |
| Blueprint edits | **No** |
| C++ function bodies | Only if you built from the terminal (see below) |
| New `UCLASS`, new `UPROPERTY`, constructor changes | **Yes** |
| A module that has never been loaded | **Yes** |

The underlying reasons are two, and both are real:

- **The OS**: your module is a shared library already mapped into the editor process. A
  loaded `.so` / `.dll` cannot be swapped in place.
- **The reflection system**: `UClass` objects and their CDOs are built when the module
  loads. Every live `UObject` points at that `UClass` and its vtable. Replacing the code
  underneath leaves them pointing at something else.

## 5. Live Coding and Hot Reload, honestly

**Live Coding is Windows only.** It lives under `Engine/Source/Developer/Windows/LiveCoding`
and `.../LiveCodingServer`. There is no Linux implementation; do not promise it.

**Hot Reload exists on Linux and macOS.** `Engine/Binaries/<Platform>/libUnrealEditor-HotReload.so`
ships with the engine and `bAutomaticallyHotReloadNewClasses=True` is the default. It is
the **Compile** button in the editor toolbar: it builds a library with a fresh suffixed
name, loads it alongside the old one and re-points objects at the new classes. It does
not replace code; it duplicates modules and patches references. That is why it copes with
function-body edits and falls over on new `UCLASS`es, changed class layout and
constructor changes.

### The trap: terminal builds disable the Compile button

These two workflows do not mix:

| Workflow | Who builds | Output | Restart |
|----------|-----------|--------|---------|
| Terminal `Build.sh` | UBT, overwrites the base library | base `.so` | **Always** |
| Editor **Compile** button | UBT, hot-reload naming | suffixed `.so` | Only if hot reload fails |

If you build from the terminal while the editor is open, the editor keeps the old library
in memory and the base file on disk is now current. Press **Compile** afterwards and UBT
reports everything up to date, builds nothing, and therefore never performs the reload —
so the button appears broken. Pick one workflow per session and say which you are using.

## 6. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Editor offers to rebuild on every launch | `UnrealEditor.modules` BuildId does not match the engine | Rebuild against the same engine version |
| New class never appears in the Content Browser or class picker | Module was built but the editor has not restarted | Restart; confirm with `unreal.load_class(None, '/Script/my_game.MyClass')` |
| `GlobalDefaultGameMode` silently ignored, you spawn as a flying `DefaultPawn` | The `/Script/my_game....` path cannot resolve because the module is not loaded | Restart the editor; the fallback is silent, which is what makes it confusing |
| `error: declaration shadows a field` | UE builds with `-Wshadow -Werror` | Rename the local; it is usually a sign the local deserves a better name anyway |
| `SetTimer` will not compile with your handler | Timer handlers must be `void()` | Add a thin `void` wrapper that calls the real function |
| Link fails with the editor open | The target library is loaded | Close the editor; only the *first* build of a brand new module is safe with it open |

## 7. What C++ unlocks that scripting cannot

Worth knowing before you decide to add a module at all. Python in the editor can create
assets, place actors, import meshes, author materials and even author `AnimSequence` bone
tracks. It **cannot** create Blueprint graph nodes or connect pins: `BlueprintEditorLibrary`
exposes `add_function_graph` and `find_graph`, but there is no node-creation API. Anything
that needs runtime logic — input bindings, timers, collision responses, HUD drawing — is
therefore C++ or hand-authored Blueprint, with no third option.

Related: [[ue-enhanced-input-cpp]], [[ue-canvas-hud]], [[ue-actor-spawner]].
