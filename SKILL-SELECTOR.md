# Skill Selector

Instructions for Claude: given a project or task, choose the smallest set of skills from this arsenal, extract only those into the project, and ignore the rest. Do not load the whole arsenal. Every extra skill costs context and dilutes instructions.

## Rules

1. **Read descriptions, not bodies.** Decide from the frontmatter (`name`, `description`) only. Open a full `SKILL.md` only after you have selected it.
2. **Select by task, not by topic.** A skill is needed only if the work will actually perform what its description says in this session or project phase. "Related to the project" is not enough.
3. **Smallest set that covers the work.** Prefer 2 to 6 skills. If you pick more than 8, split the work into phases and extract per phase.
4. **One skill per concern.** If two skills overlap, pick the one whose trigger matches the concrete deliverable; mention the other as optional.
5. **Respect dependencies.** Some skills assume another one (see the map below). Pull in the dependency only when the dependent skill is selected.
6. **Say why.** For every selected skill write one line: the task it serves. For notable rejected skills write one line: why not.
7. **Ask only if blocked.** If the project description does not say the engine, the platform, or the deliverable, ask one short question. Otherwise infer and state the assumption.
8. **Never edit the arsenal while selecting.** Selecting and extracting are read-only on this repo.

## Procedure

1. **Parse the need.** Write down: goal, deliverables, engine/language, platform, phase (prototype, production, polish), and hard constraints (budget, license, offline).
2. **List candidate skills.** Dump the descriptions (cheap):

   ```bash
   cd ~/.claude/skills   # or the arsenal clone
   for f in */SKILL.md */*/SKILL.md; do
     [ -f "$f" ] || continue
     echo "== $f"
     grep -m2 -E '^(name|description):' "$f" | cut -c1-300
   done
   ```

3. **Match** each deliverable to a skill using the catalog below. Mark each skill: `needed`, `optional`, or `no`.
4. **Resolve dependencies and conflicts** with the map below.
5. **Extract** only the `needed` skills (and `optional` ones the user approves).
6. **Report** the selection (format below), then proceed with the task using only the extracted skills.

## Catalog

Use the trigger column to match. Paths are relative to the arsenal root.

### Content and video pipeline (Spanish short-form, faceless creator)

| Skill | Path | Select when the task is... |
|-------|------|----------------------------|
| `topic-miner` | `topic-miner` | Finding video topics / refilling the content pipeline |
| `stack-scout` | `stack-scout` | Comparing tools or vendors, build vs buy, pricing |
| `anti-slop` | `anti-slop` | Final pass on a finished Spanish script |
| `script-qa` | `script-qa` | Storyboard for a QA walkthrough video |
| `script-stakeholder` | `script-stakeholder` | Storyboard for PO / stakeholders / non-technical audience |
| `demo-video` | `demo-video` | Planning and rendering a feature demo video |
| `audio-clone` | `audio-clone` | Narrating text with the user's own fish.audio voice |
| `notebook-cast` | `notebook-cast` | Podcast or study artifacts from sources via Gemini Notebook |
| `exam-dumps` | `exam-dumps` | Scraping certification exam questions (ExamTopics) |

### 3D modeling

| Skill | Path | Select when the task is... |
|-------|------|----------------------------|
| `meshy-tripo-3d-pipeline` | `3DModeling/meshy-tripo-3d-pipeline` | Generating 3D props/characters from text or images |
| `mixamo-auto-rig-mapper` | `3DModeling/mixamo-auto-rig-mapper` | Rigging a humanoid mesh, animation download, retargeting |

### Graphics 2D / VFX textures

| Skill | Path | Select when the task is... |
|-------|------|----------------------------|
| `sprite-sheet-packer` | `Graphics2D/sprite-sheet-packer` | Flipbooks (SubUV), atlases, animated icons |

### Audio for games

| Skill | Path | Select when the task is... |
|-------|------|----------------------------|
| `elevenlabs-sfx-generator` | `Audio/elevenlabs-sfx-generator` | Producing sound effects with AI |
| `bark-edge-tts-dialogue` | `Audio/bark-edge-tts-dialogue` | Character voice lines / barks with TTS |
| `ue-niagara-audio-trigger` | `Audio/ue-niagara-audio-trigger` | Triggering Niagara VFX and sound from gameplay events in UE5 |
| `ue-sfx-pipeline` | `Audio/ue-sfx-pipeline` | Getting a sound file into UE5 and playing it: format, mono, attenuation, concurrency |

### Game development

