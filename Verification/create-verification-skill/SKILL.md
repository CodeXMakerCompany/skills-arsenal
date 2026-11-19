---
name: create-verification-skill
description: Generate a project-local verification skill that drives the real app the way a user does, in any language or framework, so later agents can prove behavior instead of claiming it. Use for /create-verification-skill, "make a control skill for this repo", or when a project has no scripted way to prove UI, CLI, or service behavior.
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, capture evidence. This skill generates that as a project-local skill at `.claude/skills/verify-<app>/`, tailored to the repo.

Write the output for the next agent, not for a human. It will be read cold, mid-task, by an agent that has never seen this app.

## 1. Interview the repo, not the user

Answer these from the codebase and ask the user only what you cannot observe.

- **Surface.** What does a user actually touch? A web UI, a CLI, an API, a mobile app, a library, a queue consumer? A repo can have several, so pick the primary one and note the rest.
- **Run.** How does it start locally? Prefer the repo's own documented command: package scripts, Makefile, compose file, README quickstart. Note ports, env vars, seed data, auth.
- **Drive.** How can an agent interact with it programmatically? Existing harnesses first: Playwright or Cypress specs, a `requests`/`supertest` suite, curl-able endpoints, a debug port. Only then a generic recipe: a browser driver for web, a PTY harness for a CLI, plain HTTP for a service.
- **Observe.** What evidence can be captured? Screenshots, terminal transcripts, response bodies, logs, exit codes, database rows, queue depth.
- **Isolate.** Can two instances run side by side (ports, data dirs, profiles)? If not, say so in the generated skill. Refusing to double-drive a shared instance beats corrupting the user's session.

If the checkout does not build or start as is, fix that first or report it precisely before generating. A skill written against a broken base teaches wrong steps.

## 2. Generate the skill

Write `.claude/skills/verify-<app>/SKILL.md` with frontmatter (`name: verify-<app>`, and a description naming the app, the surface, and when to reach for it; without frontmatter the skill never registers) and these sections, each grounded in what the interview actually found. No placeholders.

- **Launch.** The exact command, and how to tell it is ready: a log line, a healthy endpoint, a prompt. Launch must reach a usable state from an empty data dir, including migrations and seed data. **Ready means usable, not that a process answers**: a database health check passes while its init scripts are still running.
- **Doctor.** One read-only check answering "is this instance worth driving?" Process up, right build, port owned by us, auth valid. An agent runs this first whenever anything looks off.
- **Drive.** The harness recipe with real selectors, routes, and commands from this repo, not examples. Prefer stable handles (ARIA labels, test ids, route paths, prompt strings) over coordinates and tab order.
- **Evidence.** What to capture and where it goes. State the proof standards: exercise the real user path, not an internal setter or a test-only endpoint; capture the action and the resulting state, not just the final screen; verify side effects (rows written, messages sent, files created) alongside what is visible; mock only where a production boundary already isolates the external system. Where the safe path is a dry run, verify what it actually skips by observing files, network, and refs, because some dry runs still touch the network.
- **Cleanup.** How to tear down what the run created. Never kill by process name, kill what you started. Cleanup removes instances and scratch state and **never the evidence**, which survives in a location the skill names.
- **Helpers.** Any script the skill ships is executable and its invocation appears in the skill body. A helper the reader has to reverse-engineer is not a helper.

## 3. Seed the feature map

Create `.claude/skills/verify-<app>/features/README.md` as an index, plus one file per user-facing feature, aiming at the top three to five from routes, commands, menus, or docs. Each file answers, from the user's point of view: what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. Use four headings: `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, `Gotchas`.

If the seed data lacks a precondition a journey needs, the journey reports a failure and the reason goes in that feature's `Gotchas`. **Never weaken a journey to make it pass.**

The map is the repo's maintained verification source. A proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

Run its own instructions end to end once: launch, doctor, drive one mapped feature, capture evidence, clean up. After cleanup, confirm the evidence still exists where the skill says. A cleanup that eats the proof fails this step.

Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts do not strand processes and ports. **A generated skill that was never executed is a draft, not a deliverable.**

If you proved it in a stand-in for the real target (a container for a VM, a local stack for a remote one), list every setup step the stand-in did that the target will not. Those stay unverified.

## 5. Offer the maintenance loop

Point the user at **maintain-verification-skill** for keeping the map honest as the app changes. Suggest a cadence only if they ask.
