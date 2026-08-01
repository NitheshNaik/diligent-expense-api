# AI_NOTES.md

I initialized the project structure myself and committed the initial scaffold to GitHub. From there, I used an AI coding agent with staged prompts, one
stage per commit, to build the project incrementally, reviewing and testing
each stage before moving to the next.

## 1. Which parts were AI-generated vs. written by me

**AI-generated boilerplate, prompted and reviewed by me:**
- Stage 1: project scaffold (`src/`, `tests/`, `README.md`,`AI_NOTES.md`, `requirements.txt`), structure only, no logic.
- Stage 2: `Expense` / `ExpenseCreate` Pydantic models, in-memory store, and `POST /expenses`.
- Stage 3: `GET /expenses` with optional `?category=` filtering.
- Stage 4: total endpoints (overall and by category).
- Stage 5: `DELETE /expenses/{id}`.

I wrote each stage's prompt myself rather than generating the whole app in
one go, specifically so I could review and test every piece before building
on top of it.

**Stage 6 onward — AI-assisted, but decisions were mine:**
- Stage 6: README install/run/test commands, AI drafted the wording, but I
 personally cloned the repo into a fresh folder and ran every command
 exactly as written to confirm it worked on a clean checkout.
- Stage 6.1: validation hardening (malformed dates, empty titles, negative
  amounts, empty-store behavior).
- Stage 6.2: Swagger/OpenAPI polish (titles, field examples, route
  descriptions) — no behavior change, docs only.
- Stage 6.3: `.gitignore`, pinned `requirements.txt` versions, and a GitHub
  Actions workflow to run pytest on every push.
- Stage 6.4: the idea for a minimal static `ui/index.html` page was mine, I
  wanted a lightweight way to exercise the API without touching `src/`, so I
  asked the AI to build only that, kept outside `src/` on purpose so it
  can't interfere with how the core API is graded.

## 2. What I validated, tested, or changed

- I manually exercised every endpoint (add, list, filter, totals, delete)
  against the running server at each stage.
- I ran the full `pytest` suite locally after every stage and confirmed all
  tests passed before committing.
- category filtering was case-sensitive at first; I had it corrected to normalize case before comparing.
- Before submitting, I did a clean `git clone` into a separate folder and ran
  the README's install/run/test commands verbatim to make sure they work
  for a reviewer with no prior context.

## 3. AI suggestions I chose not to use

- The AI suggested adding a `scripts/` folder with `start.sh` / `stop.sh`
  convenience scripts for managing the venv and server. I decided against
  this, it added extra moving parts that weren't requested.