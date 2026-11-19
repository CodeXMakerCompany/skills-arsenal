---
name: setup-issue-bot
description: Configure the unattended issue bot and its two automations, triage and reproduce. Use when installing the issue bot, or changing its chat source, tracker, repository, routing, control adapter, model, or budget.
---

# Set up the issue bot

The issue bot is two unattended automations over one config: **triage-issue-reports** turns a reported problem into one verdict and at most one ticket, and **reproduce-and-fix-issues** takes a triaged ticket, reproduces it against the real app, and opens a bounded draft PR only after before-and-after proof.

Both read the config this skill writes. Neither invents a setting.

## 1. Collect the config

Ask only what you cannot observe from the repo. Write `.claude/issue-bot.yaml`:

```yaml
source:
  kind: slack                 # slack | linear | jira | github
  channel: "#bugs"            # where reports arrive
  reply_in_thread: true       # a verdict is one threaded reply, never a new message
tracker:
  kind: linear                # linear | jira | github
  project: "APP"
  dedupe_window_days: 30
repo:
  path: .
  base_branch: main
  pr: draft                   # draft always; never ready-for-review unattended
control:
  verification_skill: .claude/skills/verify-app/SKILL.md
  seed_command: npm run seed
limits:
  max_files_changed: 8
  max_diff_lines: 300
  max_minutes_per_issue: 25
  max_usd_per_issue: 2.00
models:
  triage: claude-haiku-5-5
  reproduce: claude-opus-5-5
escalate_to: "@sam"
```

## 2. Require the control adapter

**The reproduce automation cannot run without a verification skill.** Reproducing a bug means driving the real app, and an agent that cannot launch, drive, and observe the app will instead read the code and report a theory as a repro. That is the failure this bot exists to avoid.

If the repo has no verification skill, stop and run **create-verification-skill** first. Then come back.

## 3. Set the fences

These are the settings that keep an unattended bot safe. State each one back to the user before writing the file.

- **Draft PRs only**, on a branch per issue, never on the base branch.
- **Never force-push, never deploy, never run a migration against real data, never message a customer.**
- **Never close, merge, or reassign a ticket** a human owns. The bot comments and labels.
- **One verdict per report**, as a threaded reply. A bot that posts twice in a channel gets muted within a week.
- **Fail closed.** Any step the bot cannot complete ends in escalation to `escalate_to`, not in a guess. A ticket it could not reproduce says exactly that.
- **Spend caps are hard.** At the cap the bot stops, reports where it got to, and escalates.

## 4. Prove it on one real report

Run the triage automation once against a real past report with the output redirected to a scratch channel or a dry-run flag, then run the reproduce automation once against a ticket you already know the answer to. Confirm: the verdict is one message, the ticket has no duplicate, the repro drove the real app, the PR is draft and inside the limits, and the cost came in under the cap.

**An automation that was never run against a real report is not configured, it is drafted.**

## 5. Hand back

The config path, each setting and why, which fences are on, what the two automations will and will not do, the per-issue cost ceiling, and how to turn it off in one step.
