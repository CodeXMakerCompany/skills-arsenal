---
name: ue-niagara-audio-trigger
description: Event-driven VFX (Niagara) and audio (MetaSound, Sound Cue) orchestration for Unreal Engine 5. Use when triggering impact effects, hit feedback, card or ability visuals, UI feedback, ambient soundscapes, or any gameplay "juice" from C++ or Blueprint, including pooling, parameter driving, concurrency, scalability and dedicated-server handling.
---

# UE5 Niagara VFX & Audio Orchestration

Gameplay code should say *what happened* ("hit", "card played"); a single FX layer decides *which* Niagara system and sound to play and *how*. This keeps gameplay free of asset references and makes effects tunable by designers and artists.

## Before you start

1. Check the engine version. Some signatures differ (e.g. `PlaySoundAtLocation` initial parameters, Niagara pooling enums, MetaSound parameter APIs). Read the headers for the installed version.
2. Add module dependencies in `YourModule.Build.cs`: `"Niagara"`, `"AudioMixer"` (and `"MetasoundEngine"` only if you reference MetaSound C++ types directly).
3. Decide who triggers FX: server-authoritative events should replicate a lightweight event (tag + location), and clients play the FX. Never replicate spawned FX actors or components.

## Architecture

```
Gameplay event (hit, play card, pickup)
        |  FGameplayTag + location/target + optional magnitude
        v
JuiceSubsystem (per world)  ---->  FX definition lookup (Data Asset / Data Table)
        |                                   |
        |                         Niagara system + Sound + parameters + limits
        v
Spawn pooled Niagara + sound (skipped on dedicated server)
```

Rules:
- Gameplay passes a **tag** (e.g. `FX.Impact.Metal`) and context, not asset pointers.
- Assets live in a data asset or table, loaded by soft reference where the set is large.
- One entry point (the subsystem). No ad hoc `SpawnSystemAtLocation` calls scattered in gameplay classes.

## 1. Data definition

```cpp
// Public/Juice/JuiceTypes.h
#pragma once
#include "CoreMinimal.h"
#include "GameplayTagContainer.h"
#include "Engine/DataAsset.h"
#include "JuiceTypes.generated.h"

class UNiagaraSystem;
class USoundBase;
class USoundAttenuation;
class USoundConcurrency;

USTRUCT(BlueprintType)
struct FJuiceCue
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TSoftObjectPtr<UNiagaraSystem> Niagara;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TSoftObjectPtr<USoundBase> Sound;   // MetaSound Source or Sound Cue

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TObjectPtr<USoundAttenuation> Attenuation = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TObjectPtr<USoundConcurrency> Concurrency = nullptr;  // limits overlapping instances

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float VolumeMultiplier = 1.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FVector2D PitchRange = FVector2D(1.f, 1.f);   // random pitch per play for variety
};

UCLASS(BlueprintType)
class YOURMODULE_API UJuiceCueSet : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ForceInlineRow))
    TMap<FGameplayTag, FJuiceCue> Cues;
};
```

## 2. Subsystem

```cpp
// Public/Juice/JuiceSubsystem.h
#pragma once
#include "CoreMinimal.h"
#include "GameplayTagContainer.h"
#include "Subsystems/WorldSubsystem.h"
#include "JuiceSubsystem.generated.h"

class UJuiceCueSet;
class UNiagaraComponent;
class UAudioComponent;

UCLASS()
class YOURMODULE_API UJuiceSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;

    /** Play the cue registered for Tag at a world location. */
    UFUNCTION(BlueprintCallable, Category = "Juice")
    void PlayCueAtLocation(FGameplayTag Tag, FVector Location,
                           FRotator Rotation = FRotator::ZeroRotator,
                           float Intensity = 1.f);

    /** Play the cue attached to a component (follows moving targets). */
    UFUNCTION(BlueprintCallable, Category = "Juice")
    void PlayCueAttached(FGameplayTag Tag, USceneComponent* AttachTo,
                         FName Socket = NAME_None, float Intensity = 1.f);

    UPROPERTY(EditDefaultsOnly, Category = "Juice")
    TObjectPtr<UJuiceCueSet> CueSet;
};
```

```cpp
// Private/Juice/JuiceSubsystem.cpp
#include "Juice/JuiceSubsystem.h"
#include "Juice/JuiceTypes.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Components/AudioComponent.h"

bool UJuiceSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
    // No visuals or audio needed on a dedicated server.
    return !IsRunningDedicatedServer() && Super::ShouldCreateSubsystem(Outer);
}

void UJuiceSubsystem::PlayCueAtLocation(FGameplayTag Tag, FVector Location,
                                        FRotator Rotation, float Intensity)
{
    const FJuiceCue* Cue = CueSet ? CueSet->Cues.Find(Tag) : nullptr;
    if (!Cue) { return; }   // missing cue is not a gameplay error; log in dev builds

    if (UNiagaraSystem* Fx = Cue->Niagara.LoadSynchronous())
    {
        UNiagaraComponent* Comp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
            GetWorld(), Fx, Location, Rotation, FVector::OneVector,
            /*bAutoDestroy*/ true, /*bAutoActivate*/ true,
            ENCPoolMethod::AutoRelease, /*bPreCullCheck*/ true);

        if (Comp) { Comp->SetVariableFloat(TEXT("User.Intensity"), Intensity); }
    }

    if (USoundBase* Snd = Cue->Sound.LoadSynchronous())
    {
        const float Pitch = FMath::RandRange(Cue->PitchRange.X, Cue->PitchRange.Y);
        UGameplayStatics::PlaySoundAtLocation(
            GetWorld(), Snd, Location, Rotation,
            Cue->VolumeMultiplier * Intensity, Pitch, /*StartTime*/ 0.f,
            Cue->Attenuation, Cue->Concurrency);
    }
}
```

