# AI use log

Running log of how AI was used, for the Devpost disclosure (PLAN.md section 16).
Add a line every phase: what the AI did, and what we checked or changed by hand.

## Phase 0: Setup

- Claude Code reviewed PLAN.md and listed gaps (demo login safety, school email filters, the "nobody teaches" scoring hole, duplicate first names, report handling).
- Claude Code scaffolded the repo: FastAPI app with `/health`, Next.js app, Supabase migration with RLS, README, and these docs.
- Claude Code built a clickable prototype (`prototype/index.html`) with fake data to show the flow before the real app exists.

## Phase 1 head start: Matching

- Claude Code wrote `api/app/matching.py` and `api/tests/test_matching.py` from the rules in PLAN.md section 8.
- TODO (team): read through `matching.py` line by line, run `pytest`, and be ready to explain the swap score and why max-weight beats greedy.
