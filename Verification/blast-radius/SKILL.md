---
name: blast-radius
description: Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it is safe because of by running real code instead of writing it up. Use for "blast radius of X", "what could this break", "¿qué puede romper esto?", or reviewing a small diff you do not trust.
---

# Blast radius

Find what a change breaks somewhere else, before it ships.

Companion to **how** and **why**. `how` tells you what the code does. `why` tells you why it is shaped that way. Blast radius tells you what it breaks elsewhere.

Listing the callers is not the job. Anyone can grep those in a second. The job is the breakage grep will not show you.

## Do not trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it is true. So do not hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case cannot happen. You walked the failure step by step and it does not reach.
4. You ran it. A script or test that calls the real code and fails loud if you are wrong.
5. You reproduced it in the running system.

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you are worried about.

## Steps

1. **Read the change.** The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff does not spell out. Pull the PR and its commits.
2. **Find the one fact it is safe because of.** Most changes that look risky are safe because of a single fact, such as "this only evicts entries already past their TTL". Find that fact. If it holds, most risky cases clear at once. Spend your time here, not on a long list of maybes.
3. **Look where grep stops.** The JSON shape an API returns and another service parses. A column another service reads. A queue message an older consumer still handles. A cached value with a different lifetime. An IAM policy that allowed the old call. A feature flag. An event another team subscribes to. The library's own source, its pinned version, and any local patch. In a microservice estate, the consumer you will break is in another repository, so grep there too.
4. **Be honest about each risk.** Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed and list the ones you checked and cleared separately. Cite a real `file:line`. A search that finds nothing is still an answer. Never invent a caller or an API.
5. **Prove the one fact.** Write the script, run it, paste what happened.
6. **For a big or wide change, run it as an arena.** Ask more than one model the same question and merge the answers.

## What to hand back

- **What it does.** What changed, including the part that is not obvious.
- **The one fact it is safe because of.** State it, say which step you got it to, show the proof. If you could not prove it, write unproven.
- **Risks.** Each with how it breaks, the `file:line`, how likely, how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it is fine.
- **Before you merge.** The cheapest test or repro that would catch the real bug, including the script you wrote.

Write it through **unslop**, cite real code, and strip anything private before it goes anywhere public.
