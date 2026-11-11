# skills-arsenal

Personal Claude Code skills, synced across machines.

Each directory is one skill, defined by a `SKILL.md` with YAML frontmatter
(`name`, `description`) followed by the instructions Claude loads on invocation.

## Skills

| Skill | Purpose |
|-------|---------|
| [`topic-miner`](topic-miner/SKILL.md) | Mine recent AI news for short-form technical video topics with a senior engineering angle. Outputs scored topics in Spanish. |
| [`stack-scout`](stack-scout/SKILL.md) | Scout tools for a need or painpoint, model real cost at your scale, decide build vs buy. Produces a sequenced build strategy when nothing fits. |
| [`anti-slop`](anti-slop/SKILL.md) | Quality gate for Spanish short-form scripts. Kills generic AI phrasing at word, rhythm and structure level, enforces the spoken word budget, returns a ships/doesn't-ship verdict. |
| [`exam-dumps`](exam-dumps/SKILL.md) | Drive the local Free-Exam-Dumps scraper: list ExamTopics certifications with descriptions, scrape the selected one, loop. Maps outputs and the two upstream breakages. |
| [`audio-clone`](audio-clone/SKILL.md) | Generate speech from text with the user's own fish.audio cloned voices. Lists My Voices, renders the chosen one to mp3, loops. Token from `.env`. |
| [`demo-video`](demo-video/SKILL.md) | Demo videos that explain one functionality: problem, the single move, the proof. Always gates on an approved scene script with labels, then drives the HyperFrames CLI to render. |
| [`script-qa`](script-qa/SKILL.md) | Storyboard for a QA walkthrough: preconditions, one step per frame, each with its expected result and how failure looks. Covers features, bug-fix verification, regression and boundary cases. |
| [`script-stakeholder`](script-stakeholder/SKILL.md) | Storyboard for product owners and stakeholders: before, the moment, after, what it means, the limit. Strips all technical detail and swaps jargon for outcomes. |
| [`notebook-cast`](notebook-cast/SKILL.md) | Group sources into a Gemini Notebook and fire a generation — podcast by default, plus video, reports, quizzes, slides. Async: reports the artifact id, never waits. |
| [`aws-log-insights`](aws-log-insights/SKILL.md) | Forensic RCA on AWS logs: noise filtering, trace ID check, CloudWatch Logs Insights queries, metric filter and alarm. Can scan a root of repos to find a target's log groups. Output in Spanish. |

> Working on a specific project? Use [`SKILL-SELECTOR.md`](SKILL-SELECTOR.md): it tells Claude how to
> pick only the skills a task needs and extract them into the project, with a worked example.

### 3DModeling

| Skill | Purpose |
|-------|---------|
| [`meshy-tripo-3d-pipeline`](3DModeling/meshy-tripo-3d-pipeline/SKILL.md) | AI 3D generation with Meshy and Tripo: input image prep, prompting, API workflow, inspection checklist, cleanup, scale and axis conventions, engine validation. |
| [`mixamo-auto-rig-mapper`](3DModeling/mixamo-auto-rig-mapper/SKILL.md) | Auto-rig humanoid meshes (Mixamo, Tripo, Meshy), choose the animation set, import and retarget in UE5 with IK Rig and IK Retargeter. |

### Audio

| Skill | Purpose |
|-------|---------|
| [`ue-niagara-audio-trigger`](Audio/ue-niagara-audio-trigger/SKILL.md) | Unreal Engine 5 VFX and audio orchestration: tag-driven cues, Niagara parameter driving, MetaSound parameters, pooling, concurrency, networking and dedicated-server guards. |
| [`elevenlabs-sfx-generator`](Audio/elevenlabs-sfx-generator/SKILL.md) | AI sound effects: prompt structure, ElevenLabs parameters, trimming, loudness targets, layering and variation, engine hand-off. |
| [`bark-edge-tts-dialogue`](Audio/bark-edge-tts-dialogue/SKILL.md) | Character dialogue with Bark, Edge-TTS and XTTS: line writing, correct Bark tags, voice profiles, batching and caching, loudness, licensing. |
| [`ue-sfx-pipeline`](Audio/ue-sfx-pipeline/SKILL.md) | Take a raw sound file to something Unreal actually plays: WAV conversion, trimming dead air that delays the hit, mono downmix so it spatialises at all, SoundAttenuation and SoundConcurrency assets, and PlaySoundAtLocation with randomised pitch for self-destroying pickups. |

