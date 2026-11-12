---
name: ue-canvas-hud
description: Build an Unreal Engine 5 HUD and simple menus in C++ with AHUD and Canvas - score counters, health bars with centred labels, circular countdown rings, and a title screen with a clickable PLAY button via hit boxes. Covers resolution-independent scaling, measuring text instead of eyeballing offsets, caching actor lookups out of DrawHUD, and wiring a menu level and its game mode by config. Use when adding on-screen counters, bars, timers or a start screen, or when UMG is more machinery than the job needs. On UE 5.8, build real menus through the widget toolset; use Canvas when the HUD must stay in C++ and draw every frame without widget assets.
---

# UE5 Canvas HUD and Menus

## Working in the UE 5.8 editor

On 5.8 the editor is an MCP server, `unreal-mcp` at `http://127.0.0.1:8000/mcp`, when the Unreal MCP and All Toolsets plugins are enabled. Change the editor through those tools.

1. Spawn, import, materials, Blueprints, widgets and levels go through `unreal-mcp`. If that server is not connected, stop before mutating the editor and say so. Writing the runtime code in this skill does not require it. Do not move those editor mutations to remote Python when a toolset can do them.
2. `list_toolsets`, then `describe_toolsets` with schemas, then `call_tool`. Names change between builds. Never call a tool you have not just described.
3. Save the level and dirty assets before a bulk edit and again after. An error result means the edit did not happen.
4. Stop PIE first. Tool calls run one at a time on the game thread.
5. Editor Python is the fallback for an operation no described tool covers. Keep world and actor references inside the function, never in a module global.
6. Python samples in this skill specify the operation. Translate them into the toolset you just described, and run the Python only when no tool covers it.


`AHUD::DrawHUD` gives you an immediate-mode canvas: draw rectangles, text and lines every
frame, with no widget assets. That is the right tool for counters, bars, timers and a
one-button title screen that has to stay in C++.

On 5.8, menus with text input, lists, layout or designer styling belong to UMG, and the
widget toolset can build those graphs. Do not drop to Canvas because a widget graph
"cannot be scripted".

## Before you start

1. **Register the HUD class** on the game mode: `HUDClass = AMyHUD::StaticClass();`
   Nothing draws without it and there is no warning.
2. **Decide where state lives.** The HUD reads; it does not own. Counters belong to the
   pawn, timers to the spawner, lives to the character.
3. **Pick a reference resolution.** Everything below scales from 1080p.

## 1. Scale and a text helper

```cpp
void AMyHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !GEngine) return;

    const APunkGirlCharacter* Player = Cast<APunkGirlCharacter>(GetOwningPawn());
    if (!Player) return;

    UFont* Big = GEngine->GetLargeFont();
    if (!Big) return;

    const float S = FMath::Max(0.75f, Canvas->SizeY / 1080.0f);
    const float X = Margin.X * S;
    float Y = Margin.Y * S;

    auto DrawLabel = [&](const FString& Text, float PosX, float PosY,
                         float Scale, const FLinearColor& Color)
    {
        FCanvasTextItem Item(FVector2D(PosX, PosY), FText::FromString(Text), Big, Color);
        Item.Scale = FVector2D(Scale, Scale);
        Item.EnableShadow(FLinearColor(0, 0, 0, 0.75f));
        Canvas->DrawItem(Item);
    };
```

Every offset multiplied by `S` is what keeps the layout intact at 720p and 4K. A HUD laid
out in raw pixels is correct on exactly one monitor.

The shadow is not decoration: white text on a bright sky is unreadable without it.

## 2. Counter and a bar with a centred label

```cpp
    DrawLabel(FString::Printf(TEXT("CUBOS  %d"), Player->GetCubesCollected()),
              X, Y, 1.7f * S, FLinearColor::White);
    Y += 46.0f * S;

    const float BarW = BarSize.X * S;
    const float BarH = BarSize.Y * S;
    const float Fill = FMath::Clamp(float(Player->GetLives()) / Player->GetMaxLives(), 0.f, 1.f);

    DrawRect(FLinearColor(0, 0, 0, 0.55f), X - 2, Y - 2, BarW + 4, BarH + 4);   // outline
    DrawRect(FLinearColor(0.12f, 0.12f, 0.12f, 0.85f), X, Y, BarW, BarH);       // track
    if (Fill > 0.f)
    {
        DrawRect(BarColor, X, Y, BarW * Fill, BarH);                             // fill
    }

    // Centre the label by measuring it, not by guessing an offset.
    const FString LifeText = FString::Printf(TEXT("x%d"), Player->GetLives());
    float TW = 0.f, TH = 0.f;
    Canvas->TextSize(Big, LifeText, TW, TH);
    DrawLabel(LifeText,
              X + (BarW - TW * S) * 0.5f,
              Y + (BarH - TH * S) * 0.5f, S, FLinearColor::White);
```

`Canvas->TextSize` is the difference between a label that stays centred as the number
grows from `x6` to `x12` and one that drifts. Measure, never eyeball.

