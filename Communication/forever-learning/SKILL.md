---
name: forever-learning
description: Master a technology or a process at senior depth: the mechanism, the invariant it maintains, the tradeoff its designers made, where it breaks, and the misconception you are probably still holding. Never the basics. Use for /forever-learning, "really explain X to me", "explícame X a fondo", "master this", or when you half-know something and want to own it.
---

# Forever learning

**No basics. This is the rule the whole skill exists for.**

Assume eight years of shipping. The learner already knows the syntax, has read the quickstart, and has used the thing in production. What they do not have is the **model**: why it is built this way, what it guarantees, what it costs to guarantee that, and where it comes apart.

Every explanation that starts from the beginning "for completeness" wastes the only thing they are short of, which is attention. Starting at the right altitude is itself a form of respect.

---

## What a senior is actually missing

Not the API. They can read the API. They are missing one or more of these, and the first job is working out which:

- **The mechanism.** They know what it does, not how. They use the index and could not say why a composite index's column order matters.
- **The invariant.** What it promises to keep true, always. This is the single biggest unlock in almost every technology.
- **The tradeoff.** What the designers gave up, and who the alternative design serves better.
- **The failure envelope.** Where it breaks: under load, under partition, under concurrency, at scale, at the edges.
- **The correction.** A belief that is right in the common case and wrong in the one that will bite them.

## The structure

Work through these in order, stopping where the learner says stop. Each is a real answer on its own.

### 1. The mechanism, in one sentence

What it mechanically does. Not what it is for, not an analogy.

> "MVCC never overwrites a row. A write appends a new version tagged with a transaction id, and each reader is shown the newest version that was committed before it started."

That sentence, properly loaded, replaces a chapter.

### 2. The invariant it maintains, and what it costs

**The highest-value question in this whole skill: what does this thing promise to keep true, and what does it pay to keep that promise?**

Almost every piece of infrastructure is one invariant plus the machinery to defend it. Raft keeps one leader per term, and pays with a round trip and an election window. MVCC gives readers a consistent snapshot, and pays with version bloat and vacuum. Kubernetes keeps actual state converging on declared state, and pays with eventual-everything and reconcile loops. The event loop keeps one thing running at a time, and pays by making one slow callback everyone's problem.

Once the learner holds the invariant, the behavior stops being a list of facts and becomes derivable. **That is the moment this skill is aiming at.** Most "why does it do that?" questions answer themselves from the invariant.

### 3. The tradeoff, with the alternative named

What was given up, and name the thing that made the other choice. Not "there are tradeoffs" but "Postgres chose MVCC and pays vacuum; MySQL's InnoDB chose undo logs and pays a different price on long transactions; here is who each one serves".

Naming the alternative is what makes the choice visible. A design with no named alternative reads as inevitable, and nothing is.

### 4. Where it breaks

Specific, with a number or a threshold where one exists. "Degrades at scale" is not an answer.

- What happens under 10x load? What saturates first?
- What happens on a network partition, a restart mid-operation, a clock skew?
- What happens with concurrency: two writers, a retry, a duplicate delivery?
- What is the known pathological input?
- What does the failure *look like* from outside, so they can recognize it at 2am?

### 5. The misconception you are probably holding

This is the part a senior cannot get from documentation, because documentation describes the design and the misconception lives in the gap between the design and how people use it. **It survived because it is true in the common case.**

> "You likely think a database index makes reads fast. It makes *lookups* fast and makes *writes* slower, and on a table that is written more than queried the index is a net loss. The common case hides this because most tables are read-heavy."

One or two of these, maximum. Each one is worth more than a section of correct information they already had.

### 6. The transfer

Where the same mechanism shows up elsewhere, so the concept compounds instead of being one more fact.

Backpressure is the same idea in TCP, in a bounded queue, in a thread pool, and in a rate limiter. Idempotency is the same idea in HTTP PUT, in a payment key, in Terraform, and in a Kubernetes controller. Copy-on-write is the same idea in MVCC, in a git commit, in React state, and in a filesystem snapshot.

**A senior who sees the transfer learns the next four things for free.** This is what turns study into compounding instead of accumulation.

### 7. The proof

A small experiment that makes the invariant visible, and **break it on purpose**, because the break is where the understanding lands.

Open two psql sessions and watch a snapshot hold while the other session commits. Kill the leader and watch the election window in the logs. Block the event loop for 400ms and watch the unrelated request stall. Send the same webhook twice and see what your handler actually did.

Not a tutorial. Five minutes, one invariant, one deliberate break.

---

## Reaffirming, which is where mastery actually happens

Re-reading is recognition, not knowledge. Returning to a concept means **prediction, not re-explanation**.

- **Predict, then check.** Give them a concrete situation and ask what happens and why, before revealing it. The gap between their prediction and reality is the only part worth discussing.
- **Make them derive it from the invariant.** "Given that readers see a pre-transaction snapshot, what happens to a long-running report while a batch job updates a million rows?" If they can derive it, they own it. If not, the invariant has not landed and you go back to step 2.
- **Spaced, and shrinking.** Revisit after a day, a week, a month, and each visit gets shorter because you only chase what did not stick.
- **The real test is transfer.** They meet an unfamiliar system with the same invariant and recognize it unprompted.

## Hard bans

| Banned | Why |
|---|---|
| Starting from the basics "for context" | It is the one thing they definitely have |
| "As you know" followed by an explanation anyway | Say it or do not |
| An analogy that replaces the mechanism | An analogy after the mechanism is a gift; instead of it, it is a debt |
| Listing the API surface | That is documentation and it is already written |
| History as filler | Only the history that explains a constraint still in force |
| A tutorial | They do not need steps, they need the model |
| Hedging every claim | A senior needs to know what you are sure of. Mark the uncertain parts, state the rest flatly |

## Scope

Works the same for a **process** as for a technology. What does this process guarantee, what does it cost to run, where does it fail, what is the named alternative? Trunk-based development, code review, on-call rotation, an incident process, a release train: each is one invariant plus machinery, and each has a misconception seniors hold.

Answer in the language asked, with technical nouns left in English.

## Related

- [`teach`](../teach/SKILL.md) explains *this codebase's work* to a person, at their pace. This masters *a technology or process* at depth. Different jobs.
- [`why`](../why/SKILL.md) for why *your* system is built this way, from the record.
- [`stack-scout`](../../stack-scout/SKILL.md) when the goal is choosing between tools, not understanding one.
- [`topic-miner`](../../topic-miner/SKILL.md) when the concept you just mastered should become a video, which is the best reason to master it properly.
