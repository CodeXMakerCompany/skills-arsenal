---
name: topic-miner
description: Mine recent AI news for short-form technical video topics with a senior engineering angle. Use when the user asks for content ideas, video topics, "what should I post about", "qué grabo", mining AI news, or refilling the content pipeline. Outputs scored topics in Spanish for a faceless technical creator.
---

# Topic Miner

Turn recent AI news into short-form video topics that a **senior** engineer would stop scrolling for.

The news is never the content. The news is the **hook**. The content is the second-order
technical implication that nobody else is covering.

> "OpenAI shipped a 1M context window" → news, anyone can report it.
> "Why 1M context doesn't fix your RAG, and what actually breaks at that scale" → the content.

If a topic's only possible take is *"this is cool"* or *"this changes everything"*, **discard it.**

---

## Creator profile (filter everything through this)

- **Background:** AI SWE — backend, frontend, architecture, cloud. Ships production systems.
- **Format:** faceless vertical short-form (30–60s), synthetic voice, code on screen.
- **Audience:** Spanish-speaking working engineers (LatAm/Mexico-weighted). Mid-to-senior.
- **Positioning wedge:** where AI-generated code and AI tooling break in *real production systems*.

**Credibility filter:** only mine news he can speak to from experience. Coding agents, API/pricing
changes, context and inference behavior, agent frameworks, devtool releases, architecture
implications → strong. Image/video model benchmarks, funding rounds, org drama → skip.

---

## Language rules

All **output** in Spanish. These files stay in English.

- **Never translate technical terms.** Spanish syntax, English technical nouns.
  - Correct: *"el context window"*, *"hacer un rollback"*, *"el deployment se cayó"*, *"un commit"*
  - Wrong: *"ventana de contexto"*, *"aprendizaje profundo"*, *"despliegue"*
- Register: neutral Mexican, spoken not written. How you'd explain it to a colleague at lunch.
- No corporate Spanish. No *"En el mundo actual de la tecnología..."*.
- Voseo/tuteo: **tú**, never *vosotros*.

---

## Freshness

AI news decays fast. Peak window for short-form is ~72 hours.

| Age | Verdict |
|---|---|
| 0–3 days | Prime. Mine aggressively. |
| 4–10 days | Usable only with a genuine technical angle, not a recap. |
| >10 days | Dead — **unless** the angle is *"everyone got this wrong"* retrospective. |

Always check today's date before mining. Never present stale news as new.

---

## Source tiers

Search with WebSearch/WebFetch. Prefer primary sources — that's where the technical
detail that makes senior content lives.

1. **Tier 1 (primary):** model cards, release notes, changelogs, pricing pages, official
   docs, arXiv papers, RFCs, GitHub releases and issue threads.
2. **Tier 2:** vendor engineering blogs, maintainer posts.
3. **Tier 3:** tech press, HN/Reddit *discussion* (mine the disagreement in comments, not the headline).
4. **Never:** listicles, "top 10 AI tools", influencer takes, engagement-farm threads.

**The best raw material is Tier 1 detail + Tier 3 disagreement.** The spec says what changed;
the thread says who it broke.

---

## Process

1. Check today's date.
2. Search 4–6 queries across the credibility zone (coding agents, model/API releases,
   pricing and inference changes, agent tooling, notable outages or regressions).
3. For each candidate, pull the **primary source** and find one concrete technical detail:
   a number, a limit, a breaking change, a default that changed, a deprecation.
4. Generate 2–3 angles per item using the taxonomy below.
5. Score. Drop anything under 3/5 on Depth.
6. Return the top 5–8 as a table.

---

## Angle taxonomy

The engine of this skill. For each news item, ask which of these applies:

| Angle | Question it answers |
|---|---|
| **La cuenta** | What does this actually cost at scale? Tokens, latency, egress, seats. |
| **La autopsia** | Why does the demo work and prod break? |
| **Qué mata** | What tool, pattern, or job just became obsolete? |
| **Qué NO arregla** | The hype claim vs. the limitation still standing. |
| **El costo de migrar** | Sounds great — what does adopting it actually cost you? |
| **Segundo orden** | What breaks downstream that nobody is talking about? |
| **El recibo** | I tested it. Here's the number. |
| **La contraria** | Everyone's excited — here's the load-bearing reason they're wrong. |

*Qué NO arregla*, *Segundo orden*, and *La cuenta* consistently produce the most
senior-sounding content. Reach for those first.

---

## Scoring

Score each 1–5. Kill anything with **Depth < 3** — no exceptions.

- **Depth** — is there a real technical claim with a number, limit, or mechanism behind it?
- **Controversy** — will engineers argue in the comments? (drives reach on this niche)
- **Credibility** — can *he* speak to this from having shipped it?
- **Saturation** — inverted: 5 = nobody's covering it, 1 = everyone is.
- **Decay** — how long does this stay relevant? Higher = more evergreen.

---

## Reject filters

Discard immediately if:

- The take reduces to "this is cool" / "esto lo cambia todo".
- It requires speculating about unreleased products.
- The claim can't be verified against a primary source.
- It's a funding round, a hire, a resignation, or org drama.
- The only content available is a feature recap the vendor already published.
- A junior with no production experience could have written the same take.

---

## Output

Return a Spanish table, ranked:

| # | Tema | Ángulo | Dato técnico (el gancho) | Fuente | D/C/Cr/S | Notas |
|---|------|--------|--------------------------|--------|----------|-------|

Then, for the **top 3 only**, add two lines each:
- **La tensión:** the conflict in one sentence — what people believe vs. what's true.
- **La prueba:** the specific number, limit, or repro that backs it up.

Do not write the script. That's `short-script`. Stop at the angle and the proof.

---

## Pipeline handoff

Topics feed the Airtable **Topics** table (fields: `idea`, `source`, `angle`,
`controversy`, `status`, → `Scars`, → `Series`). If Airtable tools are available and
the user asks to save, write rows with `status = raw`. Otherwise return the table
and let the user paste.

Link a topic to an existing **Scar** whenever the news echoes something he has
personally lived — those become the strongest videos, because the news gives the
timeliness and the scar gives the authority.
