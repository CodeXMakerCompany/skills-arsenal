---
name: webhook-trigger-ui
description: Build a small page or control panel that wakes an agent or a workflow over a webhook, keeping the sender key on the server. Use when you want a button, dashboard, or form that kicks off an automation, an n8n workflow, or a scheduled agent, and when exposing that panel on a private network.
---

# Webhook trigger UI

Build a page a human clicks. A small server on the trusted side receives the click and POSTs JSON to the webhook that wakes the agent or workflow. **The secret stays on the server.**

The shape is always the same three pieces: the page, the server that holds the credential, the webhook that does the work. Most of the mistakes are in the middle piece.

## 1. Create the webhook endpoint first

Create the receiving end before the UI: an n8n webhook node, a scheduled agent's webhook trigger, a Lambda behind a function URL, or an API route. Then write down its URL and its secret, and note that the URL alone is not a credential.

The receiving prompt or workflow treats the POST body as **untrusted data**. It names the fields the UI sends and does the matching action. A webhook whose prompt says "do what the body asks" is a public shell, however obscure its URL.

## 2. Keep the secret on the server

- The sender key, signing secret, or token lives in the server's environment. Never in the page, never in a bundled JS file, never in a query string, never pasted into a chat.
- The browser calls **your** endpoint. Your endpoint calls the webhook. The browser never learns the secret and never talks to the webhook directly.
- Sign the request where the receiver supports it (an HMAC over the body with a timestamp), and verify the signature and the timestamp on the receiving side. A shared bearer token that never rotates is the floor, not the goal.
- Rotate on exposure, and treat a secret that reached a browser, a log, or a screenshot as exposed.

## 3. Make the trigger safe to press twice

Every button will be pressed twice, by an impatient human or a retrying browser.

- Send an idempotency key with each trigger, generated per click, and have the receiver ignore a repeat (principle-make-operations-idempotent).
- Disable the control while a run is in flight, and show the run's state rather than a spinner that lies.
- Rate-limit on the server, per user and overall. A page with one button and no limit is one hotkey away from fifty concurrent runs and a real bill.
- For an irreversible action, require a typed confirmation of what will happen, not a second button.

## 4. Show the run, not just the submit

A trigger panel whose only feedback is "sent" gets distrusted and then abandoned. Show: the run id, its state, when it started, and where to read its output. Poll your own endpoint for that, never the vendor's API from the browser with a key attached.

## 5. Expose it privately

Default to localhost. Where it must be reachable from a phone or another machine, put it on the private network: a mesh VPN (Tailscale or equivalent), an SSH tunnel, or an internal load balancer with the organization's identity provider in front.

**Never expose a trigger panel to the public internet with no authentication**, whatever the URL looks like. If the only auth you can manage is a shared password in an environment variable, say so plainly and keep it off the public internet.

## 6. Hand back

The three pieces and where each one runs, where the secret lives and how to rotate it, the idempotency and rate-limit behavior, how the panel is reached, and the one command that takes it down.
