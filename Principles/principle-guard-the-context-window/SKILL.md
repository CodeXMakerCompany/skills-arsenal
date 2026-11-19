---
name: principle-guard-the-context-window
description: Apply when context is filling up: large outputs, long files, repeated reads, log and trace dumps, fan-out planning. Route bulk to subagents; keep summaries in the main thread, never raw payloads.
---

# Guard the Context Window

Context overflow degrades reasoning before it stops progress. The failure is quiet: the answers get worse while the agent sounds the same.

- **Route bulk to subagents.** A log file, a trace, a transcript, a 4000-line generated file, a dependency tree. The subagent reads it and returns the finding. The payload never enters the main thread.
- **Keep summaries, not dumps.** A worker's job is to hand back a conclusion with its evidence pointer, not its raw output. Pasting a full subagent report into the main thread defeats the delegation.
- **Size phases and cap scope.** Limit files per phase, set a turn budget, and account for what each mechanism costs in tokens before you launch it.
- **Read the region, not the file.** Grep first, then read the matching range. Reading a whole file to find one function is the most common way context goes.
- **Re-reading is a signal.** The third read of the same file means the finding should have been written down the first time.

Cost follows the same curve as quality here. Input tokens are billed on every turn of the conversation, so a payload pasted once is paid for repeatedly. Prompt caching helps only where the prefix stays byte-identical, so put the stable material first and the volatile material last.
