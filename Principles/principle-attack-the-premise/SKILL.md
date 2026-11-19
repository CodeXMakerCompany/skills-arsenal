---
name: principle-attack-the-premise
description: Apply when two or more fixes that share one premise have failed the same gate. Write the premise down and test it directly before writing another fix that assumes it.
---

# Attack the Premise

When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

- **Write the premise down.** The one sentence every failed fix assumed. "The timeout is the retry budget." "The 429s come from our rate limiter." "The slow part is the model call."
- **Test it before the next fix.** Find an observation that would come out differently if the premise were false, and make it. Look at how the failures are distributed, not only how large they are. One request's trace beats an average.
- **If the evidence contradicts the premise**, look for what the failures share that it did not predict. If one part always lands on the losing side, change what puts it there rather than adding a mechanism that cleans up after it.

Do not start the next fix before the premise is written down and tested. Three fixes against an untested premise cost more than one hour spent testing it.
