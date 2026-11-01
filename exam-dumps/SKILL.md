---
name: exam-dumps
description: Browse and scrape certification exam question dumps from ExamTopics using the local Free-Exam-Dumps scraper. Use when the user asks for exam dumps, exam questions, "scrape SAA-C03", "dumps de examen", "saca las preguntas de AZ-104", names a certification code (SAA-C03, AZ-104, SY0-701, CISSP, 200-301), asks which exams are available, or wants to run another scrape after one finishes. Lists exams with descriptions, scrapes the selected one, then offers the list again.
---

# Exam Dumps

Drive the local `Free-Exam-Dumps` scraper: list exams, scrape one, repeat.

The tool is a **CLI that prompts interactively**. This skill never lets it prompt. Every
run is fed a single exact exam slug on stdin so it resolves to exactly one exam and starts
immediately. A run that reaches an `input()` call with nothing on stdin hangs forever.

> **Wrong:** `python main.py` — blocks on "Exam code or name:" and never returns.
> **Right:** `printf '%s\n' "$SLUG" | python3 main.py` — one exact hit, straight to work.

---

## Repo map

| What | Where |
|---|---|
| Scraper repo | `/home/codexmaker/Repositories/Free-Exam-Dumps` |
| Entry point | `main.py` (interactive; only flag is `--refresh`) |
| Library | `examtopics/` — `index`, `matching`, `scanner`, `parsers`, `output` |
| Exam index cache | `.examtopics_index.json` — 2,340 exams, ~172 KB, no expiry |
| Question output | `<slug> dumps.txt` |
| Link output | `<slug> links.txt` |

**Every path the tool writes is relative to the working directory.** Always run it with
`cd /home/codexmaker/Repositories/Free-Exam-Dumps`, so outputs land at the repo root next
to `main.py`. Both output patterns are in that repo's `.gitignore`, so they never show up
as dirty files.

The repo sits **outside** the `skills-arsenal` session folder, so the app's file pane will
not open those files from a relative path. Always report the **full absolute path** when a
run finishes.

---

## Preflight

Run these two checks once per session, before the first scrape. Both failures are silent
and produce zero results rather than an error.

**1. `tqdm` must be importable.**

```bash
cd /home/codexmaker/Repositories/Free-Exam-Dumps && python3 -c "import requests, tqdm" 2>&1
```

`requests` is present system-wide. `tqdm` is not, and this machine has no `pip`, no
`python3-venv` and no `uv`, so the README's `.venv` path cannot be followed as written.
The fix needs the user's own sudo:

```bash
sudo apt install python3-tqdm
```

Do not work around a missing `tqdm` by editing the scraper. `main.py` and `scanner.py`
both import it at module level for their progress bars.

**2. The provider parser must still match the live site.**

```bash
cd /home/codexmaker/Repositories/Free-Exam-Dumps && python3 -I -c "
import sys; sys.path.insert(0,'.')
from examtopics.http_client import HttpFetcher
from examtopics.parsers import extract_providers
print(len(extract_providers(HttpFetcher().fetch_html('https://www.examtopics.com/exams/'))), 'providers')"
```

Expect ~195. **If it prints 0, no scrape can work** — the listing regexes have stopped
matching the live markup.

This already happened once and is **patched locally** (uncommitted, in the clone only).
ExamTopics moved from relative to absolute hrefs
(`href="https://www.examtopics.com/exams/amazon/"`), which silently broke three places:

| Site | Effect when it breaks |
|---|---|
| `extract_providers` | 0 providers → 0 exams → "Could not load the exam index" |
| `extract_exam_entries` | 0 exams for every provider |
| `CONTENT_SENTINEL` | `is_blocked_html` never short-circuits, so real pages can be read as captcha pages |

The fix is a shared `HREF_ORIGIN = r"(?:https?://[^/'\"]+)?"` spliced in front of each
`/exams/` anchor, and a sentinel matched on the path alone. It accepts both forms, so it
is safe if the site reverts.

**A `git pull` in that repo will revert this.** The upstream test suite uses only relative
hrefs in its fixtures, so it passes either way and will not warn you. Re-run this preflight
after any pull, and never patch that repo silently — ask first.

---

## The loop

1. **List** — show exams with descriptions, scoped (see below). Number every row.
2. **Select** — the user picks a number, a code, or a description.
3. **Confirm the slug** — resolve the pick to its exact slug before running anything.
4. **Scrape** — one background run. Report progress only when asked.
5. **Report** — absolute output path, question count, coverage.
6. **Show the list again** and ask whether to scrape another. Keep looping until the user
   stops.

Step 6 is not optional. The list comes back every time without being asked for.

---

## Listing exams

There are **2,340 exams across 195 providers**. Never dump all of them — scope first.

```bash
cd /home/codexmaker/Repositories/Free-Exam-Dumps && python3 -I -c "
import sys; sys.path.insert(0,'.')
from examtopics.http_client import HttpFetcher
from examtopics.index import load_exams, find_exams
exams = load_exams(HttpFetcher())
for provider, slug, name in find_exams('QUERY', exams)[:40]:
    print(f'{slug}\t{provider}\t{name}')"
```

- `find_exams(query, exams)` matches a code **or** a partial name, shortest slug first.
- Replace `find_exams('QUERY', exams)` with a provider filter
  (`[e for e in exams if e[0] == 'microsoft']`) when the user names a vendor.
