---
name: sprite-sheet-packer
description: Packing animation frames into sprite sheets, flipbooks and texture atlases for games and VFX. Use when building particle flipbooks (SubUV), animated UI icons, 2D character animation sheets or atlases with metadata, and when choosing between uniform grid flipbooks and trimmed atlases for Unreal, Unity, Godot or web engines.
---

# Sprite Sheet & Flipbook Packer

Two different products get called "sprite sheet". Pick the right one first:

| Type | Layout | Metadata | Used for |
|------|--------|----------|----------|
| **Flipbook / SubUV grid** | Uniform cells, fixed columns x rows, no trimming or rotation | Just grid size and frame count | Particles, shader-driven animation (Niagara SubUV, Unity Shader Graph flipbook, Godot AnimatedSprite via region) |
| **Atlas (trimmed)** | Frames cropped and packed tightly, optional rotation | JSON/XML with frame rects, offsets, pivots | 2D characters, UI icons, sprite renderers, Paper2D, Phaser, Unity Sprite Atlas |

Mixing them up is the most common mistake: a trimmed, rotated atlas cannot drive a SubUV material, and a uniform grid wastes space for sprites.

## Before you start

1. Identify engine, renderer (sprite component, Niagara sprite, UI) and animation driver (material, sprite animator, engine tool).
2. Gather frames in order: consistent size, consistent registration (same pivot), transparent background, numbered `frame_0001.png`.
3. Decide frame count and cell size from the on-screen size (a VFX that is 200 px on screen does not need 512 px cells).
4. Decide the alpha model: straight vs premultiplied, additive (black background, no alpha) vs alpha-blended.

## 1. Source frame preparation

