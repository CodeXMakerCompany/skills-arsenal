# skills-arsenal

Personal Claude Code skills, synced across machines.

Each skill is a directory with a `SKILL.md`: YAML frontmatter (`name`, `description`) followed by
the instructions Claude loads on invocation. Skills are grouped into category directories, each with
a `MAP.md` that routes a task to its leaf. 132 skills.

Start at [`ARSENAL-MAP.md`](ARSENAL-MAP.md) for the graph, [`COMBOS.md`](COMBOS.md) for the small sets
that work well together, or [`codex-mode`](Agentic/codex-mode/SKILL.md), which is the operating style
everything else hangs off.

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

> **Two doors.** [`ARSENAL-MAP.md`](ARSENAL-MAP.md) is for finding the skill you need right now: the
> category graph, routing by the shape of the work, and the three spines most tasks walk along. Each
> category also has its own `MAP.md`. [`SKILL-SELECTOR.md`](SKILL-SELECTOR.md) is for extracting a
> subset into a project. The [`arsenal-help`](Meta/arsenal-help/SKILL.md) skill is the map with
> reasoning attached, for when a task could land in three places.

### Agentic

How work gets run. [`MAP`](Agentic/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`codex-mode`](Agentic/codex-mode/SKILL.md) | **The entry point.** The operating style: principles cited by name, deliberate subagents with a model per role, every design priced, every claim evidenced. Ships 12 playbooks (bug fix, feature, refactoring, perf, eval, shipping, incident, autonomous run) and the `worker.md` rules every spawned agent reads first. |
| [`clarity`](Agentic/clarity/SKILL.md) | The requirements gate, and the one skill in the arsenal that stops you. Extracts every requirement as a testable statement, then blocks execution on anything ambiguous, inconsistent, or missing until the owner resolves it in writing. Draws the line against never-block: a wrong guess you can refactor is yours to make, a wrong guess that needs a rewrite is not. |
| [`architect`](Agentic/architect/SKILL.md) | Two shapes before any code: types, signatures, boundaries, and the cost per request of each. Picks the one where state has one owner and callers know least. |
| [`arena`](Agentic/arena/SKILL.md) | N candidates at one task on different models, a blind cross-judge, pick a base, graft the strongest parts of the losers. |
| [`swarm`](Agentic/swarm/SKILL.md) | N workers over slices or racing one brief, drained into a single report. Declares the selection rule before spawning. |
| [`figure-it-out`](Agentic/figure-it-out/SKILL.md) | Design the playbook when none fits: rigor scaled to the task, a hypothesis loop, an auditable decision trail. |
| [`sharpen`](Agentic/sharpen/SKILL.md) | Make a task deeper, not bigger, then rewrite the prompt to ask for what a top practitioner would do. |
| [`recall`](Agentic/recall/SKILL.md) | Rebuild working context across recent sessions plus the shared record, into a tagged thread capsule. |
| [`ketchup`](Agentic/ketchup/SKILL.md) | Catch the human up in plain words and small visuals, then every call waiting on them with enough to decide. |
| [`show-me-your-work`](Agentic/show-me-your-work/SKILL.md) | The decision trail for long or unattended runs: an append-only TSV, audited against what actually happened, reviewed by another model. |
| [`kiro-agent-creator`](Agentic/kiro-agent-creator/SKILL.md) | Create Kiro custom agents (IDE 1.0 / CLI V3) with least privilege, write them to `.kiro/agents/` or `~/.kiro/agents/`, and wire sub-agents into an orchestrator. Ships a script that creates, validates, wires and lists. |

### Principles

24 leaves the mode skill cites. Rules, not workflows. [`MAP`](Principles/MAP.md)

Core: laziness-protocol, foundational-thinking, redesign-from-first-principles, attack-the-premise, subtract-before-you-add, minimize-reader-load, outcome-oriented-execution, experience-first, exhaust-the-design-space, build-the-lever. Architecture: model-the-domain, boundary-discipline, type-system-discipline, make-operations-idempotent, migrate-callers-then-delete-legacy-apis, separate-before-serializing-shared-state. Verification: prove-it-works, fix-root-causes, sequence-verifiable-units, test-behavior-not-implementation, explain-the-number. Delegation and meta: guard-the-context-window, never-block-on-the-human, encode-lessons-in-structure.

### Verification