### Graphics2D

| Skill | Purpose |
|-------|---------|
| [`sprite-sheet-packer`](Graphics2D/sprite-sheet-packer/SKILL.md) | Pack frames into SubUV flipbooks or trimmed atlases: layout, padding, ImageMagick/Pillow/TexturePacker commands, Niagara SubUV setup, optimization. |

### Development

| Skill | Purpose |
|-------|---------|
| [`state-machine-architect`](Development/state-machine-architect/SKILL.md) | Design and implement finite state machines in any language: when to use one, transition tables, hierarchical and parallel variants, async-safe TypeScript reference, anti-patterns, testing. |

### Videogames

| Skill | Purpose |
|-------|---------|
| [`ue-character-movement`](Videogames/ue-character-movement/SKILL.md) | Unreal Engine 5 locomotion patterns: CMC setup, custom movement modes, thread-safe AnimInstance data flow, BlendSpaces, root motion, AI and network prediction. C++ and Blueprint. |
| [`drag-drop-raycaster`](Videogames/drag-drop-raycaster/SKILL.md) | 3D drag-and-drop math: screen-to-world rays, ray-plane intersection, grab offset, frame-rate independent follow, slot snapping. TypeScript/Three.js and Unreal C++. |
| [`ue-material-instance-builder`](Videogames/ue-material-instance-builder/SKILL.md) | UE5 material instances: MIC vs MID vs Custom Primitive Data vs MPC, parameter contract, C++ runtime driving, Python editor automation, rarity and dissolve techniques. |
| [`ue-indie-game-setup`](Videogames/ue-indie-game-setup/SKILL.md) | Cut a UE5 project to an indie render budget: diagnose the frame, three scenario profiles (conservative 3D default, stylized low-poly, flat 2D), the cvar set per profile and why, template scope auditing, and the measurement traps that fake a frame rate. |
| [`ue-3d-architect`](Videogames/ue-3d-architect/SKILL.md) | Architect a 3D level or game shapes-first: derive every dimension from the pawn's capsule, step height and jump apex, script a colour-coded greybox from BasicShapes, play the box before any art exists, then swap meshes in without moving the metrics. Includes the actor/class map the blockout implies. |
| [`ue-minimal-level-bootstrap`](Videogames/ue-minimal-level-bootstrap/SKILL.md) | Script a minimal playable UE5 level (floor, sun, SkyLight, atmosphere, fog, reflection capture, PlayerStart) headless via the pythonscript commandlet, and set it as default map. Avoids the world GC leak crash. |
| [`ue-cpp-module-bootstrap`](Videogames/ue-cpp-module-bootstrap/SKILL.md) | Turn a Blueprint-only project into C++: Target/Build/module files, command-line builds on every platform, and exactly what forces an editor restart. Live Coding is Windows-only; terminal builds silently disable the Compile button. |
| [`ue-enhanced-input-cpp`](Videogames/ue-enhanced-input-cpp/SKILL.md) | Enhanced Input entirely from C++, with actions and mapping contexts built in code. The WASD swizzle/negate recipe, trigger-event choice, and the BeginPlay ordering bug that silently kills every key. |
| [`ue-character-import-pipeline`](Videogames/ue-character-import-pipeline/SKILL.md) | Import a rigged character FBX and prove it worked: choose the file by its skeleton not its name, the save trap that orphans a SkeletalMesh, scale and axis conversion, measuring mesh facing from the hips, and a rename pass with reference fixup. |
| [`ue-third-person-camera`](Videogames/ue-third-person-camera/SKILL.md) | Spring arm and follow camera: who owns the control rotation, camera-relative movement, orient-to-movement, collision pull-in and lag. Includes why the camera looks frozen when only movement is bound. |
| [`ue-sprint-and-dash`](Videogames/ue-sprint-and-dash/SKILL.md) | Hold-to-run speed switching and dash variants, plus driving animation play rate from real velocity so one walk clip covers every speed and the feet stop sliding. Cooldowns, i-frames and air dash. |
| [`ue-actor-spawner`](Videogames/ue-actor-spawner/SKILL.md) | Reusable timed spawner for mobs, rewards or hazards: timer-driven with no Tick, a hard cap on live actors, weak pointers, uniform spawn distribution over a disc and a per-wave difficulty counter. |
| [`ue-proximity-reactions`](Videogames/ue-proximity-reactions/SKILL.md) | Distance-driven reactions such as a gold glow on nearby pickups: authoring the parameterised material from Python, per-actor dynamic instances, and the three habits that keep it cheap across dozens of actors. |
| [`ue-timers-and-triggers`](Videogames/ue-timers-and-triggers/SKILL.md) | FTimerManager for waves, delays and cooldowns instead of counting down in Tick, plus overlap setup for pickups and trigger volumes including the response rules that decide whether an overlap fires at all. |
| [`ue-canvas-hud`](Videogames/ue-canvas-hud/SKILL.md) | HUDs and menus in C++ with AHUD and Canvas: counters, health bars with measured centring, circular countdown rings, and a title screen with a clickable PLAY button via hit boxes. |
| [`ue-procedural-animation`](Videogames/ue-procedural-animation/SKILL.md) | Author an AnimSequence from scratch in Python when the clip does not exist: which 5.2 read APIs return empty, reading the pose from a live component, deriving rotation axes from rig geometry, and verifying each pass with a screenshot. |

