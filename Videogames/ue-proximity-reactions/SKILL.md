---
name: ue-proximity-reactions
description: Make actors react to how close the player is in Unreal Engine 5 - distance-driven material glow with a dynamic material instance, authoring the parameterised material from Python, smooth interpolation instead of a hard threshold, and the three performance habits that keep it cheap across dozens of actors - caching the pawn in a weak pointer, writing a material parameter only when it changed, and choosing distance checks over overlap spheres. Use when pickups should highlight near the player, when enemies should telegraph awareness, or for any per-actor reaction driven by distance.
---

# UE5 Proximity Reactions

"Light up when the player is near" is a distance check, a material parameter and a lerp.
Done carelessly across thirty actors it is also thirty actor lookups and thirty render
thread writes per frame, which is why the habits below matter more than the effect.

## Before you start

1. **The engine's default materials have no usable parameters.** `BasicShapeMaterial` and
   friends cannot be driven at runtime. Author your own (section 1) or nothing will change.
2. **Decide distance check or overlap volume.** A sphere component with overlap events is
   binary and event-driven; a distance check gives you a continuous 0..1 you can lerp. For
   a glow that fades, you want the distance.
3. **Decide where the reaction lives.** Per-actor state belongs on the actor; a global
   "nearest pickup" belongs in a subsystem.

## 1. Author the material from Python

```python
import unreal
MEL = unreal.MaterialEditingLibrary

mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    'M_Reward', '/Game/Gameplay', unreal.Material, unreal.MaterialFactoryNew())

def expr(cls, x, y):
    return MEL.create_material_expression(mat, cls, x, y)

tint = expr(unreal.MaterialExpressionVectorParameter, -900, -300)
tint.set_editor_property('parameter_name', 'Tint')
tint.set_editor_property('default_value', unreal.LinearColor(0.07, 0.07, 0.08, 1.0))

gold = expr(unreal.MaterialExpressionVectorParameter, -900, -100)
gold.set_editor_property('parameter_name', 'GlowColor')
gold.set_editor_property('default_value', unreal.LinearColor(1.0, 0.76, 0.24, 1.0))

glow = expr(unreal.MaterialExpressionScalarParameter, -900, 100)
glow.set_editor_property('parameter_name', 'Glow')
glow.set_editor_property('default_value', 0.0)

strength = expr(unreal.MaterialExpressionScalarParameter, -900, 220)
strength.set_editor_property('parameter_name', 'GlowStrength')
strength.set_editor_property('default_value', 6.0)

# base colour lerps dull -> gold
lerp = expr(unreal.MaterialExpressionLinearInterpolate, -500, -200)
MEL.connect_material_expressions(tint, '', lerp, 'A')
MEL.connect_material_expressions(gold, '', lerp, 'B')
MEL.connect_material_expressions(glow, '', lerp, 'Alpha')

# emissive = GlowColor * Glow * GlowStrength
m1 = expr(unreal.MaterialExpressionMultiply, -500, 60)
MEL.connect_material_expressions(gold, '', m1, 'A')
MEL.connect_material_expressions(glow, '', m1, 'B')
m2 = expr(unreal.MaterialExpressionMultiply, -300, 60)
MEL.connect_material_expressions(m1, '', m2, 'A')
MEL.connect_material_expressions(strength, '', m2, 'B')

MEL.connect_material_property(lerp, '', unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(m2,   '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset('/Game/Gameplay/M_Reward')
```

Driving **both** base colour and emissive from one scalar is what sells it: the object
changes colour *and* throws light, rather than just getting brighter. Verify with
`MEL.get_scalar_parameter_names(mat)` — a typo in a parameter name fails silently at
runtime.

Unlike Blueprint graphs, material graphs **are** fully scriptable; `MaterialEditingLibrary`
exposes node creation and pin connection.

## 2. One dynamic instance per actor

```cpp
void AWanderingCube::BeginPlay()
{
    Super::BeginPlay();
    GlowMaterial = MeshComp->CreateAndSetMaterialInstanceDynamic(0);
    Player = UGameplayStatics::GetPlayerPawn(this, 0);
}
```

