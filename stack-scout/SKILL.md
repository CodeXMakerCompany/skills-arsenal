---
name: stack-scout
description: Scout the market for tools matching a need or a painpoint, compare real total cost at your scale, and decide build vs buy. If no tool fits, produce a sequenced implementation strategy. Use when asked to find/compare tools or vendors, "qué herramienta uso para", "build vs buy", evaluating a category (LLM security, observability, auth, queues), pricing comparisons, or when the user describes a technical painpoint and wants options.
---

# Stack Scout

Find what to buy, prove what it costs, or decide to build.

Three rules that separate this from a "top 10 tools" listicle:

1. **A comparison without scale is meaningless.** "Best" at 10k req/día and at 10M req/día
   are different products. Establish volume first or the whole analysis is noise.
2. **Sticker price is not cost.** Latency tax, integration weeks, the enterprise-tier
   cliff, and exit cost usually dominate the line item.
3. **"Nothing fits" is a valid, common outcome** — and it does *not* mean "build it from
   scratch." See [Build strategy](#build-strategy).

---

## Input modes

**Keyword:** *"security layer for LLMs, empresa grande"* → go to Step 2.

**Painpoint:** *"nuestro LLM está filtrando datos de clientes"* → **Step 1 first.**
Never search a painpoint literally. It maps to several categories with completely
different markets, and searching the raw complaint lands you in whichever one won SEO.

---

## Step 0 — Establish constraints (blocking)

Do not search until these are known. Ask if missing; assume and **state the assumption
loudly** if the user wants to move fast.

| Constraint | Why it decides the answer |
|---|---|
| **Volume** | req/day, tokens/month, seats. Flips per-request vs flat pricing. |
| **Latency budget** | Inline tools tax *every* request. A 300ms guardrail may be unshippable. |
| **Deployment** | SaaS OK? VPC? On-prem? Air-gapped? Kills most of the market instantly. |
| **Compliance** | SOC2 Type II, ISO 27001, HIPAA, GDPR, data residency. |
| **Team size** | Self-hosted OSS with no platform team is a trap. |
| **Timeline** | Buy wins on weeks. Build wins on quarters. |

---

## Step 1 — Painpoint → requirement decomposition

Break the complaint into *mechanisms*. Each maps to a different category.

> *"El LLM filtra datos de clientes"* decomposes to:
> - PII entering the prompt → **input redaction**
> - PII in the output → **output filtering**
> - Data leaking to the vendor → **gateway / proxy / zero-retention terms**
> - Data baked into weights → **training data governance** (no tool fixes this post-hoc)
> - User A seeing user B's data → **retrieval authz** (a RAG bug, not a security product)

State which mechanism(s) actually apply before searching. Frequently the painpoint is
an **architecture bug, not a missing product** — say so and stop. That's the single
most valuable output this skill produces.

---

## Step 2 — Map the category

Name the category before naming vendors. Vague asks hide several distinct markets.

> *"Security layer for LLMs"* is not one category:
> guardrails/content filtering · prompt-injection detection · PII redaction ·
> AI gateway/proxy · model access governance · output validation · red-teaming/eval ·
> agent permission sandboxing

Ask which. If the user needs 3+ of these, that is itself the finding: no single
vendor covers it, and the real work is the orchestration layer.

---

## Step 3 — Enterprise gate (run EARLY)

For "big business", apply before evaluating features. It eliminates most of the market
in one pass, and evaluating features first wastes the whole analysis.

Hard filters: SOC2 Type II · data residency · SSO/SAML + SCIM · audit logs ·
DPA/subprocessor list · contractual SLA · VPC or on-prem option · zero-retention terms.

**The SSO tax:** SSO, audit logs, and SCIM are routinely gated behind "contact sales."
Assume the real enterprise price is **3–10x the published tier** until proven otherwise.

---

## Step 4 — Find candidates

Source rules, in priority order:

1. **Vendor pricing page and docs** — the only acceptable source for a price or a limit.
2. **Changelogs, status pages, security pages** — reveal maturity and incident history.
3. **Practitioner reports** — HN/Reddit threads from people running it in production.
   Mine the complaints, not the headline.
4. **Never trust** "top 10 tools" roundups, comparison-site pricing tables, or
   affiliate reviews. **These are systematically stale and wrong.**

> Verified failure mode: three LLM-pricing aggregators reported a Claude Sonnet 5 price
> increase that the vendor docs said was cancelled. **Always confirm price against the
> vendor's own page.** If you cannot verify a price, mark it `NO VERIFICADO` — never
> present it as fact.

