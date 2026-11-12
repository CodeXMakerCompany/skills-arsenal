---
name: ue-material-instance-builder
description: Patterns for creating and driving material instances in Unreal Engine 5 from C++, Blueprint and Editor automation. Use when applying generated or per-item textures, rarity glows, dissolve or hover effects, character skins or team colors to meshes, and when choosing between Dynamic Material Instances, Material Instance Constants, Custom Primitive Data and Material Parameter Collections. On UE 5.8, change the editor through Unreal MCP toolsets instead of remote Python.
---

# UE5 Material Instance Builder

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


Build one flexible master material, expose a small set of well-named parameters, and drive them from code or editor automation. The key decision is *which kind of instance* each use case needs, because it decides cost and what can be changed.

## Before you start

1. Check the engine version and whether the project uses Interchange or legacy import (affects the texture import script).
2. Read the master material: list its parameter names, types, defaults and groups. Do not guess names; a wrong name silently does nothing.
3. Decide which values are fixed per asset (editor time) and which change at runtime (gameplay time).

## 1. Choosing the right tool

| Need | Use | Why |
|------|-----|-----|
| Fixed per-asset values (skins, rarities, variants) authored in the editor | **Material Instance Constant (MIC)** asset | No runtime cost, can use static switches, batches better |
| Values that change at runtime on one object | **Material Instance Dynamic (MID)** | Scalar/vector/texture parameters can change per frame |
| Many instances of the same mesh with different per-instance values | **Custom Primitive Data** (`SetCustomPrimitiveDataFloat`) | No per-object material, keeps batching/instancing, cheap |
| Global values (time of day, wetness, global glow) | **Material Parameter Collection (MPC)** | One update drives all materials that read it |
| Static features on/off (rarity frame variants, emissive on/off) | **Static Switch** in a MIC | Compiles out unused paths; cannot change at runtime on a MID |

Rule of thumb: start with MICs, drop to MIDs only for runtime changes, use Custom Primitive Data when you would otherwise create dozens or hundreds of MIDs.

## 2. Master material conventions

Keep a stable parameter contract so code and artists stay in sync.

| Parameter | Type | Range / notes |
|-----------|------|---------------|
| `BaseColorMap` | Texture2D | sRGB on |
| `NormalMap` | Texture2D | Normal compression, sRGB off |
| `RoughnessMap` (or packed `ORMMap`) | Texture2D | sRGB off; prefer packing Occlusion/Roughness/Metallic into one |
| `RarityGlowColor` | Vector | Linear color, HDR allowed |
| `StarRarityTier` | Scalar | 1 to 5 (cast to int in the material with floor) |
| `DissolveAmount` | Scalar | 0 to 1 |
| `HoverAmount` | Scalar | 0 to 1 |
| `Tint` | Vector | Multiplies base color |

- Group parameters (`Textures`, `Rarity`, `FX`) and set sensible defaults, so an unset parameter produces a valid look.
- Give every texture parameter a default texture (not none) so instances never render black or pink.
- Names are case sensitive. Put them in a shared header as constants:

```cpp
// Public/Materials/MaterialParamNames.h
#pragma once
#include "UObject/NameTypes.h"

namespace MatParam
{
    inline const FName BaseColorMap(TEXT("BaseColorMap"));
    inline const FName NormalMap(TEXT("NormalMap"));
    inline const FName RoughnessMap(TEXT("RoughnessMap"));
    inline const FName RarityGlowColor(TEXT("RarityGlowColor"));
    inline const FName StarRarityTier(TEXT("StarRarityTier"));
    inline const FName DissolveAmount(TEXT("DissolveAmount"));
}
```

## 3. Runtime: Dynamic Material Instance (C++)

Create once, cache in a `UPROPERTY`, update many times.

```cpp
// CardVisualComponent.h
UCLASS(ClassGroup=(Cards), meta=(BlueprintSpawnableComponent))
class YOURMODULE_API UCardVisualComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    void ApplyCardLook(UStaticMeshComponent* Mesh, UMaterialInterface* Parent,
                       UTexture2D* Art, const FLinearColor& RarityColor, float RarityTier);

    void SetDissolve(float Amount);
    void SetHover(float Amount);

private:
    // UPROPERTY keeps the MID alive across garbage collection
    UPROPERTY(Transient)
    TObjectPtr<UMaterialInstanceDynamic> CardMID;
};
```

