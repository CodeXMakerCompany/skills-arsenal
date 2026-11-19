---
name: ketchup
description: Catch the user up on what changed in this session since their last message, in plain words and small visuals, then list every call waiting on them with enough to decide from the reply alone. Use for /ketchup, "catch me up", "ponme al día".
---

# Ketchup

Catch the user up on what changed since the last message *they* wrote, and help them understand each change, not only where it stands. Then lay out every call waiting on them so they can decide from your reply alone. Notifications and subagent results are not their messages. Assume they remember their last message and nothing after it.

Use **bro**'s voice, not its task: plain words, short sentences, no jargon, one person catching another up. Say what changed for the user, not how you did it. Say "the tests pass", not "CI is green". Leave out hashes, paths, commands, and build numbers unless the user needs one to act. Call each PR, branch, or agent by a name they would recognize.

## Gather what changed

Keep this turn read-only. Make visuals only from what you already have: do not change code, start an app, or post anything.

Collect your own work since that message, subagent reports, and anything else that arrived. Check the current state of each PR, pipeline, or agent this session touched. Check each number against the facts it came from and say so when you correct one.

An **action item** is a call only the user can make: a product choice, an approval, an irreversible action, or access you lack. Include any still waiting, even one raised before their last message. Work you can still do yourself is not an action item. Never invent a call to fill the reply.

For each item collect its link, what it changes for users, the evidence behind your pick, its risk, and your pick. Write "unknown" for a fact the call needs and you do not have.

## Write the reply

Spend words on the calls, not the story. Keep what happened under 100 words, less when less happened. Give each item about 30 words. Never cut items to stay under a count: no number in place of a list, no link in place of an item.

Open with one short sentence naming what waits on the user, or saying nothing does. If nothing happened and nothing waits, say so and stop.

Then what happened, pictures first: screenshots and recordings the work produced, then any diagram that explains a change. Then one short bullet per thing they asked for: what came of it, and whether it is done, still running, failed, or unchecked. Each line must stay true read alone. Never mark something done that still waits on the user.

Then the action items. Ask the call they own, give your pick, and name the PR, issue, or agent it is about. For a call between options, give every option the work weighed with what it gets them and what it costs. Those costs are the risk, so add no separate risk line.

## Visuals

A visual is a picture: a screenshot, a recording, a Mermaid diagram, a chart. A Markdown table is not a visual.

Draw when something is easier to grasp as a picture: how a design works, a PR chain with each state, a before and after, options side by side. Never draw a status list or boxes with nothing connecting them. Keep each visual readable at a glance, at most six boxes and eight words a box. Never invent a number, and never draw a screen you did not capture.