| Skill | Path | Select when the task is... |
|-------|------|----------------------------|
| `ue-character-movement` | `Videogames/ue-character-movement` | UE5 character locomotion, CMC, AnimInstance, BlendSpaces |
| `ue-material-instance-builder` | `Videogames/ue-material-instance-builder` | UE5 material instances, per-item textures, rarity/dissolve FX |
| `drag-drop-raycaster` | `Videogames/drag-drop-raycaster` | Drag-and-drop in 3D, cursor to world, slot snapping |
| `state-machine-architect` | `Development/state-machine-architect` | Any phase/mode logic: turns, game flow, AI states, UI flows |
| `ue-indie-game-setup` | `Videogames/ue-indie-game-setup` | UE5 runs slow, heavyweight template, choosing what to turn off, "indie setup" |
| `ue-minimal-level-bootstrap` | `Videogames/ue-minimal-level-bootstrap` | Creating a minimal/blank/greybox UE5 level by script, replacing a template level |
| `ue-3d-architect` | `Videogames/ue-3d-architect` | Starting/structuring a 3D level or game, greyboxing, blockout, spatial metrics, scope layout |
| `ue-cpp-module-bootstrap` | `Videogames/ue-cpp-module-bootstrap` | Adding C++ to a Blueprint project, builds, forced editor restarts |
| `ue-enhanced-input-cpp` | `Videogames/ue-enhanced-input-cpp` | Player input in C++, keys that do nothing, WASD + mouse look |
| `ue-character-import-pipeline` | `Videogames/ue-character-import-pipeline` | Importing a rigged character FBX, broken/sideways/backwards meshes |
| `ue-third-person-camera` | `Videogames/ue-third-person-camera` | Follow camera, camera-relative movement, camera clipping |
| `ue-sprint-and-dash` | `Videogames/ue-sprint-and-dash` | Run or sprint key, dash/dodge, foot sliding during locomotion |
| `ue-actor-spawner` | `Videogames/ue-actor-spawner` | Wave spawner, mob or reward generator, periodic actor spawning |
| `ue-proximity-reactions` | `Videogames/ue-proximity-reactions` | Pickups highlighting near the player, distance-driven effects |
| `ue-timers-and-triggers` | `Videogames/ue-timers-and-triggers` | Wave timers, cooldowns, pickups, trigger volumes, overlaps not firing |
| `ue-canvas-hud` | `Videogames/ue-canvas-hud` | On-screen counters, health bars, countdown rings, a start screen |
| `ue-procedural-animation` | `Videogames/ue-procedural-animation` | A needed animation clip does not exist; authoring one from the rig |
| `ue2d-architect` | `Videogames/ue2d-architect` | Starting/structuring a 2D game, tile size and pixel scale, 2D blockout, room graph, progression layout |
| `ue2d-paper2d-foundations` | `Videogames/ue2d-paper2d-foundations` | Starting a 2D game, blurry pixel art, sprite sort order |
| `ue2d-flipbook-animation` | `Videogames/ue2d-flipbook-animation` | Animating 2D characters, flipbooks, PaperZD state machines |
| `ue2d-platformer-controller` | `Videogames/ue2d-platformer-controller` | 2D platformer movement, floaty or unresponsive jumps |
| `ue2d-tilemap-levels` | `Videogames/ue2d-tilemap-levels` | 2D level building, tile maps, Tiled import, snagging on tile seams |
| `ue2d-camera-2d` | `Videogames/ue2d-camera-2d` | 2D camera feel, jitter, nausea, room bounds |
| `ue2d-parallax-backgrounds` | `Videogames/ue2d-parallax-backgrounds` | Depth in 2D scenes, scrolling backgrounds, seams |
| `ue2d-hitboxes-and-combat` | `Videogames/ue2d-hitboxes-and-combat` | 2D melee or projectile combat, multi-hits, combat impact |
| `ue2d-sprite-lighting` | `Videogames/ue2d-sprite-lighting` | Flat-looking 2D art, sprites ignoring lights, hit flashes |
| `ue-project-build` | `Videogames/ue-project-build` | UE 5.8 compile, Live Coding, cook, package, toolchain |
| `ue-contracts-types` | `Videogames/ue-contracts-types` | Interfaces, data assets, and the types systems use instead of Cast |
| `ue-gameplay-tags` | `Videogames/ue-gameplay-tags` | Tag vocabulary for items, damage, states, abilities |
| `ue-merge-objects` | `Videogames/ue-merge-objects` | Two items of one family become one new item |
| `ue-state-machines` | `Videogames/ue-state-machines` | AnimBP vs State Tree vs GAS vs a C++ mode machine |
| `ue-action-time-windows` | `Videogames/ue-action-time-windows` | Startup, active, recovery, buffer, cancel, hitstop |
| `ue-anim-montages-notifies` | `Videogames/ue-anim-montages-notifies` | One-shot montages, sections, notifies |
| `ue-combo-systems` | `Videogames/ue-combo-systems` | Combo graphs, buffers, cancel edges |
| `ue-breaking-the-4th-wall` | `Videogames/ue-breaking-the-4th-wall` | The game acknowledges the camera, the real keybind, the HUD, or the save |
| `ue-loop-systems` | `Videogames/ue-loop-systems` | Moment, session and meta loops, or a time-loop reset |