Proof, not plausibility. [`MAP`](Verification/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`interrogate`](Verification/interrogate/SKILL.md) | Adversaries on different models try to break a change. A finding survives only when a run proves it. |
| [`blast-radius`](Verification/blast-radius/SKILL.md) | What breaks elsewhere, beyond the diff. Finds the one fact the change is safe because of and proves it by running code. |
| [`benchmark-checklist`](Verification/benchmark-checklist/SKILL.md) | Seven questions that vet a performance number: limiter, tuning, limits, errors, repeatability, relevance, and whether the work happened. |
| [`tdd`](Verification/tdd/SKILL.md) | Failing test first where the path is cheap, and an honest alternative where it is not. |
| [`statechart`](Verification/statechart/SKILL.md) | Model-check an ordering risk with TLA+, then show the bug as a path through states in the reader's words. |
| [`create-verification-skill`](Verification/create-verification-skill/SKILL.md) | Generate the repo's own way to drive the real app: launch, doctor, drive, evidence, cleanup, plus a seeded feature map. |
| [`maintain-verification-skill`](Verification/maintain-verification-skill/SKILL.md) | Keep that skill and its feature map honest: source wave per feature, one live pass driving every feature, one PR of proven corrections. |
| [`create-formal-verification-skill`](Verification/create-formal-verification-skill/SKILL.md) | Prove an invariant where tests cannot reach, with the tool the question chooses, and leave it rerunnable. |
| [`maintain-formal-verification-skill`](Verification/maintain-formal-verification-skill/SKILL.md) | Stop a stale model from looking like a proof. Says which failures are drift and which are bugs. |

### Security

Review and security at AI speed. [`MAP`](Security/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`nexus-guard`](Security/nexus-guard/SKILL.md) | The last gate before production. Seven checks (secrets, dependency risk, boundaries, AI-code review, cost delta, observability, rollback) and a ships / doesn't-ship verdict with the failing line named. |
| [`ai-diff-review`](Security/ai-diff-review/SKILL.md) | Risk-tier an agent's diff 0 to 3 from its highest-risk hunk, apply the depth that tier earns, and hunt the eight failure modes specific to generated code. |
| [`llm-threat-model`](Security/llm-threat-model/SKILL.md) | The six surfaces an LLM feature adds: prompt injection direct and indirect, exfiltration, tool and agent abuse, output handling, cost abuse, refusal paths. |

### AIEngineering

LLM features in production. [`MAP`](AIEngineering/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`llm-evals`](AIEngineering/llm-evals/SKILL.md) | The set, the grader, and the CI gate. Validates the grader against human labels before trusting a number, and reruns everything on a model change. |
| [`inference-tuning`](AIEngineering/inference-tuning/SKILL.md) | Quality, latency and cost, with the knobs in order: caching, context, output, effort, model, then serving. One change at a time against the eval. |

### FinOps

Every design ships with its cost per request. [`MAP`](FinOps/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`cost-per-request`](FinOps/cost-per-request/SKILL.md) | Price a design before it ships: token split, cloud lines, the traffic assumption, and the levers in order from free to quality-trading. Judges cost per completed task, not per call. |
| [`cloud-cost-forecast`](FinOps/cloud-cost-forecast/SKILL.md) | Explain the bill across AWS, Azure, GCP and Oracle by decomposing the delta into price, quantity, mix and waste, then forecast as a range and rank the actions. |

### Platform

Orchestration and deployment. [`MAP`](Platform/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`deploy-pipeline`](Platform/deploy-pipeline/SKILL.md) | Cut the minutes and make deploys boring: measure per stage, build once and promote, the right gate in the right place, rollback in one rehearsed command. |
| [`iac-review`](Platform/iac-review/SKILL.md) | Review the plan, never the diff. Names every replacement and destroy, what it opens, the monthly delta, and what cannot be undone. |
| [`observability-baseline`](Platform/observability-baseline/SKILL.md) | Debuggable from production without a redeploy: structured logs with a trace id, rate / errors / duration / saturation, traces across boundaries, alerts on symptoms. |

### Communication

