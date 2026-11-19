# Graphics 2D

Texture packing for flipbooks and atlases.

```
Graphics2D/
└── sprite-sheet-packer/   layout, padding, ImageMagick/Pillow/TexturePacker, SubUV setup
```

## Route

| Need | Skill |
|---|---|
| Frames into a SubUV sheet for a Niagara effect | `sprite-sheet-packer` |
| A trimmed atlas for 2D sprites | `sprite-sheet-packer` |
| Bleeding or seams between frames | `sprite-sheet-packer`, the padding rules |
| Flipbook timing and animation, once the sheet exists | [`ue2d-flipbook-animation`](../Videogames/ue2d-flipbook-animation/SKILL.md) |
| Crisp pixel art on import | [`ue2d-paper2d-foundations`](../Videogames/ue2d-paper2d-foundations/SKILL.md) |
| The VFX that consumes the SubUV sheet | [`ue-niagara-audio-trigger`](../Audio/ue-niagara-audio-trigger/SKILL.md) |

## Where it sits

```
frames  ->  sprite-sheet-packer  ->  Niagara SubUV   (effects)
                               \->  Paper2D sprite   (2D games)
```

One skill, two consumers, and the padding and power-of-two decisions differ between them. The skill covers both.

## Not here

- Sprite import settings and sort order: [`Videogames`](../Videogames/MAP.md), `ue2d-paper2d-foundations`.
- Generating the frames in the first place: [`3DModeling`](../3DModeling/MAP.md) for rendered sequences.

## Known gap

Only one skill. Nothing covers authoring or generating 2D art, UI texture atlases, or icon pipelines. Logged for `monthly-skills-checkup` to judge whether that is a gap worth filling or a category that is simply this small.