```cpp
// CardVisualComponent.cpp
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialParamNames.h"

void UCardVisualComponent::ApplyCardLook(UStaticMeshComponent* Mesh, UMaterialInterface* Parent,
                                         UTexture2D* Art, const FLinearColor& RarityColor,
                                         float RarityTier)
{
    if (!Mesh || !Parent) { return; }

    // Create the MID once; reuse it on later calls
    if (!CardMID || CardMID->Parent != Parent)
    {
        CardMID = UMaterialInstanceDynamic::Create(Parent, this);
        Mesh->SetMaterial(0, CardMID);
    }

    if (Art)
    {
        CardMID->SetTextureParameterValue(MatParam::BaseColorMap, Art);
    }
    CardMID->SetVectorParameterValue(MatParam::RarityGlowColor, RarityColor);
    CardMID->SetScalarParameterValue(MatParam::StarRarityTier, FMath::Clamp(RarityTier, 1.f, 5.f));
}

void UCardVisualComponent::SetDissolve(float Amount)
{
    if (CardMID) { CardMID->SetScalarParameterValue(MatParam::DissolveAmount, FMath::Clamp(Amount, 0.f, 1.f)); }
}
```

Notes:
- Equivalent shortcut: `Mesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, Parent)`.
- Pass `this` (a long-lived object) as the outer when you cache the MID; do not use a transient outer that dies earlier.
- Skeletal and static mesh components both support this; for multi-slot meshes create one MID per slot you modify.
- To animate (hover, dissolve), drive the scalar from a Timeline, curve or `FMath::FInterpTo` in Tick, or better from a Material function using `Time`/a curve when no gameplay input is needed.
- Avoid `SetXParameterValue` on every frame for hundreds of objects. Update only when the value changes (compare with the last value) or move the animation into the shader.
- Do not create a new MID each time a card is drawn; recycle the MID when the actor is pooled.

### Custom Primitive Data (many objects, no MIDs)

Material side: use the `Custom Primitive Data` node (float index 0 for dissolve, 1 to 3 for tint, etc.). Code side:

```cpp
Mesh->SetCustomPrimitiveDataFloat(0, DissolveAmount);          // index 0
Mesh->SetCustomPrimitiveDataVector3(1, FVector(R, G, B));      // indices 1..3
```

Many instanced actors share one material and still look different.

### Material Parameter Collection (global)

```cpp
UMaterialParameterCollectionInstance* Inst =
    GetWorld()->GetParameterCollectionInstance(GlobalFXCollection);
Inst->SetScalarParameterValue(TEXT("GlobalGlowIntensity"), 1.5f);
```

## 4. Editor automation: create MICs from generated textures

Use this when AI-generated card art or skins arrive in bulk. Create the instances through the material toolset (`describe_toolsets` first). The Python below is the operation when no tool covers instance creation:

```python
import unreal

TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary

def import_texture(src_png: str, dest_dir: str, srgb: bool, normal: bool = False):
    task = unreal.AssetImportTask()
    task.filename = src_png
    task.destination_path = dest_dir
    task.automated = True
    task.save = True
    task.replace_existing = True
    TOOLS.import_asset_tasks([task])
    tex = task.get_objects()[0]   # the imported Texture2D
    tex.set_editor_property("srgb", srgb)
    if normal:
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    return tex

def make_card_instance(name: str, parent_path: str, art: unreal.Texture2D,
                       glow: unreal.LinearColor, tier: float, out_dir="/Game/Cards/MI"):
    factory = unreal.MaterialInstanceConstantFactoryNew()
    mi = TOOLS.create_asset(f"MI_{name}", out_dir, unreal.MaterialInstanceConstant, factory)
    parent = unreal.EditorAssetLibrary.load_asset(parent_path)
    MEL.set_material_instance_parent(mi, parent)
    MEL.set_material_instance_texture_parameter_value(mi, "BaseColorMap", art)
    MEL.set_material_instance_vector_parameter_value(mi, "RarityGlowColor", glow)
    MEL.set_material_instance_scalar_parameter_value(mi, "StarRarityTier", tier)
    MEL.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    return mi
```