Understanding, being understood, and the register you do it in. [`MAP`](Communication/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`how`](Communication/how/SKILL.md) | How does X work, answered from the code in a subagent so the walkthrough never fills the main thread. |
| [`why`](Communication/why/SKILL.md) | Why is X this way, answered from the record. Marks inferences as inferences and treats a missing why as a finding. |
| [`heatmap`](Communication/heatmap/SKILL.md) | Snapshot how the app communicates, its trade-offs, and a high-level interaction graph into `.snapshots/NOV-19-5.16PM/`. The previous snapshot is the base; `git diff` updates the flow, and `insights.md` records what changed. |
| [`business-rules-heatmap`](Communication/business-rules-heatmap/SKILL.md) | Snapshot the most common business rules by repeated patterns — shared policies, copied comparisons, schema constraints, status transitions — into the same `.snapshots/` folders. The previous rules snapshot is the base; `git diff` updates the ranking, and `insights.md` records what changed. |
| [`teach`](Communication/teach/SKILL.md) | Runs `how` and `why` and weaves them into one plain account at the person's pace, building diagrams up one part at a time. |
| [`forever-learning`](Communication/forever-learning/SKILL.md) | Master a technology or process at senior depth: the mechanism, the invariant it maintains and what it costs, the tradeoff with the alternative named, the failure envelope, the misconception you still hold, and the transfer. **No basics, ever.** |
| [`feeling`](Communication/feeling/SKILL.md) | Name in one word what an artifact must make someone feel, and the feeling to avoid, then build it from mechanisms rather than adjectives. Checked by someone who never saw the intent. |
| [`enjoyable-talk`](Communication/enjoyable-talk/SKILL.md) | The working register: warm, light, specific, candid, where warmth never costs information. Includes feedback worth having, and the banned habits that make an assistant tiring. |
| [`bro`](Communication/bro/SKILL.md) | Say it again with no jargon. A translation, not a summary: every fact survives. |
| [`in-your-own-words`](Communication/in-your-own-words/SKILL.md) | Restate the goal, the problem, and your assumptions before acting, then proceed. |
| [`unslop`](Communication/unslop/SKILL.md) | Cut AI tells from English prose, including the engineering-specific ones: the unmeasured performance adjective, the status with no fact. |
| [`technical-writing`](Communication/technical-writing/SKILL.md) | Docs, RFCs, ADRs, runbooks, PR bodies and commits: pick the mode, write to the reader, leave no sentence open to two readings. |

### Meta

Skills about the skills. [`MAP`](Meta/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`monthly-skills-checkup`](Meta/monthly-skills-checkup/SKILL.md) | The monthly pass. Asks the target model, the depth and the rewrite appetite, scores every skill on six axes, rewrites what the new capabilities made weaker (starting with scaffolding a stronger model no longer needs), proposes the gaps, verifies, and logs the run. |
| [`arsenal-help`](Meta/arsenal-help/SKILL.md) | Route a task to the right skill, and say plainly when none fits. |
| [`setup-arsenal`](Meta/setup-arsenal/SKILL.md) | One file that sets the model and effort per role, overriding every skill default. Names what degrades at each budget. |
| [`correct`](Meta/correct/SKILL.md) | Make a repeated mistake impossible: architecture, then types, then a lint whose error names the fix, then a test, docs last. Proves each check fails on a real past mistake. |
| [`reflect`](Meta/reflect/SKILL.md) | Mine the session for durable learnings and route each to a concrete skill edit, with approval before editing. |
| [`automate-me`](Meta/automate-me/SKILL.md) | Turn how you work into a mode skill, from mined evidence plus a short structured interview. |

### Automations

Unattended work, which means the fences are the content. [`MAP`](Automations/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`setup-issue-bot`](Automations/setup-issue-bot/SKILL.md) | The config both issue automations read, the fences they hold, and the verification-skill prerequisite without which a repro is just a theory. |
| [`triage-issue-reports`](Automations/triage-issue-reports/SKILL.md) | One report in, one threaded verdict out: evidence before words, cause-aware routing, dedupe, fail-closed ticket creation. |
| [`reproduce-and-fix-issues`](Automations/reproduce-and-fix-issues/SKILL.md) | Reproduce against the real app, check whether it is already fixed, then a bounded draft PR with before-and-after proof. |
| [`webhook-trigger-ui`](Automations/webhook-trigger-ui/SKILL.md) | A page that wakes an agent or a workflow, with the secret server-side, an idempotency key per click, and nothing exposed publicly. |

### 3DModeling

[`MAP`](3DModeling/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`meshy-tripo-3d-pipeline`](3DModeling/meshy-tripo-3d-pipeline/SKILL.md) | AI 3D generation with Meshy and Tripo: input image prep, prompting, API workflow, inspection checklist, cleanup, scale and axis conventions, engine validation. |
| [`mixamo-auto-rig-mapper`](3DModeling/mixamo-auto-rig-mapper/SKILL.md) | Auto-rig humanoid meshes (Mixamo, Tripo, Meshy), choose the animation set, import and retarget in UE5 with IK Rig and IK Retargeter. |

