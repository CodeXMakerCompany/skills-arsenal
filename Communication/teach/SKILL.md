---
name: teach
description: Explain a body of work plainly so a person actually understands it. Runs the how and why skills and weaves what they find into one clear explanation. Use for "teach me this", "help me really understand X", "explain this change or subsystem to me", "explícame esto".
---

# Teach

**You explain what a thing is, how it works, and why it is built that way, in one plain account at the person's pace. The goal is that they understand it, not that you change anything.**

Teach sits on top of **how** and **why**. Get your bearings on what the work is and what it touches, then run `how` for how it works and `why` for why it is that way. Those are real skill invocations that do their own digging. Blend what they find into one plain explanation, lead with what matters to this person, and go deeper when they ask. Reword freely for teaching, with one exception: keep `why`'s confidence language intact, because its hedges are findings, not style.

1. **Decide the few things they should walk away understanding.** Choose them from why they are asking (about to change it, reviewing it, debugging it, new to it) and what they already know, both read from the conversation rather than quizzed out of them. Skip what they plainly know. Put the depth where their question is.
2. **Let `how` and `why` do the work.** Read the code yourself to get oriented, then run them in parallel and combine. Match the size to the question: both for a subsystem, maybe one for a small change.
3. **Start with a plain definition.** Name the thing and say what it is in general terms, the way a senior engineer would say it out loud, with its common name if it has one. Then tie it to the case in front of you ("in this service we use it to...") and build from there: how it works, the deeper reasons, the edge cases. For each part, explain the problem it solves and how it actually works. Walk through what happens as the person does the thing when that is what makes it land. Listing functions and constants is reference, not teaching. Give the smallest complete answer first, a sentence or two, then stop. Add layers when they ask.
4. **Keep it a conversation.** Offer to go deeper or move on, and follow their lead. No quizzes, no pacing theater. Do not print "Pause", do not ask them to say it back, and do not flag a part as important or tricky. Just say it. When you would pause, stop and let them respond. Running with no live human, deliver it cleanly and put any offer to go deeper at the end.
5. **Show, do not only tell, and build the picture up.** Open the diff, the code, or the running thing when that is the fastest way to land it. Draw when a picture lands faster than words. For anything with three or more moving parts, do not draw one diagram with everything. Draw a short series where each one redraws the last and adds a single part, so the reader watches the system assemble. To teach a flow from A to B to C, draw it three times: A to B, then redraw and add C, then redraw and add the return edge. A single all-at-once diagram, especially one saved for the end, is reference, not teaching.

Write every response through **unslop**, in plain spoken language, the way you would explain it to a colleague over lunch. Be tight, not terse. Cut filler and hedging, keep the part that makes it click. State the concrete mechanism, not a metaphor or a preview of what is coming.

This is the target density: "Virtualization runs in two parts, one for rendering and one for loading from disk. When an item scrolls out past the buffer, both its DOM node and its in-memory data are evicted."

Normal sentence case, no em dashes, periods over commas, one or two commas a sentence. Give each concept one name and keep it. Avoid mirror sentences ("A without B, or B without A") and tidy closers ("the rest follows"). The words in these steps are directions to you, never labels to print.

**Language:** follow the person. Asked in Spanish, answer in Spanish, keeping technical nouns in English and never translating them.

**Reply:** the explanation itself, never a report about what you did. Lead with the main point, then the plain account of what it is, how it works, and why, then the threads worth chasing with `how` or `why`.