### Narrative and records

| Skill | Path | Select when the task is... |
|-------|------|----------------------------|
| `the-watcher` | `Narrative/the-watcher` | Devlog, development diary, making-of, jam writeup, launch thread, postmortem with personality |

## Dependency and combination map

| If you select | Also consider | Why |
|---------------|---------------|-----|
| `mixamo-auto-rig-mapper` | `ue-character-movement` | Rigged characters need locomotion/AnimBP wiring |
| `meshy-tripo-3d-pipeline` (characters) | `mixamo-auto-rig-mapper` | Generated characters usually need a rig |
| `meshy-tripo-3d-pipeline` (any, UE5) | `ue-material-instance-builder` | Generated textures need master material + instances |
| `ue-niagara-audio-trigger` | `elevenlabs-sfx-generator`, `sprite-sheet-packer` | Source of the sounds and flipbook textures it plays |
| `bark-edge-tts-dialogue` | `state-machine-architect` | Only if voice lines are driven by dialogue/combat states |
| `drag-drop-raycaster` | `state-machine-architect` | Drag states: idle, hover, dragging, snapped, dropped |
| `ue-indie-game-setup` | `ue-minimal-level-bootstrap` | Cutting render settings is half the job; a heavy template level undoes it |
| `ue-minimal-level-bootstrap` | `ue-indie-game-setup` | A clean level still renders with whatever the project's render stack is |
| `ue-3d-architect` | `ue-minimal-level-bootstrap`, `ue-indie-game-setup` | The blockout needs a clean level to live in and an honest frame budget |
| `ue2d-architect` | `ue2d-paper2d-foundations`, `ue2d-platformer-controller` | The pixel contract and the jump arc the blockout is dimensioned from |
| `ue-cpp-module-bootstrap` | `ue-project-build` | The files are the bootstrap. Versions, reload and cook are the build skill |
| `ue-combo-systems` | `ue-action-time-windows`, `ue-anim-montages-notifies` | A combo edge is only legal inside a window on a montage |
| `ue-merge-objects` | `ue-contracts-types`, `ue-gameplay-tags` | The recipe is data and tags, not a new subclass |
| `ue-breaking-the-4th-wall` | `ue-state-machines`, `ue-enhanced-input-cpp` | One director owns the beat, and the line must read the real binding |
| `ue-loop-systems` | `ue-state-machines` | The session phase is a machine. Tick does not decide that the run ended |
| `the-watcher` | nothing | Reads the record; it never needs another skill to write the chronicle |
| `demo-video` | `script-qa` or `script-stakeholder` | Audience-specific script before rendering |
| `script-qa` / `script-stakeholder` | `anti-slop`, `audio-clone` | Final polish and narration, only when delivering a finished video |
| `topic-miner` | `stack-scout` | Only when topics depend on tool comparisons |

Mutually exclusive picks (choose one per deliverable):
- `script-qa` vs `script-stakeholder`: audience decides (testers vs non-technical).
- `elevenlabs-sfx-generator` vs `bark-edge-tts-dialogue`: SFX vs spoken voice.
- `audio-clone` vs `bark-edge-tts-dialogue`: narrating a script in the user's own voice (Spanish video pipeline) vs in-game character dialogue.

## Extraction

Extract into the project so only the chosen skills load there. Prefer symlinks (they stay in sync with the arsenal); use copies for projects that must be self-contained or shared with others.

```bash
ARSENAL=~/.claude/skills            # path to this repo
PROJECT=/path/to/project
mkdir -p "$PROJECT/.claude/skills"

# Extract by relative path; the skill is placed one level deep under its own name
extract() {
  local rel="$1"; local name; name="$(basename "$rel")"
  ln -sfn "$ARSENAL/$rel" "$PROJECT/.claude/skills/$name"
  # copy instead:  cp -r "$ARSENAL/$rel" "$PROJECT/.claude/skills/$name"
}

extract Videogames/ue-material-instance-builder
extract Development/state-machine-architect
```

