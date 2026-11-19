# Investigation

**You own the answer. Plan, route, write.** Read-only. The deliverable is a cited explanation or a recommendation, never a code change.

1. Restate the question with **in-your-own-words**. An investigation answering the wrong question is wasted whatever it finds.
2. Route by what the question is actually about. Runtime behavior → **how**. A decision or a rationale → **why**. What a change could break → **blast-radius**. A number → **benchmark-checklist**. Cost → **cost-per-request**. Several at once → run them in parallel and merge.
3. Fan bulk reading out to subagents on `claude-sonnet-5-5`, one slice each, and keep only their findings in the main thread. Raw logs, long files, and trace dumps never enter your context whole.
4. Separate what the record says from what you concluded. Cite commits, PR numbers, ticket IDs, `file:line`, and dashboard links. Mark every inference as an inference and say what the record does not answer.
5. End with the decision the answer enables and the cheapest next step that would settle what is still open.

Never end an investigation with a patch. If the fix is obvious, say so in one line and let the human pick the playbook.