Drive the fill from real variables even when nothing changes it yet. A hard-coded `x6`
has to be rewritten the day damage exists.

## 3. A circular countdown

```cpp
void AMyHUD::DrawCountdownRing(float CX, float CY, float Radius,
                               float Thickness, float Fraction)
{
    constexpr int32 Segments = 40;
    const FLinearColor Track(0.05f, 0.05f, 0.07f, 0.65f);

    auto PointAt = [&](float T)
    {
        const float Angle = -PI * 0.5f + T * 2.0f * PI;   // start at twelve o'clock
        return FVector2D(CX + FMath::Cos(Angle) * Radius, CY + FMath::Sin(Angle) * Radius);
    };

    const int32 Filled = FMath::RoundToInt(Fraction * Segments);
    for (int32 i = 0; i < Segments; ++i)
    {
        const FVector2D A = PointAt(float(i) / Segments);
        const FVector2D B = PointAt(float(i + 1) / Segments);
        const bool bOn = i < Filled;
        DrawLine(A.X, A.Y, B.X, B.Y, bOn ? RingColor : Track,
                 bOn ? Thickness : Thickness * 0.6f);
    }
}
```

Forty chords is smooth at HUD sizes and costs far less than a material-driven radial
widget. The `-PI/2` offset starts the arc at the top, which is what a countdown is
expected to do.

## 4. Cache lookups out of DrawHUD

`DrawHUD` runs every frame. An actor search in it is a per-frame scene iteration:

```cpp
if (!bGeneratorSearched)
{
    bGeneratorSearched = true;
    for (TActorIterator<ARandomRewardsGenerator> It(GetWorld()); It; ++It)
    {
        Generator = *It;      // TWeakObjectPtr member
        break;
    }
}
```

Weak, so a destroyed generator does not keep the HUD pointing at a dead actor. The same
rule applies to any `GetAllActorsOfClass` you are tempted to put in a draw call.

## 5. A clickable title screen

`AHUD` has hit boxes, so a menu needs no widgets:

```cpp
void AMenuHUD::BeginPlay()
{
    Super::BeginPlay();
    if (APlayerController* PC = GetOwningPlayerController())
    {
        PC->bShowMouseCursor = true;
        PC->bEnableClickEvents = true;
        PC->bEnableMouseOverEvents = true;
        PC->SetInputMode(FInputModeGameAndUI().SetHideCursorDuringCapture(false));
    }
}
```

Without those four lines the button draws and never responds.

```cpp
// In DrawHUD, after working out BX/BY/BW/BH:
    AddHitBox(FVector2D(BX, BY), FVector2D(BW, BH), PlayBoxName, /*bConsumesInput=*/true);

void AMenuHUD::NotifyHitBoxClick(FName BoxName)
{
    Super::NotifyHitBoxClick(BoxName);
    if (BoxName == PlayBoxName)
    {
        UGameplayStatics::OpenLevel(this, LevelToPlay);
    }
}
```

Hit boxes are re-registered every frame; that is how `AHUD` expects it, not a leak.

For hover, read the mouse directly and compute it **before** drawing the button, or the
highlight lags a frame:

```cpp
float MouseX = -1.f, MouseY = -1.f;
if (APlayerController* PC = GetOwningPlayerController())
{
    PC->GetMousePosition(MouseX, MouseY);
}
bHovered = MouseX >= BX && MouseX <= BX + BW && MouseY >= BY && MouseY <= BY + BH;
```

Draw a full-screen translucent rect first so the text reads over whatever the level shows.

## 6. Wiring the menu level by config

```ini
[/Script/EngineSettings.GameMapsSettings]
EditorStartupMap=/Game/Maps/L_Main.L_Main     ; devs keep opening the gameplay level
GameDefaultMap=/Game/Maps/L_Menu.L_Menu       ; the game boots into the menu
GlobalDefaultGameMode=/Script/my_game.PunkGirlGameMode
+GameModeMapPrefixes=(Name="L_Menu",GameMode="/Script/my_game.MenuGameMode")
```

`GameModeMapPrefixes` matches by **prefix**, so use the full map name. A prefix of `L_M`
would also capture `L_Main` and boot the gameplay level with the menu on top.

## 7. Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Nothing draws | `HUDClass` not set on the game mode | Set it |
| Layout correct on one monitor only | Offsets in raw pixels | Multiply everything by `Canvas->SizeY / 1080` |
| Centred label drifts as the number grows | Hard-coded offset | `Canvas->TextSize` |
| Text unreadable over bright scenery | No shadow | `Item.EnableShadow` |
| Menu button does nothing | Cursor and click events not enabled | Set them in `BeginPlay` |
| Hover highlight one frame late | Hover computed after drawing | Compute first |
| Frame time drops with the HUD on | Actor search inside `DrawHUD` | Cache in a weak pointer |
| Both menu and gameplay use the menu game mode | `GameModeMapPrefixes` prefix too short | Use the full map name |

Related: [[ue-actor-spawner]], [[ue-timers-and-triggers]], [[ue-cpp-module-bootstrap]].
