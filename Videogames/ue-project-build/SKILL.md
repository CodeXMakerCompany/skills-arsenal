---
name: ue-project-build
description: Build, reload and package an Unreal Engine 5.8 C++ project - Target.cs versions (BuildSettingsVersion.V7, IncludeOrderVersion Unreal5_8), UBT on Linux, macOS and Windows, the preferred MSVC toolchain, Live Coding versus Hot Reload, the trap where a terminal build disables the editor Compile button, and cook/stage/package. Use when a project will not compile, when the editor must restart, when adding the first module, when packaging a build, or when Live Coding seems missing. The file templates for a new module live in ue-cpp-module-bootstrap.
---

# UE 5.8 project build

The module files are created by `ue-cpp-module-bootstrap`. This skill is the loop around them: which versions 5.8 expects, who is allowed to compile while the editor is open, and how a packaged build is produced. Editor content still goes through `unreal-mcp`. Compiling C++ does not.

## Versions

In both `Source/<Project>.Target.cs` and `Source/<Project>Editor.Target.cs`:

```csharp
DefaultBuildSettings = BuildSettingsVersion.V7;            // Latest on 5.8
IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8; // Latest on 5.8
```

`V2` and `Unreal5_2` are leftovers from older projects. UBT warns, and the warning is the migration, not a style nit. Set both targets. A game target left on the old version and an editor target moved forward will disagree about include order.

Read the warning text from the build log of this engine. Do not copy a newer enum from memory if the log names a different one.

## Toolchain

- **Windows.** 5.8 prefers MSVC 14.50 (Visual Studio 2026, toolset v145). A message that 14.38 is not the preferred version is the compiler install, not the gameplay code. Install the preferred toolset side by side. Do not retarget the project to an older compiler to silence it.
- **Linux.** Use the clang the engine ships. `Engine/Build/BatchFiles/Linux/Build.sh`.
- **macOS.** Use the Xcode version the build log asks for.

Generate project files after the `.uproject` gains a module (`GenerateProjectFiles.sh` on Linux, the right-click menu on Windows). Then build the **editor** target, not the game target, if the next step is opening the editor.

```bash
# Linux, from the engine root, editor target
./Engine/Build/BatchFiles/Linux/Build.sh <Project>Editor Linux Development \
  -project="<abs>/MyGame.uproject" -waitmutex
```

```bat
Engine\Build\BatchFiles\Build.bat <Project>Editor Win64 Development -project="<abs>\MyGame.uproject" -waitmutex
```

`-waitmutex` matters when the editor or another build already holds the UBT mutex. Without it the second build fails in a way that looks like a code error.

## What forces a restart

| Change | Live Coding (Windows) | Hot Reload (Linux, macOS) | Full restart |
|--------|----------------------|---------------------------|--------------|
| Function body | Yes | Often | No |
| New `UFUNCTION` / `UPROPERTY` / `UCLASS` | No | Unsafe | Yes |
| New module, new plugin | No | No | Yes, after the first successful build |
| `.Build.cs` dependency | No | No | Yes |
| Header layout the old instances were built with | No | Corrupts | Yes |

Live Coding on 5.8 is still Windows. It lives under the Windows developer module. Linux and macOS do not have it. Do not promise a Live Coding button on Linux.

Hot Reload is the editor **Compile** button. It loads a second copy of the module and patches references. It copes with function bodies and falls over on new reflected types, changed class layout and constructor changes. After a bad reload, restart. Do not keep compiling on top of a half-patched `UClass`.

### Terminal builds and the Compile button

These two workflows do not mix in one session:

| Workflow | Who builds | Output | Restart |
|----------|------------|--------|---------|
| Terminal `Build.sh` / `Build.bat` | UBT overwrites the base library | base `.so` / `.dll` | Always, if the editor was open |
| Editor Compile | UBT, hot-reload naming | suffixed library | Only if hot reload fails |

If you build from the terminal while the editor is open, the editor keeps the old library mapped and the file on disk is already current. The next Compile sees nothing to do, builds nothing, and never reloads. The button looks broken. Pick one workflow and say which.

Close the editor for the first build of a brand new module. The editor cannot load a module it did not have at startup.

A new reflected symbol also needs a restart even on Windows. Live Coding updates an existing function body. It does not register a new `UFUNCTION`.

## MCP and a second editor

`unreal-mcp` binds to `127.0.0.1:8000` by default and has no authentication. One editor owns that port.

- Do not launch a second editor for a commandlet on the same port.
- Commandlets do not auto-start MCP. Pass `-ModelContextProtocolStartServer` only when that commandlet is the editor an agent should drive, and give it `-ModelContextProtocolPort=` so it does not collide.
- Packaging does not need MCP. Close the agent session or leave the editor alone. Do not cook from a Python loop.

## Package

Cook and stage with RunUAT `BuildCookRun`. Confirm flags against `RunUAT.sh BuildCookRun -help` on the installed engine before inventing a switch.

The shape that matches 5.8:

- `-project=` absolute `.uproject`
- `-platform=` `Win64`, `Linux`, or `Mac`
- `-clientconfig=Development` while you are testing, `Shipping` for a release candidate
- `-build -cook -stage -pak -archive`
- IoStore is on for UE5 cooks. Leave it on unless the log says this project disabled it.

Development still has logs and checks. Shipping strips them unless the target set `bUseLoggingInShipping` / `bUseChecksInShipping`. Do not "fix" a missing log in Shipping by cooking Development and renaming the folder.

A Blueprint-only project packages without a game module. The moment `Source/` exists, the package build compiles that module. A target still on `Unreal5_2` fails here even if the editor was opened by regenerating project files earlier.

## Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Include-order or build-settings warning | Target still on `V2` / `Unreal5_2` | `V7` and `Unreal5_8` in both targets |
| MSVC 14.38 is not preferred | VS 2022 toolset | Install the 14.50 toolset the log names |
| New class missing in the picker | Module built, editor not restarted | Restart, then `load_class` the `/Script/` path |
| Compile button does nothing | Terminal build already updated the base library | Restart, then use only one build path |
| Editor dies after Hot Reload | New `UCLASS` or layout change | Restart. Do not hot-reload that change |
| Second editor cannot start MCP | Port 8000 taken | One editor, or an explicit other port |
| Cook fails on a missing module | Editor target was built, game target was not | `BuildCookRun -build`, or build the game target first |

Related: `ue-cpp-module-bootstrap`, `ue-indie-game-setup`.
