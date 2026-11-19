---
name: recall
description: Rebuild your recent working context from your own session history, live repo state, and the shared record (tickets, PRs, incidents, user reports), then hand back a tight current-state brief. Use for "recall my work on X", "where did I leave off", "what have I been working on", "¿en qué me quedé?", before starting or resuming work.
---

# Recall

**Before you start or resume work, rebuild the recent working context and hand back a tight capsule of where things stand and what to do next.**

Keep it tight and on topic. Read only what the in-scope threads need, then stop.

Context lives in two records. Your own session history holds what you did and decided. The shared record holds everything that happened around the same code under other names: the symptoms users keep reporting, the fixes that shipped and got reverted, the errors still firing in production. That second record lives in git, the issue tracker, chat channels, docs, and the error tracker. A feature with a long bug tail keeps most of its story there, so never reconstruct it from your own transcripts alone.

1. **Classify, then route.** Resuming one specific prior session is the Session pickup playbook, not this. Turning habits into a durable skill is **automate-me**. A human-readable summary of what happened in this chat is **ketchup**. Recall loads working context across recent sessions before you act. If the user already handed you a full state capsule, use it and skip the mining.
2. **Lock the scope before searching.** Pin the window ("recent" means a real range, default the last 7 days), the topic if named, and the repository. State the scope back. Never quietly turn "all" into "recent N".
3. **Fan out across your session history.** Spawn parallel subagents on `claude-sonnet-5-5`, each taking a slice. Tell every one to order candidates by real modification time, grep the topic first and read only matching sessions and only their relevant regions, and skip obvious noise. Each returns the same schema per session: topic, the user's goal, decisions, open threads, corrections, and artifacts (PRs, tickets, branches), each cited. For one or two sessions, skip the fan-out and read directly. Raw transcripts stay in the subagents.
4. **Sweep the shared record** whenever the topic names a feature, file, subsystem, or bug. This is the default, not a judgment call. One investigator per source, asking "what is the current state, what was tried and did not hold, and what are users still reporting". Null results are findings. Say which sources were unavailable.
5. **Verify against live state.** Take the PRs, branches, and tickets the mining surfaced and check them with `git` and `gh`. The record states intent; the repo states truth.
6. **Write the brief to the contract below.** Group by thread, stay on the named topic.

## Output contract

- **Capsule.** At most five bullets. What this work is and where it stands overall.
- **Threads.** One line each, prefixed with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, `[planned, not started]`. A thread with no tag is not done, so tag it.
- **Problems.** At most five, the recurring ones. Include the symptoms users keep reporting and any fix that shipped and was reverted, so the next attempt starts where the last one failed.
- **Next move.** The single most useful next action, concrete.

An adjacent feature or ticket stays out unless it blocks this one. When the brief outgrows a screen, cut detail before you cut threads. Write it through **unslop**, cite each finding by its source, and strip private context before any output that leaves the machine.