The instance must be per actor — the whole point is that each one glows by its own
distance. Hold it in a `UPROPERTY(Transient)` or it is garbage collected.

## 3. The update

```cpp
void AWanderingCube::UpdateGlow(float DeltaSeconds)
{
    if (!GlowMaterial)
    {
        return;
    }

    // The pawn is respawned on PIE restart, so re-acquire a stale cache.
    if (!Player.IsValid())
    {
        Player = UGameplayStatics::GetPlayerPawn(this, 0);
        if (!Player.IsValid())
        {
            return;
        }
    }

    const float Distance = FVector::Dist(GetActorLocation(), Player->GetActorLocation());
    const float Target = 1.0f - FMath::Clamp(Distance / FMath::Max(1.0f, ProximityRadius), 0.0f, 1.0f);

    const float Previous = Glow;
    Glow = FMath::FInterpTo(Glow, Target, DeltaSeconds, GlowInterpSpeed);

    // Pushing a parameter touches the render thread: only do it when it changed.
    if (FMath::Abs(Glow - Previous) > KINDA_SMALL_NUMBER)
    {
        GlowMaterial->SetScalarParameterValue(GlowParam, Glow);
    }
}
```

## 4. The three performance habits

These are the difference between "nice touch" and "why did the frame rate drop".

**Cache the pawn in a `TWeakObjectPtr`.** `GetPlayerPawn` is a lookup; thirty actors
calling it every frame is thirty lookups for a value that changes once per respawn. Weak,
not strong, so the actor does not keep a dead pawn alive, and re-acquire when it goes
invalid.

**Only write the parameter when it changed.** `SetScalarParameterValue` queues work for
the render thread. An actor sitting still at full distance should cost a subtraction and
a comparison, not a render command.

**Store parameter names as static `FName`s.** Constructing an `FName` from a literal every
frame hashes the string every frame:

```cpp
static const FName GlowParam(TEXT("Glow"));
```

Beyond roughly a hundred reacting actors, stop ticking each one: have a subsystem iterate
them on a timer at 10 Hz and interpolate locally, or move the whole effect into the
material using the player position from a Material Parameter Collection and spend zero
game-thread time.

## 5. The MPC alternative

For a large number of actors sharing one reaction, write the player position into a
Material Parameter Collection once per frame and compute the distance in the material.
One game-thread write total, and no per-actor tick:

```cpp
UKismetMaterialLibrary::SetVectorParameterValue(
    this, PlayerMPC, TEXT("PlayerPosition"), FLinearColor(Loc.X, Loc.Y, Loc.Z, 0.f));
```

The trade is that the material can no longer react differently per actor unless you also
feed per-instance data, so prefer the per-actor DMI until the count forces your hand.

## 6. Interpolation, not a threshold

`FInterpTo` toward a continuous target is what makes this read as a reaction rather than
a switch. A bare `if (Distance < Radius) Glow = 1;` pops, and pops worst exactly when the
player strafes along the boundary. Interp speed 6 is a good start: fast enough to feel
responsive, slow enough to hide the edge.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Nothing changes | Engine default material has no parameters | Author a parameterised material |
| All actors glow together | Shared material instead of per-actor DMI | `CreateAndSetMaterialInstanceDynamic` per actor |
| Glow stops after a PIE restart | Cached pawn went stale | Re-acquire when the weak pointer is invalid |
| Glow pops on and off | Hard threshold | `FInterpTo` toward a 0..1 target |
| Frame time drops with many actors | Per-frame lookups and parameter writes | Cache the pawn, write only on change |
| Parameter silently ignored | Name mismatch | Verify with `get_scalar_parameter_names` |
| Emissive barely visible | No HDR headroom | Multiply by a `GlowStrength` above 1 |

Related: [[ue-actor-spawner]], [[ue-material-instance-builder]], [[ue-timers-and-triggers]].
