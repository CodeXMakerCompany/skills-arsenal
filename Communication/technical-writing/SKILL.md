---
name: technical-writing
description: Layered technical-writing standard: Diátaxis structure, Google developer style sentences, simplified-English instruction rules, unambiguous syntax. Use for /technical-writing or when writing or reviewing docs, RFCs, READMEs, ADRs, runbooks, PR descriptions, or commit messages.
---

# Technical writing

Write so a tired engineer understands on the first read.

- Cut every word that does no work.
- Use the short, everyday word: "use", not "utilize".
- When a rule makes a sentence worse, fix the sentence another way or leave it alone.
- Write the real symbol, file, flag, or command name, never a synonym or a description of it.
- Do not invent jargon. Use the words a developer would say out loud, and define a named pattern the first time you use it.

## Vary the rhythm

- Mix sentence lengths. Split the sentence that carries two thoughts. Keep the long sentence that carries one.
- Have a view in explanation. Keep reference dry.
- Be specific. Not "schema changes can cause issues" but "renaming a column fails the build".

## Pick the mode first

One document, one mode. Do not mix them. Split and link instead.

- **Tutorial: learning by doing.** Say what the reader will build. Every step produces a visible result, and you say what they should see. Explanation gets one clause and a link.
- **How-to: steps to a goal.** Solve the reader's problem, assume competence, action only. Forks are allowed. Name the guide by the task.
- **Reference: facts for lookup.** Only describe. Dry, complete, certain. Mirror the structure of the thing described.
- **Explanation: understanding and why.** One bounded topic. Design decisions, history, constraints, alternatives. Opinion belongs here and nowhere else.

An ADR is explanation with a decision at the top: context, the options weighed, the decision, the consequences you accept. A runbook is a how-to written for someone at 3am, so it names the dashboard, the command, and the rollback, and it assumes nothing about what they remember.

## Write sentences to the reader

- Talk to the reader as "you", in the present tense.
- Say who does what. Passive is fine only when the actor is unknown or beside the point.
- Write instructions as commands. Put the condition before the instruction, and the common case first.
- No buzzwords, no figurative language, no "please", and never "simply", "easy", or "quickly" in a procedure.
- Do not pre-announce, and do not start consecutive sentences with the same phrase.
- Link with words that say where the link goes.
- Headings carry the point, in sentence case. One h1 per page, no skipped levels.
- Numbered lists for sequences, bullets for everything else. Introduce a list with a complete sentence and keep the items parallel.
- Code in code font, UI elements in bold, serial commas, and no "etc.".

## Make statements load one at a time

- One instruction per sentence. One thought per sentence everywhere else.
- Split instructions longer than about 20 words, and other sentences longer than about 25.
- Put the warning or condition before the step it guards.
- Keep "the" and "a".
- Give each word one meaning, and pick one word per action.
- Write procedures as direct commands, never as narration and never in the passive.

## Leave no sentence open to two readings

- Keep "only" and "not" next to the word they change.
- Break up long noun strings.
- Make every "it", "they", and "this" point at one obvious thing. Never use "this" or "which" to point at a whole clause.
- Do not drop verbs, or the small words that show structure, such as "that".
- Say which parts "and" or "or" joins.
- Use periods, not semicolons or dashes. No slashes, no "(s)". Text in parentheses is a full grammatical unit.
- Call each thing by one name, everywhere.
- Skip idioms, Latin abbreviations, and metaphors. A reader whose first language is not English pays for every one of them.

## Voice and repo specifics

- Apply **unslop** to every document this skill touches. That skill owns the slop catalog: AI vocabulary, filler, hedging, formatting tells.
- **PR descriptions and commit messages are writing too.** Every layer except the mode section applies. A PR body is a briefing a reviewer reads in under a minute, so never paste agent logs, SHA lists, or metric tables into it. Link them.
- A commit subject is imperative, under 72 characters, and says what changes for the user. The body carries the why.
- Product UI strings are not documentation. Use the product's copy guidelines for those.
- Write real paths. Make every count or tree claim true at the commit that lands it, and include the command that regenerates it.