#### 2D games (Unreal)

| Skill | Purpose |
|-------|---------|
| [`ue2d-architect`](Videogames/ue2d-architect/SKILL.md) | Architect a 2D game shapes-first: the pixel-per-unit and tile contract, reach expressed in tiles, depth lanes with collision on one lane only, a blockout of tinted rectangles driven from a table, the room graph, and the swap to tilemaps without moving a collision edge. |
| [`ue2d-paper2d-foundations`](Videogames/ue2d-paper2d-foundations/SKILL.md) | Paper2D project setup: sprite import settings that keep pixel art crisp, pixels-per-unit discipline, orthographic camera sizing for an exact pixel ratio, sort order bands and the 3D render features to switch off. |
| [`ue2d-flipbook-animation`](Videogames/ue2d-flipbook-animation/SKILL.md) | Flipbooks and PaperZD state machines: frame timing in frames not seconds, driving animation from gameplay state without letting it write back, and one-shots over locomotion. |
| [`ue2d-platformer-controller`](Videogames/ue2d-platformer-controller/SKILL.md) | Platformer feel: jump arcs derived from height and time-to-apex, asymmetric gravity, variable jump height, coyote time, jump buffering, ledge nudging and one-way platforms. |
| [`ue2d-tilemap-levels`](Videogames/ue2d-tilemap-levels/SKILL.md) | Paper2D tile maps: per-tile collision flush with tile bounds, one collision layer only, importing from Tiled, and chunking large maps for streaming. |
| [`ue2d-camera-2d`](Videogames/ue2d-camera-2d/SKILL.md) | A 2D follow camera that does not cause nausea: dead zones, interpolated look-ahead, asymmetric vertical damping, room-bounds clamping and pixel snapping applied last. |
| [`ue2d-parallax-backgrounds`](Videogames/ue2d-parallax-backgrounds/SKILL.md) | Layered parallax: factor choice including foreground above 1.0, the exact tiling arithmetic that avoids seams, material-panner skies and the overdraw budget. |
| [`ue2d-hitboxes-and-combat`](Videogames/ue2d-hitboxes-and-combat/SKILL.md) | 2D combat as a contract: separate hitbox and hurtbox channels, startup/active/recovery frame data, notify-driven windows, one hit per swing, hitstop and knockback. |
| [`ue2d-sprite-lighting`](Videogames/ue2d-sprite-lighting/SKILL.md) | Lighting and materials for sprites: unlit versus lit, normal maps, masked versus translucent alpha and what each costs, and gameplay-driven flash and dissolve parameters. |