Notes:
- `LoadSynchronous` on a hot path can hitch. Preload cue assets at level start (async via `UAssetManager` / `FStreamableManager`) and keep the handle alive, or use hard references for a small always-used set.
- Parameter name `User.Intensity` must exist as an exposed User parameter in the Niagara system.

## 3. Driving Niagara parameters

Expose parameters in the system as `User.*` variables, then set them on the returned component. Prefer the typed setters.

```cpp
NiagaraComp->SetVariableLinearColor(TEXT("User.Tint"), Color);
NiagaraComp->SetVariableFloat(TEXT("User.Scale"), 1.5f);
NiagaraComp->SetVariableVec3(TEXT("User.Direction"), HitNormal);
NiagaraComp->SetVariableBool(TEXT("User.bCritical"), true);
```

- Set parameters right after spawn and before the first simulation tick, ideally with `bAutoActivate = false` then `Activate(true)` when you must set many values.
- For data-driven spawns (many particles from game data), use Niagara Data Interfaces (array, skeletal mesh, render target) instead of per-particle component calls.
- Do not set parameters every frame from many actors; drive from a single owner or use a Niagara parameter collection for global values.

## 4. Audio

- `PlaySoundAtLocation` is fire-and-forget. Use `SpawnSoundAtLocation` / `SpawnSoundAttached` when you need the `UAudioComponent` to stop, fade, or change parameters later.
- MetaSound parameters go through the audio component:

```cpp
UAudioComponent* Audio = UGameplayStatics::SpawnSoundAtLocation(
    this, MetaSoundSource, Location, Rotation, 1.f, 1.f, 0.f,
    Attenuation, Concurrency, /*bAutoDestroy*/ true);

if (Audio)
{
    Audio->SetFloatParameter(TEXT("Intensity"), 0.8f);
    Audio->SetTriggerParameter(TEXT("OnHit"));
}
```

- Names must match the MetaSound graph inputs exactly (and trigger inputs for `SetTriggerParameter`).
- Use a **Sound Concurrency** asset for any repeatable sound (max count, resolution rule such as stop-quietest or stop-oldest) so swarms do not exhaust voices.
- Use **Sound Attenuation** for 3D falloff; UI and 2D feedback use `PlaySound2D` or `SpawnSound2D`.
- Vary pitch and volume slightly, or use a Random node in the Sound Cue / MetaSound, to avoid machine-gun repetition.
- Route sounds to Sound Classes / Submixes (SFX, UI, Ambience) so players can balance them.
- Long ambient layers: spawn once, fade in/out (`FadeIn`, `FadeOut`) and drive with parameters. Do not respawn per event.

## 5. Pooling and lifetime

| Case | Approach |
|------|----------|
| One-shot Niagara effects | `bAutoDestroy = true` and `ENCPoolMethod::AutoRelease` (built-in pool, component returns to pool on finish) |
| Looping Niagara effect you own | Spawn once, `Deactivate()` when done, then destroy or release explicitly |
| High-frequency impacts (bullets, swarms) | Pooling on, short-lived systems, cap per-frame spawns, use a Niagara Effect Type with culling and max instances |
| Attached effects on a destroyed actor | Detach and let the effect finish (`SetAutoDestroy(true)`, `Deactivate()`), otherwise it vanishes mid-play |
| One-shot audio | `PlaySoundAtLocation`, rely on concurrency limits |
| Looping audio | `UAudioComponent` with `bAutoDestroy = false` if reusing, else stop and destroy when done |

Never leave inactive but non-destroyed components on actors; they still cost memory and registration.

## 6. Networking and platform

- Server decides gameplay; clients render FX. Send a tag and location via a multicast or a replicated state change, not FX objects.
- Skip FX on dedicated servers (`IsRunningDedicatedServer()` or `NM_DedicatedServer`).
- For client-predicted actions, play FX locally on the instigator immediately and suppress the duplicate from the server for that client.
- Scalability: assign Niagara **Effect Types** (cull distance, max instances, significance), honor `fx.*` quality cvars, and test on the lowest target platform.

## 7. Blueprint usage

- Expose `PlayCueAtLocation` / `PlayCueAttached` as the only calls designers need.
- Anim Notifies: use a custom notify that calls the subsystem by tag instead of direct `Play Niagara` notifies, so cues stay data-driven.
- Keep Blueprint FX graphs thin; no per-tick spawning.

## 8. Common failures

| Symptom | Likely cause |
|---------|--------------|
| Effects pile up invisibly, memory grows | `bAutoDestroy` false or looping system never deactivated |
| Hitches on first impact | Synchronous asset load on first use; preload and keep handle |
| Sound cuts out in busy scenes | No concurrency asset; voices stolen by priority |
| Same sound feels robotic | No pitch/volume variation or random layers |
| Parameter has no effect | `User.` namespace or name mismatch; parameter not exposed in the system |
| FX play on dedicated server or twice on listen host | Missing server guard, or both predicted and replicated paths fire |
| Effect left behind when actor dies | Component destroyed with the actor; detach and let it finish |
| Audio too loud/quiet across the game | No sound class / submix mix; normalize assets and set class volumes |

## 9. Verify

- Build the editor target with no new warnings.
- PIE: trigger the same cue 100 times quickly; check `stat niagara`, `stat audio`, and `au.Debug.Sounds 1` for instance counts.
- Confirm a missing tag does nothing and does not crash.
- Test as a client and on a listen server to confirm FX play once.
- Profile on target hardware for the heaviest scene before shipping.