Always include **at least one OSS option** and **one "do nothing / build the seam"**
option. A comparison of only commercial vendors is a rigged comparison.

---

## Step 5 — Real cost model

Compute at the user's stated volume. Show the arithmetic.

| Cost line | What to look for |
|---|---|
| **Sticker** | per seat / request / token / GB. Note the pricing *axis* — it decides how you scale. |
| **Latency tax** | added p50 and **p99** per request. For inline tools this is the dominant cost. |
| **Enterprise cliff** | what's gated behind sales. Assume 3–10x. |
| **Integration** | eng-weeks to first production traffic. |
| **Ops** | for self-hosted: who pages at 3am? |
| **Egress / data transfer** | cross-cloud is where budgets die quietly. |
| **Exit cost** | proprietary formats, no export API, rewritten call sites. |

**Latency deserves its own row, not a footnote.** A guardrail adding 200ms to every LLM
call may be more expensive in conversion than its entire license fee.

---

## Step 6 — Build vs buy rubric

| Signal | Verdict |
|---|---|
| Capability is your differentiation | **Build** |
| Commodity, well-served, mature market | **Buy** |
| Data cannot leave your perimeter | **Self-host or build** |
| Category <2 years old, no clear leader, high churn | **Build the seam, defer** |
| Requires 3+ vendors to cover | **Buy the pieces, build the orchestration** |
| Compliance needs an accountable third party | **Buy** (you're buying liability transfer) |
| Team has no platform/on-call capacity | **Buy**, even at a premium |

Be explicit when the honest answer is "buy the boring one and move on." Not every
decision deserves a build.

---

## Build strategy

<a id="build-strategy"></a>
When nothing fits. **Never propose building the whole system.**

### 1. Build the seam, not the system

Define the interface now. Put the cheapest thing behind it. Swap later without
touching call sites. This converts an irreversible decision into a reversible one,
and it's almost always the correct first move in an immature category.

```
Your app → [YourGuardrail interface] → regex/deny-list (hoy)
                                     → vendor X (si escala)
                                     → modelo propio (si se vuelve core)
```

### 2. Take the deterministic 80% first

Regex, deny-lists, schema validation, and allow-lists catch a large share of cases at
near-zero latency and cost. Reach for an ML classifier only for what survives. Most
teams buy the expensive thing to solve a problem `re.match` handles.

### 3. Name what has no OSS equivalent

That gap is your actual build cost. Everything else is integration work. If the gap
is small, build. If it's a research problem, buy or descope.

### 4. Sequence by risk reduction per week

Order the work by how much risk each step removes, not by architectural elegance.
Ship the ugly mitigation this week; the clean design survives contact with reality
better afterward.

### 5. Define the trigger to revisit

"Rebuild the decision when we exceed X req/s, or when a vendor ships Y." A build
decision without a revisit trigger becomes permanent by accident.

---

## Vendor red flags

- Pricing not public → expensive, negotiated, and slow to procure
- No published latency numbers → they're bad
- No VPC/on-prem option when you have residency requirements → non-starter, stop here
- <18 months old in a category where failure is catastrophic
- No status page or incident history → no operational maturity
- **For any inline security/observability vendor: they see all your prompts and data.**
  A tool bought to reduce data risk that becomes your largest data-sharing relationship
  is a net loss. Check retention and training terms explicitly.

---

## Output

Spanish. Technical terms stay in English (`latency`, `deployment`, `self-hosted`,
`guardrails`) — never translate them.

1. **El problema real** — 2 líneas. Restate the requirement after decomposition. Flag
   if it's an architecture bug rather than a purchasing problem.
2. **Supuestos** — volume, latency budget, deployment, compliance. Mark assumed values.
3. **Categoría(s)** — what market this actually is.
4. **Shortlist** — 3–5 max, incl. one OSS and one build option:

| Opción | Deployment | Precio (fuente) | Latency | Enterprise gate | Riesgo |
|---|---|---|---|---|---|

5. **Costo a tu escala** — arithmetic, per option, at stated volume.
6. **Veredicto** — one recommendation with the load-bearing reason. Not a menu.
7. **Si es build** — the sequenced strategy above, with the revisit trigger.
8. **Qué verificar antes de firmar** — the questions only their sales team can answer.

Mark every unverified price `NO VERIFICADO`. Cite the vendor page for every number.

---

## Pipeline handoff

A build-vs-buy analysis is strong content. When one produces a genuinely surprising
finding — a pricing cliff, a latency number nobody publishes, a category that
shouldn't exist — hand it to `topic-miner` as a topic with the *La cuenta* or
*Qué NO arregla* angle. The research is already done; the receipt is the hook.