- With no query at all, show **provider counts** and ask which vendor, rather than 2,340 rows.
- The first `load_exams` call of the machine's life costs ~190 requests and ~30s, then it
  is cached forever. A search that misses rebuilds it once automatically.

Present it as a numbered table. The description is what the user selects on, so it leads:

| # | Exam | Code | Provider |
|---|---|---|---|
| 1 | AWS Certified Solutions Architect – Associate | `SAA-C03` | amazon |

Keep the slug out of the table — it is long and the user never needs to type it. Hold it
internally for step 3.

---

## Running a scrape

```bash
cd /home/codexmaker/Repositories/Free-Exam-Dumps && printf '%s\n' "aws-certified-solutions-architect-associate-saa-c03" | python3 main.py
```

**Always pass the full exact slug, never the bare code.** `find_exams` has an exact-slug
branch that wins outright and returns a single hit, so the tool skips its menu and starts.
A bare code like `SAA-C03` is a substring search against 2,340 exams: it can return several
hits, print a numbered menu, and then block on a second `input()` that nothing answers.

**Always run it in the background.** Measured times:

| Exam | Questions | Time |
|---|---|---|
| `SAA-C03` | 1019 | 130s |
| `github-actions` | 65 | ~247s |
| `AI-103` | 135 | ~346s |
| `hpe7-a07` | 62 | ~415s |

A sparse exam is slower than a big one: the id walk only runs when the listing is missing
questions, and it works through every round before giving up. Minutes, not seconds — so
never run one in the foreground and never poll its output file while waiting.

**Re-running:** a finished exam returns instantly from its own output files. Add `--refresh`
to download it again, which **overwrites** both files — say so before using it.

```bash
cd /home/codexmaker/Repositories/Free-Exam-Dumps && printf '%s\n' "$SLUG" | python3 main.py --refresh
```

---

## Reporting a finished run

Report exactly four things, then show the list again:

1. **Absolute path** to `<slug> dumps.txt`.
2. **Question count** and **coverage** — the tool prints `N of M published (P%)`.
3. **Whether it was reused** — "reused" in the output means nothing was downloaded.
4. The links file only if the run was interrupted or coverage looks wrong.

**A zero exit code does not mean a complete scrape.** The tool writes what it got and
exits 0 even after losing questions, so always read the coverage line. There are two very
different reasons it can be low, and they get opposite answers:

| What the output says | Meaning | Response |
|---|---|---|
| Low coverage, no warnings | Those questions have no public discussion thread | Real result. Do not retry. |
| `[WARN] N questions could not be fetched` with `429` | Rate limited mid-run | Incomplete. Wait, then `--refresh`. |
| `Recovered: 0 questions by id` on a sparse exam | The id probe was throttled too | Treat the whole run as rate limited. |

Never retry a 429 immediately, and never raise `WORKERS` to compensate — that is what
caused it. Building the exam index costs ~195 requests, so a scrape started right after a
fresh index build is the most likely one to get throttled. Wait a few minutes between the
two.

The dump is plain UTF-8 text: a header, then one block per question with the choices, the
suggested answer and the community vote split. Offer to open it or to pull out a specific
topic — do not paste the whole file into the conversation, it runs to thousands of lines.

---

## Failure modes

| Symptom | Cause | Response |
|---|---|---|
| Hangs with no output | stdin empty, blocked on `input()` | Kill it. Re-run with the slug piped in. |
| `0 providers` in preflight | Absolute-href parser bug | Stop. See Preflight 2. Nothing works until it is fixed. |
| `ModuleNotFoundError: tqdm` | Missing dependency | `sudo apt install python3-tqdm`, by the user. |
| `Could not load the exam index` | Network, or the parser bug | Run preflight 2 before blaming the connection. |
| "No discussion links found" | Exam exists, has no threads | Real answer. Not retryable. |
| `Blocked by anti-bot/captcha page` | Rate limited | Stop and wait. Do not retry in a loop or raise `WORKERS`. |
| `429 Too Many Requests`, exit code 0 | Rate limited, partial output kept | Check coverage. Wait, then `--refresh`. |
| Multiple hits, menu printed | A code was passed instead of a slug | Re-run with the exact slug. |

The scraper's concurrency is already at a measured ceiling (`WORKERS = 24`, ~8 req/s server
side). Raising it adds sockets and no speed. Leave `settings.py` alone.

---

## Boundaries

- Do not answer the exam questions, grade them, or present a dump as a study guide. This
  skill fetches files; what the user does with them is theirs.
- Do not edit `settings.py`, and do not patch `parsers.py` without asking.
- Do not commit output files — they are gitignored upstream for a reason, and they are
  large.
- Do not scrape an exam the user did not select. One run per explicit choice.
- Mirror the user's language. This skill is a tool driver, not content for the Spanish
  audience — there is no Spanish-output rule here, unlike `topic-miner` and `anti-slop`.

---

## When upstream changes

This skill is pinned to the shape of a third-party repo, and two things have already
drifted: the absolute-href parser bug and the `.bat`-only install path. When a scrape
breaks, check in this order: preflight 2 (parser vs live HTML), then `main.py`'s prompt
flow, then `settings.py` for a renamed output pattern.

Upstream commit this was written against: `b3c6785`. Re-read `main.py` and
`examtopics/parsers.py` after any `git pull` in that repo.