### Narrative

| Skill | Purpose |
|-------|---------|
| [`the-watcher`](Narrative/the-watcher/SKILL.md) | Turn the real record of a build into an epic, funny chronicle: mine git, the Claude Code session transcript, engine logs and timestamps into a dated timeline, stage it as acts where every chapter is a real obstacle with its real number, and close with what is honestly still unverified. |

## Install on a new machine

This repo *is* the personal skills directory. Clone it into place:

```bash
git clone git@codexmaker:CodeXMakerCompany/skills-arsenal.git ~/.claude/skills
```

If `~/.claude/skills` already exists, clone elsewhere and symlink it instead.

## Base layer

External plugins installed alongside this repo. They are *not* part of the arsenal —
they come from the Anthropic plugin directory and follow their own release cycles.
Install them after cloning:

```bash
claude plugin install auto-research@anthropic-plugin-directory -y
claude plugin install unslop@anthropic-plugin-directory -y
claude plugin install caveman-mode-short-answers@anthropic-plugin-directory -y
claude plugin install linkedin-career-intelligence---rankedin@anthropic-plugin-directory -y
```

`hyperframes` ships from HeyGen's own marketplace rather than the Anthropic
directory, so it takes its own line:

```bash
claude plugin install hyperframes --marketplace heygen-com/hyperframes -y
```

| Plugin | Tier | Purpose | Runs |
|--------|------|---------|------|
| `hyperframes` | must | Render stage — write HTML, render video. Eight skills: the render contract, the CLI, ~450 registry blocks, captions and overlays, media and voiceover, Figma import, Remotion port, slideshows. | local |
| `auto-research` | must | Improves a skill in this repo — 5 parallel research agents, then a keep/discard loop. `/auto-research <skill>`. Rewrites `SKILL.md` in place, so commit first. | local |
| `unslop` | reference | AI-slop guardrail for prose. German/English only, so it does not replace `anti-slop` — it is the blueprint `anti-slop` was built from. | local |
| `caveman` | optional | Short, direct answers, no filler. `/caveman` toggles it. | local |
| `rankedin` | optional | Career positioning and next-move analysis. Outside the content pipeline. | remote MCP — input leaves the machine |

### Prerequisites

Only `hyperframes` needs anything beyond the install. Check both before trusting a
render on a new machine:

| Needs | Why | Check |
|-------|-----|-------|
| Node 22+ | the CLI runs through the plugin's own launcher, `plugin-cli.mjs` | `node --version` |
| `ffmpeg` on `PATH` | audio, grading, transcripts and render all shell out to it | `ffmpeg -version` |

```bash
sudo apt install ffmpeg      # Debian/Ubuntu/Pop!_OS
```

> Everything in this section is community-published and unreviewed (`review: none`),
> except `hyperframes`, which is Apache-2.0 from HeyGen.
> `claude plugin list` is the source of truth for what is enabled on a machine.

## Sync

```bash
cd ~/.claude/skills
git pull            # get skills from other machines
git add . && git commit -m "add: <skill>" && git push
```

Skills are loaded at session start — restart Claude Code after pulling for new
skills to appear in the `/` menu.