Notes:
- Claude Code looks for skills at `<skills-dir>/<skill-name>/SKILL.md`. Skills inside category folders (`3DModeling/`, `Audio/`, ...) may not be discovered when the arsenal is used directly as the skills directory. Extracting each one to `.claude/skills/<name>` puts it at the expected depth.
- Extract the whole skill folder (it may contain `references/` or scripts), not only `SKILL.md`.
- Do not extract `synced/` or the base-layer plugins; they are managed separately.
- Do not commit symlinks that point outside the repo. If the project is shared, copy instead, or document the extraction commands.
- Restart the session after extracting; skills load at session start.

To undo: delete the project's `.claude/skills/<name>` link or folder. The arsenal is untouched.

## Report format

Reply with this before doing the work:

```
Task understanding: <one or two lines: goal, engine, deliverables, phase>
Assumptions: <only if inferred>

Selected (extracted):
- <skill> - <task it serves>
- ...

Optional (not extracted, say if you want them):
- <skill> - <when it would help>

Rejected:
- <skill> - <why not>

Extraction:
<the extract commands that were run>
```

## Sample

**Request:** "I'm prototyping a card battler in UE5. Cards are 3D objects the player drags from hand onto board slots. I want to generate the creature models and animate them, add sounds and effects when cards are played, and have creatures talk. Turn-based. Cards have rarity with glowing foil."

**Parsed need:** UE5, 3D cards with drag-and-drop, AI-generated creatures (rigged, animated), SFX + VFX on card play, creature voice lines, turn flow, rarity-based material look. Phase: prototype.

**Candidate matching:**

| Deliverable | Skill | Decision |
|-------------|-------|----------|
| Drag cards onto slots | `drag-drop-raycaster` | needed |
| Turn phases (draw, play, resolve, end) | `state-machine-architect` | needed |
| Creature models from images/text | `meshy-tripo-3d-pipeline` | needed |
| Rig and animate creatures | `mixamo-auto-rig-mapper` | needed, but only if creatures are humanoid (see below) |
| Rarity glow, card art, dissolve | `ue-material-instance-builder` | needed |
| VFX + sound on card play | `ue-niagara-audio-trigger` | needed |
| Card-play and spell sounds | `elevenlabs-sfx-generator` | needed |
| Creature voice lines | `bark-edge-tts-dialogue` | optional (prototype can ship silent) |
| Animated foil/burst textures | `sprite-sheet-packer` | optional (only if flipbook VFX are wanted) |
| Character movement | `ue-character-movement` | no (creatures are stationary on slots) |
| Video, scripts, stack, exam, notebook skills | - | no (not part of the game build) |

**Assumption check:** insectoid creatures are not humanoid, so Mixamo's auto-rigger is a poor fit. Ask once: "Are the creatures humanoid?" If no, drop `mixamo-auto-rig-mapper` and note that rigging is manual or uses Tripo/Meshy rigging.

**Output to the user:**

```
Task understanding: UE5 card battler prototype. Drag 3D cards to slots, AI-generated
creatures, SFX/VFX on card play, rarity foil materials, turn-based flow.
Assumptions: creatures may be non-humanoid; voice lines are not required for the prototype.

Selected (extracted):
- drag-drop-raycaster - drag cards from hand to board slots with snapping
- state-machine-architect - turn phases and drag states
- meshy-tripo-3d-pipeline - generate and validate creature meshes
- ue-material-instance-builder - rarity glow, card art, dissolve per card
- ue-niagara-audio-trigger - tag-driven VFX + sound on card play
- elevenlabs-sfx-generator - card-play and spell sound effects

Optional (not extracted, say if you want them):
- mixamo-auto-rig-mapper - only for humanoid creatures that need animation
- bark-edge-tts-dialogue - creature voice lines
- sprite-sheet-packer - flipbook foil/burst textures

Rejected:
- ue-character-movement - creatures do not locomote
- topic-miner, stack-scout, anti-slop, script-qa, script-stakeholder, demo-video,
  audio-clone, notebook-cast, exam-dumps - content pipeline, not the game build

Extraction:
extract Videogames/drag-drop-raycaster
extract Development/state-machine-architect
extract 3DModeling/meshy-tripo-3d-pipeline
extract Videogames/ue-material-instance-builder
extract Audio/ue-niagara-audio-trigger
extract Audio/elevenlabs-sfx-generator
```

Result: 6 of 18 skills loaded in the project, 3 more available on request, nothing else in context.

### Second sample (non-game)

**Request:** "Make a short video showing the PO what the new checkout retry feature does."

**Selected:** `script-stakeholder` (audience is a PO), `demo-video` (render), `anti-slop` (final pass on the Spanish script), `audio-clone` (narration in the user's voice).
**Rejected:** `script-qa` (audience is not QA), all game, 3D and audio-for-games skills.