- Render or export all frames at the same canvas size. Do not crop per frame for a flipbook.
- AI-generated frames: generate a consistent seed/style, then clean. Check jitter, background halos and drifting centers. Align frames to a common pivot before packing (auto-align on the subject's center or contact point).
- Remove background cleanly (alpha matte or key). Check edge halos on a dark and light background.
- Additive VFX: render on black, no alpha needed, saves memory (RGB). Alpha-blended VFX (smoke): RGBA with premultiplied or straight alpha, be consistent.
- For smooth looping effects: make the first and last frames match or crossfade.
- Frame rate: 12 to 24 fps source is typical for VFX; use fewer frames and let the engine interpolate (SubUV blending) rather than packing 60 frames.

## 2. Layout rules

- **Power of two for the whole sheet:** 512, 1024, 2048 or 4096 per side. Square is simplest; rectangular POT (e.g. 2048x1024) works in modern engines.
- **Uniform cells for flipbooks:** e.g. 8x8 grid of 256x256 = 2048x2048 with 64 frames. Pick columns x rows to match the frame count; leave unused cells empty at the end.
- **Padding:** leave transparent (or edge-extruded) padding between cells. With mipmaps, bleeding grows with each mip level, so 2 px padding is a minimum for 1 to 2 mip levels. For long mip chains or filtered sampling use 4 to 8 px, or disable mips on the flipbook.
- **Border extrusion** (duplicating edge pixels into padding) avoids dark fringes on atlas sprites with alpha.
- **Budget:** 4096x4096 RGBA is 64 MB uncompressed (about 16 MB with BC3/DXT5 compression). Prefer 2048 or lower plus fewer, larger cells over huge sheets, especially on mobile.

## 3. Building the sheet

### Uniform flipbook (ImageMagick)

```bash
# 8 columns x 8 rows, 256x256 cells, no gaps -> exactly 2048x2048 (POT)
montage frames/frame_*.png \
  -tile 8x8 -geometry 256x256+0+0 -background none \
  flipbook_8x8.png
```

Do not add `+N+N` gaps to `-geometry`: that makes the sheet 2064 px wide, which is not POT. Keep padding inside each cell instead (leave a transparent border in every frame). Always check the output dimensions:

```bash
identify flipbook_8x8.png
```

Python (Pillow) when you need exact control:

```python
from PIL import Image
import glob

COLS, ROWS, CELL = 8, 8, 256
frames = sorted(glob.glob("frames/frame_*.png"))
sheet = Image.new("RGBA", (COLS * CELL, ROWS * CELL), (0, 0, 0, 0))

for i, path in enumerate(frames[: COLS * ROWS]):
    im = Image.open(path).convert("RGBA").resize((CELL, CELL), Image.LANCZOS)
    sheet.paste(im, ((i % COLS) * CELL, (i // COLS) * CELL))

sheet.save("flipbook_8x8.png")
print(f"{len(frames)} frames -> {COLS}x{ROWS}, {sheet.size}")
```

### Trimmed atlas (TexturePacker CLI)

```bash
TexturePacker \
  --format <data-format> \
  --data atlas.json \
  --sheet atlas.png \
  --max-size 2048 \
  --size-constraints POT \
  --trim-mode Trim \
  --shape-padding 2 --border-padding 2 \
  --extrude 1 \
  --enable-rotation \
  --multipack \
  ./frames/*.png
```

- `<data-format>` must match your engine's loader (for example the Paper2D format for Unreal sprites, or `json-array`, `phaser`, `unity-spritesheet`...). List supported values with `TexturePacker --help` or the current docs; do not guess.
- `--trim-mode Trim` removes transparent borders but stores offsets. Use `CropKeepPos` to crop while keeping original position data.
- Never trim or rotate frames that will be used as a SubUV flipbook.
- Open-source alternatives exist if you want to avoid a commercial tool; check their output format against your engine.

## 4. Engine setup

### Unreal Engine 5 (Niagara / Materials)

- Texture settings: for VFX flipbooks use **Compression: Default (BC1/BC3)** for color, **Masks** for single-channel data, **sRGB** on for color, off for data. For UI icons use `UserInterface2D (RGBA)` for sharp edges. Do not use `VectorDisplacementMap`; it is for displacement data, not flipbooks.
- Mips: **Mip Gen Settings** `FromTextureGroup` for normal use; set `NoMipmaps` if the flipbook is shown at a fixed small size or edges bleed.
- Texture Group: `Effects` for VFX, `UI` for icons, so streaming and LOD work as intended.
- Niagara: in the Sprite Renderer, enable **Sub UV** and set **Sub Image Size** X (columns) and Y (rows) to match the grid. Use a **SubUV Animation** module with total frames equal to the real frame count, not columns x rows if the last cells are empty.
- Material: use the **Flipbook** node (or SubUV texture sample with `Particle SubUV`), enable **SubUV blending** to interpolate between frames. Use **ParticleSubUV** texture sample type in particle materials.
- Blend mode: `Additive` for fire/energy on black, `Translucent` or `AlphaComposite` for smoke. Prefer Masked + dithering when overdraw is a problem.
- Use **Particle Color** and **Dynamic Parameter** for tinting so one sheet serves many variants.

### Unity / Godot / Web

- Unity: Sprite Atlas for UI/2D; Shader Graph Flipbook node for VFX, Particle System Texture Sheet Animation module with Tiles X/Y.
- Godot: `AnimatedSprite2D` with SpriteFrames from sheet, or a shader using `UV / vec2(cols, rows)` and a frame index.
- Web (Pixi/Phaser): use the JSON atlas format their loaders expect; keep atlases under 4096 for mobile.

## 5. Optimization

- **Share sheets:** one flipbook with color variants via tint, rather than separate recolored sheets.
- **Channel packing:** pack multiple grayscale effects (smoke, fire mask, noise) into R/G/B/A channels of one texture, and select channels in the shader.
- **Resolution per distance:** make 512 and 256 versions for LOD on low settings.
- **Compression:** BC4 for single-channel, BC7 for high-quality RGBA (larger), ASTC on mobile. Verify visually at gameplay scale.
- **Overdraw:** tight quad shapes for particles (cut the corners with custom geometry) reduce fill cost for large transparent sprites.
- **Frame count:** lower the frame count, use blending. Often 16 to 32 frames is enough for VFX.

## 6. Verification checklist

- [ ] Sheet dimensions are POT, and `columns x cell_size = width`.
- [ ] Frame count and order correct; animation plays smoothly and loops.
- [ ] No bleeding at cell edges at mip 0, 1, 2 and at minimum screen size.
- [ ] No dark or white fringes on alpha edges.
- [ ] Pivot stable: the effect does not wobble frame to frame.
- [ ] Sheet size within budget for target platform.
- [ ] Metadata (JSON or grid size) committed with the image.
- [ ] Source frames stored (or reproducible script) for later rebuilds.

## Failure patterns

| Symptom | Fix |
|---------|-----|
| Neighbor frame visible at edges | More padding, disable mips, or clamp UVs |
| SubUV animation off by a few frames | Frame count includes empty cells; set the real count |
| Animation jitters | Frames not aligned to a common pivot; auto-align before packing |
| Dark halo on alpha edges | Extrude/dilate color into transparent pixels; check premultiplied alpha |
| Blurry on screen | Cell resolution too low for on-screen size, or wrong compression |
| Atlas works in tool, fails in engine | Data format mismatch or rotation unsupported; export without rotation |
| Memory too high | Reduce size, channel pack, compress (BC/ASTC), lower frame count |