Notes:
- This is an outline: confirm function and property names in the Python API of the installed engine version (`dir(unreal.MaterialEditingLibrary)`), and test on one asset before running in bulk.
- Drive the batch from a manifest (name, texture path, rarity). Idempotent: re-running updates existing assets instead of duplicating.
- Texture import rules: BaseColor sRGB on; Normal `TC_NORMALMAP`, sRGB off; Roughness/Metallic/ORM `TC_MASKS`, sRGB off; power-of-two sizes for mipmaps and streaming; correct Texture Group (`World`, `Character`, `UI`).
- Place assets by convention: `/Game/Cards/Art/T_<Name>_BC`, `/Game/Cards/MI/MI_<Name>`.
- Blueprint alternative: an Editor Utility Widget/Blueprint with the same nodes (`Set Material Instance Scalar Parameter Value` from the Material Editing Library).

## 5. Best practices for good looking, cheap materials

- **One master per family** (cards, characters, props). Branch via static switches in MICs instead of many masters.
- **Keep instruction count low:** check Material Stats; avoid large texture counts per material (aim for under 16 samplers on mobile, fewer is better).
- **Pack textures:** ORM in one texture, emissive in alpha or a mask, to cut samples.
- **Feature switches:** `Use Normal`, `Use Emissive`, `Use Dissolve` as static switches; most cards need none of the costly features.
- **Rarity look:** drive frame, glow, foil shimmer from `StarRarityTier` in the shader (lerp/select by tier) instead of separate materials per rarity. Add a subtle fresnel/rim glow and animated shimmer (panning noise, `Time`) scaled by the tier.
- **Dissolve:** use a noise texture with `DissolveAmount` as threshold, a bright emissive edge via `smoothstep` around the threshold, and `Opacity Mask`/Masked blend mode. Use dithered opacity for cheaper translucency.
- **Hover/selection:** add emissive boost, slight fresnel and optional parallax from a single `HoverAmount` scalar. Smooth the value in code with `FInterpTo`.
- **Team/skin colors:** use a mask texture to select which regions take `Tint`, keeping details from the base color.
- **Flipbooks and masks:** see `sprite-sheet-packer` for animated foil/VFX textures.
- **Streaming:** keep texture groups right and use Virtual Textures only where large (landscapes, huge atlases); small cards stream normally.
- **Nanite/Lumen:** check that the master material works with the project's pipeline (Nanite supports masked with caveats, check engine version; world-position-offset limitations).
- **Pooling:** when actors are pooled, reset all parameters (dissolve 0, hover 0, tint default) on reuse.
- **Testing:** view in Lit, Unlit, and Detail Lighting modes, at multiple distances, in dark and bright lighting. Verify on the lowest quality scalability level.
- **Naming and ownership:** parameter names are an API; version them carefully and never rename without updating code and instances.

## 6. Common failures

| Symptom | Likely cause |
|---------|--------------|
| Parameter change does nothing | Name typo or case mismatch, parameter missing from the parent, or instance of the wrong material |
| Material turns black or default grid | Missing default texture, parent not set, or shader still compiling |
| MID disappears or crashes after a while | Not stored in a `UPROPERTY`, garbage collected |
| Hundreds of draw calls from cards | One MID per object; use Custom Primitive Data or shared MICs |
| Static switch has no effect at runtime | Static switches only work on MICs authored in editor, not on MIDs |
| Texture looks washed out/dark | sRGB wrong for the texture type |
| Normal map looks inverted | Flip green channel on import (DirectX vs OpenGL) |
| Dissolve edge looks flat | No emissive edge band; add HDR emissive with smoothstep |
| Spikes when drawing cards | Creating MIDs/loading textures synchronously at draw time; preload and pool |
