# 3D Modeling

Getting a usable, rigged asset into an engine without hand-modeling it.

```
3DModeling/
├── meshy-tripo-3d-pipeline/   generate a mesh from text or an image, then validate it
└── mixamo-auto-rig-mapper/    rig a humanoid, pick the animation set, retarget in UE5
```

## The pipeline

```
meshy-tripo-3d-pipeline      generate, inspect, clean up, fix scale and axes
          |
mixamo-auto-rig-mapper       auto-rig, download the animation set, retarget with IK Rig
          |
ue-character-import-pipeline prove the import actually worked
```

The third step is in [`Videogames`](../Videogames/MAP.md) and it is not optional. A generated character that imports without an error can still be scaled wrong, facing backwards, or bound to the wrong skeleton, and the way you find out is by measuring, not by looking.

## Route

| Need | Skill |
|---|---|
| A prop or character from a prompt or an image | `meshy-tripo-3d-pipeline` |
| The generated mesh is the wrong size or orientation | `meshy-tripo-3d-pipeline`, the scale and axis conventions |
| A humanoid mesh that needs to move | `mixamo-auto-rig-mapper` |
| Retargeting animation onto a different skeleton | `mixamo-auto-rig-mapper`, IK Rig and IK Retargeter |
| The import landed wrong in UE | [`ue-character-import-pipeline`](../Videogames/ue-character-import-pipeline/SKILL.md) |
| A master material and per-asset instances | [`ue-material-instance-builder`](../Videogames/ue-material-instance-builder/SKILL.md) |

## The rule that saves the most time

**Fix scale and axes before rigging, not after.** A rig built on a mesh with the wrong up-axis or the wrong unit scale propagates into every animation and every retarget, and unwinding it costs more than regenerating the asset.

## Not here

- Everything downstream in the engine: [`Videogames`](../Videogames/MAP.md).
- Textures, atlases and sprite sheets: [`Graphics2D`](../Graphics2D/MAP.md).
