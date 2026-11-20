# Arsenal map

How to travel through 132 skills without reading them. Start here, drop into a category's `MAP.md`, stop at the leaf.

Three other doors. [`COMBOS.md`](COMBOS.md) has the small sets that work well together, which is what you want most days. [`SKILL-SELECTOR.md`](SKILL-SELECTOR.md) is for extracting a subset into a project. The [`arsenal-help`](Meta/arsenal-help/SKILL.md) skill is this map with reasoning attached, for when a task could land in three places.

---

## The one-line version

**Nothing starts without [`clarity`](Agentic/clarity/SKILL.md), everything non-trivial runs under [`codex-mode`](Agentic/codex-mode/SKILL.md), and nothing ships without [`nexus-guard`](Security/nexus-guard/SKILL.md).** Those three are the bookends and the spine. The playbooks pull in the rest.

---

## The graph

```
                        Agentic/clarity
                  (requirements clear, or stop)
                               |
                        Agentic/codex-mode
                     (the operating style)
                               |
         +---------------------+---------------------+
         |                     |                     |
   understand            decide & build          prove & ship
         |                     |                     |
  Communication            Agentic                Verification
   how  why  heatmap     architect  arena           interrogate
   teach  bro            swarm  figure-it-out       blast-radius
   forever-learning      sharpen  recall            tdd  statechart
   feeling               ketchup                    benchmark-checklist
   enjoyable-talk        show-me-your-work          create/maintain-*
   unslop  in-your-own-words
   technical-writing
   business-rules-heatmap
         |                     |                     |
         +----------+----------+----------+----------+
                    |                     |
               Development            Security
            comment-psycho          ai-diff-review
            typescript-*            nexus-guard  <-- the gate
            state-machine-*         llm-threat-model
                    |                     |
            under Principles/ (24)         |
                                           v
                              AIEngineering   FinOps   Platform
                               llm-evals    cost-per-   deploy-pipeline
                               inference-     request   iac-review
                                tuning      cloud-cost- observability-
                                            forecast     baseline

   Meta/            arsenal-help  setup-arsenal  correct  reflect
                    automate-me   monthly-skills-checkup
   Automations/     setup-issue-bot  triage-issue-reports
                    reproduce-and-fix-issues  webhook-trigger-ui
   Content (root)   topic-miner  stack-scout  anti-slop  demo-video
                    script-qa  script-stakeholder  notebook-cast
                    audio-clone  exam-dumps  aws-log-insights
   Game dev         Videogames/ (35)  3DModeling/ (2)  Audio/ (4)
                    Graphics2D/ (1)  Narrative/ (1)
```

---

## Route by the shape of the work

| The work is | Go to | Leaf to open first |
|---|---|---|
| A ticket, spec or request just arrived | [`Agentic`](Agentic/MAP.md) | `clarity`, before anything else |
| Anything non-trivial, run properly | [`Agentic`](Agentic/MAP.md) | `codex-mode`, then its playbook |
| Understanding code that exists | [`Communication`](Communication/MAP.md) | `how` for mechanism, `why` for rationale |
| Understanding a whole unfamiliar repo | [`Communication`](Communication/MAP.md) | `heatmap`, the dated communication graph in `.snapshots/` |
| Which rules the app enforces over and over | [`Communication`](Communication/MAP.md) | `business-rules-heatmap` |
| Explaining it to a person | [`Communication`](Communication/MAP.md) | `teach`, or `bro` to translate |
| Mastering a technology at senior depth | [`Communication`](Communication/MAP.md) | `forever-learning`. No basics |
| Deciding what an artifact should make someone feel | [`Communication`](Communication/MAP.md) | `feeling`, before you build it |
| How to talk, and how to give real feedback | [`Communication`](Communication/MAP.md) | `enjoyable-talk` |
| Deciding a shape before code | [`Agentic`](Agentic/MAP.md) | `architect`, `arena` if contested |
| Creating or fixing a Kiro custom agent | [`Agentic`](Agentic/MAP.md) | `kiro-agent-creator` |
| Writing or changing code | [`Development`](Development/MAP.md) | `typescript-best-practices`, `comment-psycho` |
| The rule behind a judgment call | [`Principles`](Principles/MAP.md) | the 24 leaves, cited by name |
| Proving it works, or breaking it | [`Verification`](Verification/MAP.md) | `interrogate`, `blast-radius`, `tdd` |
| Reviewing an agent's diff | [`Security`](Security/MAP.md) | `ai-diff-review` |
| The last gate before production | [`Security`](Security/MAP.md) | `nexus-guard` |
| An LLM feature going live | [`AIEngineering`](AIEngineering/MAP.md) + [`Security`](Security/MAP.md) | `llm-evals`, `llm-threat-model` |
| What something costs | [`FinOps`](FinOps/MAP.md) | `cost-per-request` |
| Pipelines, infra, deploys, telemetry | [`Platform`](Platform/MAP.md) | `deploy-pipeline`, `iac-review`, `observability-baseline` |
| A recurring job that runs itself | [`Automations`](Automations/MAP.md) | `setup-issue-bot` |
| The arsenal itself | [`Meta`](Meta/MAP.md) | `arsenal-help`, `monthly-skills-checkup` |
| Video, scripts, narration, research | root skills, below | `topic-miner`, `demo-video`, `anti-slop` |
| Unreal, 3D, sprites, game audio | [`Videogames`](Videogames/MAP.md) and siblings | per that map |

