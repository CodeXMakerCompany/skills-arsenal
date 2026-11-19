---
name: unslop
description: Cut AI tells from any writing in English: docs, PR bodies, commit messages, reports, replies. Use for /unslop, "unslop this", "clean this up", or before any prose leaves the session. For Spanish video scripts use anti-slop instead.
---

# Unslop

Edit text to remove AI patterns. Scan for the patterns below, then rewrite. Preserve the meaning and match the intended tone.

Rule numbers are stable ids that other skills cite. A removed rule leaves a gap.

3. No trailing "-ing" phrases that add no fact ("highlighting...", "ensuring...").
5. No vague attributions ("experts believe", "studies show"). Name the source or delete the claim.
7. No AI vocabulary: additionally, crucial, delve, enhance, foster, landscape, pivotal, robust, seamless, showcase, testament, underscore, vibrant.
8. Say "is" or "has", not "serves as", "stands as", "boasts", "features".
9. No "not just X, but Y". State the point.
10. Do not force ideas into threes.
11. One name per thing. Repeat it.
12. No "from X to Y" unless X and Y sit on a real scale.
13. No em dashes, en dashes, or hyphens used as dashes, and no parentheses in their place. Use a period or a comma.
14. A colon goes before a list or an example, never mid-sentence as a connector.
15. Do not bold every proper noun or acronym.
16. No bold label and colon that restates its line ("**Performance:** Performance improved..."). A bold lead-in that ends in a period and adds new detail is fine.
17. Sentence case headings.
18. No decorative emojis.
19. Straight quotes.
20. No chatbot phrases ("I hope this helps", "Let me know if...").
22. No praise or agreement openers. Respond directly.
23. Cut filler. "In order to" becomes "to". Delete "it is important to note that".
24. One hedge at most, and prefer "may".
25. No generic conclusions. State a specific plan or fact.
26. No abstract metaphor nouns: substrate, wedge, vector, nexus, primitive, harness, surface, scaffolding, paradigm, ratchet, north star, flywheel. Use the concrete word.
27. Say what it does, not how it feels. Name the mechanism or the number. Cut any sentence that could appear unchanged in another project's docs.
28. One idea per sentence. Split a sentence the reader has to reread.
29. Active voice. Name the actor unless it is unknown or beside the point.
30. Cut the adverb or use a stronger verb. Give the number.
31. Use the plain word: "use", not "utilize" or "leverage".
32. No metaphor, aphorism, personified code, or figurative verb where a literal phrase exists.
33. Write whole sentences with their articles and verbs. Spell out arrows and abbreviations.

## Engineering-specific tells

34. No status without a fact. "Improved error handling" says nothing. "Returns 422 with the field name instead of 500" says it.
35. No unmeasured performance adjective: fast, lightweight, scalable, efficient, performant. Give the number and its limiter, or drop the claim.
36. No "best practice", "industry standard", or "enterprise-grade" as a justification. Say what breaks without it.
37. A number with no unit, run count, or baseline is not a number. "40% faster" is a rumor until it says faster than what, measured how many times.
38. Do not narrate the work in a deliverable. A PR body says what changed and what it proves, not "I then investigated the service layer".

For Spanish short-form video scripts, **anti-slop** owns the catalog instead, including the translation smell and the spoken word budget. This skill is for English technical prose.
