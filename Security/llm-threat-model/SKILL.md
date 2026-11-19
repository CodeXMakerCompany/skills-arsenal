---
name: llm-threat-model
description: Map and close the attack surface an LLM feature adds: prompt injection, data exfiltration, tool and agent abuse, output handling, cost abuse, and model-specific refusal and jailbreak paths. Use for /llm-threat-model, "is this AI feature safe", "prompt injection", "securing our agent", "¿es seguro este endpoint de IA?", or before any LLM feature reaches production.
---

# LLM threat model

AI in production means a new attack surface, not a new feature on the old one. Treat prompt injection, data exfiltration, and model abuse as first-class security concerns, because none of the existing controls see them: a WAF does not read intent, and an authenticated user is the attacker in most of these paths.

Work through the six surfaces. For each, name what you found and the control you are relying on, not the control you hope exists.

---

## 1. The trust boundary

Draw it first, before anything else. **Everything the model reads that a user or a third party can influence is untrusted input**, and the model cannot tell it apart from your instructions.

List every source that reaches the context: the user's message, uploaded files, retrieved documents, a web page fetched, a tool's result, a database row, an email, a ticket, a PR comment, another agent's output. Each one is a path for injected instructions.

The control is not "tell the model to ignore instructions in the data". That is a mitigation with a known failure rate. **The control is that the model's output cannot do damage on its own** (surfaces 3 and 4).

## 2. Prompt injection

- **Direct.** The user tells the model to ignore its instructions, reveal the system prompt, or call a tool it should not. Assume the system prompt is readable and design so that it being readable costs you nothing. A secret in a system prompt is a published secret.
- **Indirect.** Instructions hide in content the model reads: a document, a page, an email, a filename, a code comment, an issue body. This is the one that matters, because it needs no access to your app.
- **Controls that actually hold:** mark untrusted spans structurally rather than by politeness; keep the operator channel separate from the conversation; give the model no authority it does not need; and put the irreversible step behind a human or a deterministic check, never behind the model's judgment.
- **Test it.** Keep a small injection suite in the eval set (**llm-evals**) and run it on every prompt change and every model change. An injection defense nobody re-tests after a model swap is a defense from the previous model.

## 3. Data exfiltration

The model is a channel out of your system, and so is anything it can make a request to.

- **What is in the context that should not leave?** Another tenant's rows, PII, secrets, internal URLs, the retrieval corpus itself.
- **Multi-tenant retrieval is the common breach.** Filter by tenant in the query, not after it, and prove it with a test that asks for another tenant's data by id.
- **The exfiltration paths to close:** a rendered image or link whose URL carries the data, a tool that makes an outbound request to a URL the model chose, a markdown link in the output, an error message that echoes context, a log line that writes the whole prompt.
- **Allowlist outbound destinations** for any tool the model can call. A fetch tool with an open destination is an exfiltration endpoint with extra steps.

## 4. Tool and agent abuse

- **Every tool the model can call is an action an attacker can request.** Inventory them, and for each: what it can do at its worst, with whose credentials, and whether it is reversible.
- **Least privilege per tool, not per service.** A read tool uses a read-only credential. A tool that touches one tenant's data takes the tenant from the request context, never from a model-supplied argument.
- **Validate tool arguments as untrusted input**, with a schema, even though a model produced them. Especially a path, a URL, an id, a query, or anything that reaches a shell.
- **Irreversible actions need a human or a deterministic gate**: sending, paying, deleting, deploying, messaging a customer, writing to a shared branch.
- **Multi-agent means the blast radius compounds.** An agent that passes untrusted content to another agent has passed the injection along with it. Keep privilege at the edge, and never let a worker's output authorize anything.

## 5. Output handling

Model output is untrusted data on the way out, exactly like user input on the way in.

- Rendered as HTML means XSS. Rendered as markdown means link and image exfiltration. Put into a query means injection. Passed to a shell means RCE. Written to a file means path traversal. **Encode for the sink, every time.**
- Parse structured output against a schema and handle the parse failure as a normal error path, because a hallucinated field is routine, not exceptional.
- Where output drives a decision (an approval, a score, a route), decide what happens when it is wrong, and make that path cheap.

## 6. Abuse, cost, and availability

- **Rate-limit per user and per tenant on tokens, not just requests.** One request with a 200k-token input costs a thousand small ones.
- **Cap max tokens, cap the loop, cap the fan-out, cap retries.** An agent loop with no iteration cap is an unbounded bill and an unbounded latency.
- **Validate input size before it reaches the model.** The cheapest rejection is the one that never buys tokens.
- **Watch the spend as a security signal.** A spike is either a bug or an abuser, and both want an alert (**cost-per-request** for the model, **observability-baseline** for the alarm).
- **Plan for refusal and degradation.** A model can decline a request or fail safety classification, and your path must handle that as a first-class outcome rather than rendering an empty answer. Likewise for a timeout: name the fallback, whether that is a smaller model, a cached answer, or an honest error.

---

## Output

A table of the six surfaces with what you found and the control you rely on, then:

- **Findings**, ordered by what an attacker gets. Each with the path, the proof (the injection string, the request, the output), and the fix.
- **Accepted risks**, each with who accepted it.
- **The one test** to add to the eval set so this does not regress on the next prompt or model change.
- **Verdict**: ships or does not, by the same rule as **nexus-guard**.

A threat model with no proven finding is a valid result, and it says which surfaces you probed and how, so the next reviewer knows what was and was not tried.