---

## The categories

| Category | Count | What it owns | Its map |
|---|---|---|---|
| `Agentic` | 11 | How work gets run: the mode, playbooks, parallelism, memory, the requirements gate, and Kiro agents | [MAP](Agentic/MAP.md) |
| `Principles` | 24 | The rules the mode cites. Leaves, not workflows | [MAP](Principles/MAP.md) |
| `Verification` | 9 | Proof: adversarial review, blast radius, tests, model checking | [MAP](Verification/MAP.md) |
| `Development` | 3 | Code craft at the keyboard | [MAP](Development/MAP.md) |
| `Security` | 3 | Review at AI speed, the LLM attack surface, the production gate | [MAP](Security/MAP.md) |
| `AIEngineering` | 2 | LLM features in production: evals, inference tuning | [MAP](AIEngineering/MAP.md) |
| `FinOps` | 2 | Cost per request, and the bill it rolls up into | [MAP](FinOps/MAP.md) |
| `Platform` | 3 | Pipelines, infrastructure, observability | [MAP](Platform/MAP.md) |
| `Communication` | 12 | Understanding, being understood, and the register you do it in | [MAP](Communication/MAP.md) |
| `Meta` | 6 | Skills about the skills | [MAP](Meta/MAP.md) |
| `Automations` | 4 | Unattended work with fences | [MAP](Automations/MAP.md) |
| `Videogames` | 35 | Unreal Engine, 3D and 2D | [MAP](Videogames/MAP.md) |
| `Audio` | 4 | Game audio and generated speech | [MAP](Audio/MAP.md) |
| `3DModeling` | 2 | Generated assets and rigging | [MAP](3DModeling/MAP.md) |
| `Graphics2D` | 1 | Sprite sheets and atlases | [MAP](Graphics2D/MAP.md) |
| `Narrative` | 1 | Turning a real build into a story | [MAP](Narrative/MAP.md) |
| root | 10 | The content pipeline and personal tooling | below |

### The root skills

They live at the repo root rather than in a category, deliberately: several are extracted into projects by path, and moving them would break those extractions. They group into two sets.

**Content pipeline** (Spanish short-form, faceless technical creator): [`topic-miner`](topic-miner/SKILL.md) finds topics, [`stack-scout`](stack-scout/SKILL.md) compares tools, [`script-qa`](script-qa/SKILL.md) and [`script-stakeholder`](script-stakeholder/SKILL.md) storyboard by audience, [`demo-video`](demo-video/SKILL.md) renders, [`anti-slop`](anti-slop/SKILL.md) is the last gate, [`audio-clone`](audio-clone/SKILL.md) narrates, [`notebook-cast`](notebook-cast/SKILL.md) makes study artifacts.

**Personal tooling:** [`aws-log-insights`](aws-log-insights/SKILL.md) for forensic RCA on AWS logs, [`exam-dumps`](exam-dumps/SKILL.md) for the certification scraper.

---

## The three spines

Most real tasks are a walk along one of these. Learn these and the map stops being necessary. [`COMBOS.md`](COMBOS.md) has the shorter everyday sets.

**Build something.** `clarity` → `codex-mode` → `feature` playbook → `architect` → `cost-per-request` → implement under `Principles` → `comment-psycho` → `ai-diff-review` → `nexus-guard` → `opening-a-pr`.

**Fix something.** `codex-mode` → `bug-fix` playbook → `aws-log-insights` or `how` → `tdd` → fix → `blast-radius` → `nexus-guard` → `correct` so it cannot happen again.

**Ship an AI feature.** `architect` → `inference-tuning` → `llm-evals` → `llm-threat-model` → `cost-per-request` → `observability-baseline` → `nexus-guard`.

---

## Rules of travel

- **One leaf owns the deliverable.** The rest gate it. A tie means you have not named the deliverable yet.
- **Prefer the narrower skill.** `tdd` beats `figure-it-out` for a bug with an obvious test. Reaching for `figure-it-out` first turns a 20-minute task into a phased program.
- **Principles are cited, not run.** A principle changes a decision inside another skill's work. Name the principle and the choice it changed.
- **A gate is not optional because the change is small.** It is optional because the check does not apply, and then you say which and why.
- **No skill fits, sometimes.** Say so, do the task, and record the gap for `monthly-skills-checkup`. Do not stretch a description to cover something it does not do.