### Audio

[`MAP`](Audio/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`ue-niagara-audio-trigger`](Audio/ue-niagara-audio-trigger/SKILL.md) | Unreal Engine 5 VFX and audio orchestration: tag-driven cues, Niagara parameter driving, MetaSound parameters, pooling, concurrency, networking and dedicated-server guards. |
| [`elevenlabs-sfx-generator`](Audio/elevenlabs-sfx-generator/SKILL.md) | AI sound effects: prompt structure, ElevenLabs parameters, trimming, loudness targets, layering and variation, engine hand-off. |
| [`bark-edge-tts-dialogue`](Audio/bark-edge-tts-dialogue/SKILL.md) | Character dialogue with Bark, Edge-TTS and XTTS: line writing, correct Bark tags, voice profiles, batching and caching, loudness, licensing. |
| [`ue-sfx-pipeline`](Audio/ue-sfx-pipeline/SKILL.md) | Take a raw sound file to something Unreal actually plays: WAV conversion, trimming dead air that delays the hit, mono downmix so it spatialises at all, SoundAttenuation and SoundConcurrency assets, and PlaySoundAtLocation with randomised pitch for self-destroying pickups. |

### Graphics2D

[`MAP`](Graphics2D/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`sprite-sheet-packer`](Graphics2D/sprite-sheet-packer/SKILL.md) | Pack frames into SubUV flipbooks or trimmed atlases: layout, padding, ImageMagick/Pillow/TexturePacker commands, Niagara SubUV setup, optimization. |

### Development

Code craft at the keyboard. [`MAP`](Development/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`state-machine-architect`](Development/state-machine-architect/SKILL.md) | Design and implement finite state machines in any language: when to use one, transition tables, hierarchical and parallel variants, async-safe TypeScript reference, anti-patterns, testing. |
| [`comment-psycho`](Development/comment-psycho/SKILL.md) | Ship features with zero comments: every fact a comment would carry is forced into a name or a type. The exemption list, the five moves that kill a comment, naming and typing laws per language, an adversarial reviewer pass, and a ships/doesn't-ship gate. |
| [`typescript-best-practices`](Development/typescript-best-practices/SKILL.md) | Make the compiler do the work: discriminated unions, branded primitives, boundary parsing, exhaustiveness, no `as`, no enums, and the React and Next.js specifics. |

### Videogames

35 skills, mostly Unreal Engine 5. The [`MAP`](Videogames/MAP.md) groups them by job.

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

[`MAP`](Narrative/MAP.md)

| Skill | Purpose |
|-------|---------|
| [`the-watcher`](Narrative/the-watcher/SKILL.md) | Turn the real record of a build into an epic, funny chronicle: mine git, the Claude Code session transcript, engine logs and timestamps into a dated timeline, stage it as acts where every chapter is a real obstacle with its real number, and close with what is honestly still unverified. |

## Install on a new machine

**Do not clone this into `~/.claude/skills`.** Skill loaders look for `<name>/SKILL.md` one level
under the skills root, and the categories here put every skill one level deeper. Clone the repo
wherever you keep projects, then generate the flat view and link it:

```bash
git clone git@codexmaker:CodeXMakerCompany/skills-arsenal.git
```

```bash
cd skills-arsenal && ./bin/skills.sh build && ./bin/skills.sh install
```

`build` writes `dist/skills/`, one link per skill, flat, validated. `install` points
`~/.claude/skills` at it, moving any existing directory aside to a timestamped backup first.
On Windows it uses directory junctions, which need no admin rights; elsewhere, symlinks.

```bash
./bin/skills.sh status
```

| Command | What it does |
|---------|--------------|
| `check` | Validates every `SKILL.md`: frontmatter present, `name` matches its directory, description non-empty, and no two skills share a name. Exits non-zero on any problem. |
| `build` | Runs `check`, then regenerates `dist/skills/` plus a `.manifest.tsv` of name, category and source path. |
| `install` | Points `~/.claude/skills` at `dist/skills`. Takes `--target DIR` for a project's `.claude/skills` or another agent's skill directory. |
| `status` | Repo count, dist count, and what is actually installed. Says when `dist/` is stale. |

Add `--dry-run` to `build` or `install` to see what would change.

**After editing a skill**, nothing to do: the links point at the real directories, so edits are live
immediately. **After adding, renaming, or deleting one**, rerun `./bin/skills.sh build`.

`dist/` is generated and gitignored. The categorized tree is the only source of truth.

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


