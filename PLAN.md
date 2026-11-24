# StudySwap — Build Plan

> **For Claude Code:** This file is the source of truth for the project. Read it fully before writing code. Work **one phase at a time**, in order. At the end of each phase: run the checks listed under "Done when", summarize what you built in plain language (the team must be able to explain every part to judges), and **stop and wait for review** before starting the next phase. Keep code simple and readable over clever. Never commit secrets.

*"StudySwap" is a placeholder name. Rename it everywhere in Phase 0 if the team picks another.*

---

## 1. Context

**Event:** CSC Winter Sparkathon (Devpost, ages 13–18).
**Theme:** Build technology that brings people together or helps people support one another.
**Deadline:** Submit by **Sun Nov 29, 2026**. Treat Sat Nov 28 as the real finish line.
**Judging:** Learning, Design, Creativity, Functionality, Impact (no weights given).
**Rules that affect the build:**
- Substantial development must happen during the hackathon period (all code is new).
- No collecting private or sensitive info from real users without permission. **Demo with seeded fake students.**
- Must not promote unsafe behavior. That matters because we put teens on video calls (see section 7).
- The project must be open source / publicly viewable if we opt in to awards. Keep the repo clean.
- AI use is allowed but must be disclosed, and the team must be able to explain the code.

## 2. The product in one paragraph

Most study buddy apps pair students who are *similar*. StudySwap pairs students who are **opposites**: within the same course, it matches someone strong in a unit with someone weak in it, *and the other way around*, so each person teaches the other something. It also checks that their schedules overlap and their study styles fit. It finds the best pairing for the whole class at once (**maximum weight matching**), explains every match in plain words, and then hands the pair a **ready-made 45-minute session**: an online room with voice/video and a shared whiteboard that already has an AI-written plan and practice problems on it, with a timer that walks them through who teaches what.

**One-line pitch:** *"It pairs students who can teach each other, then gives them exactly what to do in their first session."*

## 3. Core user flow

1. **Sign in** with a school email (magic link). Only allowed school domains can join.
2. **Onboarding** (one short multi-step form):
   - First name only
   - Pick course(s)
   - Rate each unit of the course: **Weak / OK / Strong**
   - Weekly availability grid (click hour blocks)
   - Study style: quiet vs. talkative, morning / afternoon / evening, camera on vs. off by default
3. **Matching** runs per course and pairs everyone at once.
4. **Match card** on the dashboard, with the reasons spelled out:
   *"You're strong in Limits and Derivatives, and Sam is strong in Integrals. You're both free Tue 4–6pm and both like quiet study."* Buttons: **Accept / Decline**. A match only becomes active when **both** accept.
5. **Start session** opens the session room:
   - Left: Daily video/voice call (**camera off by default**)
   - Right: tldraw whiteboard **preloaded with the AI session plan and practice problems**
   - Top: segment timer ("Segment 2 of 3: Sam teaches Integrals, 12:04 left") with a "Next segment" button
   - Report/Block button always visible
6. **End session**: a quick feedback form (helpful 1–5, "what did you learn?" optional). This gives us Impact numbers for the Devpost writeup.

## 4. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js (App Router) + TypeScript + Tailwind** | Fast to build, easy deploy on Vercel |
| Backend | **FastAPI (Python 3.11+)** | Matching uses `networkx`, which is Python |
| DB + Auth | **Supabase** (Postgres + email magic-link auth) | Free tier, auth built in |
| Matching | **networkx** `max_weight_matching` | Best total pairing for the whole class |
| Video | **Daily Prebuilt** (`@daily-co/daily-js`) | Embeddable, 10,000 free participant-minutes/month |
| Whiteboard | **tldraw** + `@tldraw/sync` (`useSyncDemo`) | Multiplayer whiteboard with almost no backend |
| AI | Any chat LLM with JSON output (we have **Backboard** credits) | Session plans and practice problems |
| Hosting | Vercel (web) + Render or Railway (api) | Free tiers |
| Domain | Free `.xyz` from Gen.xyz | Real URL for the demo |

**LLM note:** Wrap all LLM calls in one module (`api/app/llm.py`) with `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` env vars, using an OpenAI-compatible chat API if available. **Check Backboard's docs for its actual API before wiring it up. Do not guess endpoints.** If Backboard doesn't fit, any provider works behind the same module.

**tldraw note:** Development needs no license key. For the deployed demo, request a free **hobby license** (non-commercial; the "made with tldraw" watermark stays) and set `NEXT_PUBLIC_TLDRAW_LICENSE_KEY`. `useSyncDemo` uses tldraw's hosted demo sync server. It's fine for a hackathon, but use **unguessable room IDs (UUIDs)** and never put personal info on the board. Check the installed tldraw version's docs for how note/text shapes take text (newer versions use `richText` with a `toRichText()` helper).

**Daily note:** Create **private** rooms server-side via the Daily REST API, and give each participant a **meeting token** created server-side. Never expose `DAILY_API_KEY` to the browser.

## 5. Repo structure

```
/
├─ PLAN.md                  ← this file
├─ README.md                ← setup + run instructions (Phase 0), project summary (Phase 7)
├─ docs/
│  ├─ DECISIONS.md          ← short log of every important design decision and why
│  └─ AI_USE.md             ← running log of how AI was used (for the Devpost disclosure)
├─ web/                     ← Next.js app
│  ├─ app/
│  │  ├─ page.tsx                  landing
│  │  ├─ login/page.tsx
│  │  ├─ onboarding/page.tsx
│  │  ├─ dashboard/page.tsx
│  │  ├─ session/[id]/page.tsx
│  │  └─ admin/page.tsx            dev/demo tools only
│  ├─ components/
│  └─ lib/ (supabase client, api client)
├─ api/                     ← FastAPI app
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ auth.py            verify Supabase JWT
│  │  ├─ db.py
│  │  ├─ matching.py        scoring + max weight matching (pure functions, no DB)
│  │  ├─ explain.py         match explanation text (template, NOT LLM)
│  │  ├─ plan.py            AI session plan (+ fallback template)
│  │  ├─ daily.py           Daily room + token helpers
│  │  └─ llm.py
│  └─ tests/
│     ├─ test_matching.py
│     └─ test_plan.py
├─ scripts/
│  ├─ seed.py               fake school, courses, units, ~40 students
│  └─ compare_matching.py   greedy vs. max-weight stats for the writeup
└─ supabase/migrations/     SQL schema
```

## 6. Data model (Postgres / Supabase)

```sql
schools        (id uuid pk, name text, email_domain text unique)
profiles       (id uuid pk = auth.users.id, first_name text, school_id uuid fk,
                pref_noise text check in ('quiet','talk'),
                pref_time  text check in ('morning','afternoon','evening'),
                pref_camera_on bool default false,
                is_demo bool default false, created_at timestamptz)
courses        (id uuid pk, school_id uuid fk, name text)              -- e.g. 'AP Calculus AB'
units          (id uuid pk, course_id uuid fk, name text, position int)
enrollments    (user_id uuid fk, course_id uuid fk, pk(user_id, course_id))
unit_ratings   (user_id uuid fk, unit_id uuid fk, rating smallint check in (1,2,3),  -- 1 weak, 2 ok, 3 strong
                pk(user_id, unit_id))
availability   (user_id uuid fk, day smallint 0-6, hour smallint 8-21, pk(user_id, day, hour))
matches        (id uuid pk, course_id uuid fk, user_a uuid, user_b uuid,
                score real, breakdown jsonb,          -- {swap, schedule, style, overlap_hours, a_teaches[], b_teaches[], shared_slots[]}
                a_accepted bool null, b_accepted bool null,
                status text check in ('proposed','active','declined','ended'),
                created_at timestamptz)
sessions       (id uuid pk, match_id uuid fk, daily_room_name text, tldraw_room_id uuid,
                plan jsonb, started_at timestamptz, ended_at timestamptz)
session_feedback (session_id uuid fk, user_id uuid fk, helpful smallint 1-5, learned text,
                pk(session_id, user_id))
reports        (id uuid pk, reporter uuid, reported uuid, session_id uuid null, reason text, created_at timestamptz)
blocks         (blocker uuid, blocked uuid, pk(blocker, blocked))
```

- Assume everyone at one school shares a time zone; store availability as local day/hour. Note this in DECISIONS.md.
- Enable Row Level Security. Users can read/write their own profile, ratings, availability, and feedback, and can read matches/sessions they're part of. The FastAPI backend uses the service-role key for matching and session creation.
- **Do not collect** age, birthday, last name, phone, photo, or location.

## 7. Safety and privacy (required, judges will ask)

- **School email only:** sign-in limited to `ALLOWED_EMAIL_DOMAINS`.
- **First names only** are shown anywhere.
- **Mutual opt-in:** a session can't start until both students accept the match.
- **Camera off by default** (`start_video_off: true`); voice + whiteboard is the default mode.
- **Private Daily rooms** with server-issued meeting tokens, max 2 participants, expiring after 2 hours.
- **Report and Block** buttons in the session room and on the match card. A blocked pair is never matched again.
- **No direct messaging** outside a session.
- Unguessable tldraw room IDs. The board holds only the study plan and work.
- **Demo uses seeded fake students only.** Real testers must agree first.
- A short "Safety" section on the landing page and in the README.

## 8. Matching algorithm (the core; keep it in pure functions and test it)

For each course, build a graph where each eligible student is a node. For each pair (a, b):

**Skip the pair (no edge)** if: they share fewer than 1 free hour, either has blocked the other, or they previously declined each other.

**Swap score**, the heart of the idea:
- `a_teaches` = units where a is Strong (3) and b is Weak (1)
- `b_teaches` = units where b is Strong and a is Weak
- Also count "Strong vs OK" as half a point each way.
- `swap_raw = min(|a_teaches|, |b_teaches|) * 2 + max(|a_teaches|, |b_teaches|)`
  (two-way swaps are worth much more than one-way tutoring)
- Normalize: `swap = min(swap_raw / 6, 1.0)`

**Schedule score:** `schedule = min(overlap_hours, 6) / 6`

**Style score:** +0.5 if `pref_noise` matches, +0.5 if `pref_time` matches → `style` in [0, 1]

**Total:** `score = 0.6 * swap + 0.25 * schedule + 0.15 * style`

Then run `networkx.max_weight_matching(G, maxcardinality=False)` and store each pair as a `proposed` match with its `breakdown`. A student left unmatched (odd count or no edges) sees: *"No great match yet. We'll pair you when more classmates join."*

**Why not greedy?** Greedy takes the single best pair first, then the next best, and so on. That can strand people. Example (put it in a test and in DECISIONS.md):
- A–B = 10, A–C = 9, B–D = 9, C–D = no edge
- Greedy picks A–B (10), and then C and D can't be paired → total 10, **2 students unmatched**
- Max weight picks A–C + B–D → total 18, **everyone matched**

`scripts/compare_matching.py` runs both on the seeded data and prints: students matched, total score, average swap score. **Put these numbers in the Devpost writeup.**

**Explanations** (`explain.py`): build them from `breakdown` with a template, not an LLM, so they're always accurate. Example output:
*"You're strong in Limits and Derivatives, and Sam is strong in Integrals and Series. You're both free Tue 4–6pm and Thu 5–6pm. You both prefer quiet study in the afternoon."*

## 9. AI session plan (`plan.py`)

**Input:** course name, both first names, units each person teaches (from `breakdown`), duration 45 min.
**Output:** JSON validated with Pydantic:

```json
{
  "title": "Limits ⇄ Integrals swap",
  "segments": [
    {"minutes": 5,  "leader": "both", "unit": null,        "goal": "Warm-up: each person says what confuses them most"},
    {"minutes": 17, "leader": "Alex", "unit": "Limits",    "goal": "...", "problems": ["...", "...", "..."]},
    {"minutes": 17, "leader": "Sam",  "unit": "Integrals", "goal": "...", "problems": ["...", "...", "..."]},
    {"minutes": 6,  "leader": "both", "unit": null,        "goal": "Quiz each other: one problem each, then plan next session"}
  ]
}
```

- Prompt rules: high-school level, problems **without answers** (the teacher-student works them out), 3 problems per teaching segment, no personal info.
- Validate; on invalid JSON retry once; on second failure use a **fallback template plan** (same structure, generic goals, no problems). The session must never fail because of the LLM.
- Label problems on the board as "AI-generated: double-check with your notes."

## 10. Session room (`/session/[id]`)

- Layout: call panel on the left (about 35% width), whiteboard on the right (about 65%), timer bar on top. On narrow screens, stack them.
- **Call:** `DailyIframe.createFrame(container, { url, token, showLeaveButton: true })`. Room and token come from `GET /api/sessions/{id}`.
- **Whiteboard:** `useSyncDemo({ roomId: tldraw_room_id })` → `<Tldraw store={store} onMount={...} />`. On mount, **if the board is empty**, create note shapes for each segment (title, leader, goal, problems) laid out left to right. Check for existing shapes first so two people joining doesn't create duplicates.
- **Timer:** driven by `plan.segments`; shows current segment, leader, and countdown; "Next segment" button; gentle chime at the end of each segment. (A per-client timer is fine for the MVP; syncing is a stretch goal.)
- **Report/Block** button opens a small modal and calls the API.
- **End session** → `POST /api/sessions/{id}/end` → feedback form → dashboard.

## 11. API endpoints (FastAPI)

All require a Supabase JWT except `/health`. Check that the caller belongs to the match or session.

| Method | Path | Does |
|---|---|---|
| GET | `/health` | ok |
| POST | `/api/match/run` `{course_id}` | Runs matching for unmatched enrolled students in that course (admin/demo only) |
| GET | `/api/matches/me` | My matches with explanation text |
| POST | `/api/matches/{id}/respond` `{accept: bool}` | Sets my acceptance; both accept → `active`; any decline → `declined` |
| POST | `/api/sessions` `{match_id}` | Match must be `active`. Creates the Daily private room, tldraw room UUID, and AI plan; returns session id |
| GET | `/api/sessions/{id}` | Plan, tldraw room id, Daily room URL, **a meeting token for the caller** |
| POST | `/api/sessions/{id}/end` | Sets ended_at |
| POST | `/api/sessions/{id}/feedback` | Saves feedback |
| POST | `/api/reports` | Creates a report |
| POST | `/api/blocks` | Creates a block; ends any active match between the pair |
| GET | `/api/stats` | Totals for the landing page / admin: students, matches, sessions, avg helpfulness |

## 12. Demo mode (judges must be able to try it)

- `/admin` page (protected by an `ADMIN_EMAILS` env var or a `DEMO_MODE=true` flag): **Seed data**, **Run matching** per course, **Compare greedy vs. max-weight** (shows the stats), and **Log in as demo student** (pick from seeded students).
- A **"Try the demo"** button on the landing page that signs in as a seeded demo account with a match already accepted, so a judge can open a session room in 2 clicks.
- Seed data (`scripts/seed.py`): 1 school, 3 courses (AP Calculus AB with 8 real unit names, AP Chemistry, AP Biology), about 40 fake students with first names only, realistic availability (mostly after-school blocks), and unit ratings with deliberate variety so complementary pairs exist.

## 13. Environment variables

```
# web/.env.local
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_TLDRAW_LICENSE_KEY=

# api/.env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
DAILY_API_KEY=
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
ALLOWED_EMAIL_DOMAINS=school.org
ADMIN_EMAILS=
DEMO_MODE=true
```

Add `.env*` to `.gitignore` and provide `.env.example` files.

---

## 14. Phases (do them in order; stop after each)

### Phase 0: Setup (Mon night / Tue morning)
- Scaffold `web/` (Next.js + TS + Tailwind) and `api/` (FastAPI, `requirements.txt` with fastapi, uvicorn, networkx, pydantic, supabase, httpx, python-dotenv, pytest).
- `.gitignore`, `.env.example` files, README with run instructions, empty `docs/DECISIONS.md` and `docs/AI_USE.md`.
- Supabase migration with the full schema from section 6 plus RLS policies.
- `/health` works; the web app shows a placeholder landing page.
- **Done when:** both apps run locally with one command each, and the migration applies cleanly.

### Phase 1: Matching engine (Tue). *Most important phase.*
- `matching.py` as pure functions: `pair_score(a, b) -> (score, breakdown) | None`, `build_graph(students)`, `match(students) -> list[pairs]`, `greedy_match(students)` (for comparison only).
- `explain.py` template explanations.
- `tests/test_matching.py`: no edge without schedule overlap; blocked pairs excluded; two-way swap beats one-way; the greedy-vs-optimal example from section 8; odd count leaves exactly one unmatched.
- `scripts/seed.py` and `scripts/compare_matching.py`.
- **Done when:** `pytest` passes and `compare_matching.py` prints a clear comparison table on the seeded data.

### Phase 2: Auth and onboarding (Tue–Wed)
- Supabase magic-link login, rejecting emails outside `ALLOWED_EMAIL_DOMAINS` (check in the UI and in the API).
- Multi-step onboarding: name → courses → unit ratings (three-button Weak/OK/Strong per unit) → availability grid (click/drag hour cells, Mon–Sun 8am–10pm) → style prefs.
- Saves to the DB; returning users skip onboarding.
- **Done when:** a new user can sign in and finish onboarding in under 2 minutes, and the data appears correctly in the DB.

### Phase 3: Matches and dashboard (Wed)
- Endpoints: `/api/match/run`, `/api/matches/me`, `/api/matches/{id}/respond`.
- Dashboard: course list, match card (partner first name, score as a simple "great / good match" label, explanation text, shared free times), Accept/Decline, status states (waiting for partner, active → "Start session").
- `/admin` page with seed, run matching, compare stats, and log in as demo student.
- **Done when:** with seeded data you can run matching, log in as two students, accept on both, and see "Start session".

### Phase 4: AI session plan (Thu, light day)
- `llm.py`, `plan.py` with Pydantic validation, retry, and fallback.
- `tests/test_plan.py`: fallback is used when the LLM returns garbage; output always matches the schema.
- **Done when:** creating a session stores a valid plan every time, including with the LLM disabled.

### Phase 5: Session room (Fri). *Riskiest phase; a teammate can prototype it in parallel from Tue.*
- `daily.py`: create a private room (max 2 participants, `start_video_off`, 2-hour expiry) and create meeting tokens.
- `POST /api/sessions`, `GET /api/sessions/{id}`, `/end`, `/feedback`.
- `/session/[id]` page: Daily frame + tldraw board with the plan preloaded (no duplicates) + segment timer + Report/Block + End → feedback.
- **Done when:** two browsers (one normal, one incognito, logged in as the two matched demo students) join the same session, hear each other, see each other's cursors on the board, and the plan appears once.

### Phase 6: Safety, polish, and demo (Sat morning)
- Report/Block endpoints and UI; blocked pairs are excluded from matching (already tested).
- Landing page: pitch, 3-step "how it works", Safety section, live stats from `/api/stats`, **Try the demo** button.
- Visual polish: consistent colors, friendly empty states, loading states, mobile-OK dashboard.
- Deploy: web to Vercel, api to Render/Railway, `.xyz` domain, tldraw hobby license key set.
- **Done when:** a stranger can open the deployed URL, click "Try the demo", and reach a working session room without help.

### Phase 7: Submission materials (Sat afternoon)
- README: what it is, screenshots, how matching works (with the greedy example), safety design, tech stack, setup.
- Fill out `docs/AI_USE.md` and turn it into the Devpost AI disclosure (see section 16).
- Make sure the repo is public and clean (no secrets, no dead code).
- **Done when:** everything in section 15 is ready.

### Stretch goals (only if everything above is done)
- Synced timer across both clients (store segment start time in the session row).
- Groups of 3 for odd counts.
- "Next session" plan built from the feedback.
- Trust signal: a "sessions completed" count on match cards.

### If behind schedule, cut in this order
1. Stretch goals
2. Feedback form (keep the End button)
3. Timer chime / mobile layout
4. Auth via magic link → replace with the demo login only (keep the school-domain check in the writeup as designed)

**Never cut:** the opposites matching, match explanations, the session room with the preloaded plan, and the safety basics.

---

## 15. Devpost submission checklist

- [ ] Project name
- [ ] Problem (2–3 sentences): students who struggle often won't ask for help; generic study buddy apps pair similar students, so nobody can teach anybody; and matched pairs often never meet or don't know what to do when they do.
- [ ] What it does (the one-paragraph description from section 2)
- [ ] Demo link (`.xyz` domain) + GitHub repo + 1–2 min video + screenshots
- [ ] Tools list: Next.js, TypeScript, Tailwind, FastAPI, Python, networkx, Supabase, Daily, tldraw, [LLM provider], Vercel, Render/Railway, Gen.xyz
- [ ] AI-use disclosure (section 16)
- [ ] Team member names
- [ ] Greedy vs. max-weight numbers from `compare_matching.py`
- [ ] Results from real testers (with their permission): sessions run, average helpfulness
- [ ] Opt in to awards

## 16. AI-use disclosure (template; fill in honestly)

> We used AI in two ways. **In the product:** an LLM writes each pair's 45-minute session plan and practice problems. Match scores and explanations are computed by our own code, not AI, so they're always accurate. **While building:** we used Claude (including Claude Code) to help plan the architecture, write and debug code, and draft documentation. We reviewed all code, wrote and ran the tests ourselves, and can explain every part, especially the matching algorithm (scoring, and why maximum weight matching beats greedy). [Add specifics: which parts each teammate wrote or changed by hand.]

## 17. 90-second demo video script

- **0–10s:** "Study buddy apps pair students who are the same. But if you're both bad at integrals, who teaches who?"
- **10–30s:** Onboarding: rate units, click availability.
- **30–45s:** Match card: "You're strong in Limits, Sam's strong in Integrals, you're both free Tuesday at 4." Both accept.
- **45–75s:** Session room: call connects, whiteboard already has the plan, timer says "Alex teaches Limits," cursors working the problem together.
- **75–85s:** The greedy vs. max-weight comparison: "our matching pairs X% more students."
- **85–90s:** Safety in one line: school emails, first names, camera off by default, report/block.

## 18. Working agreements for Claude Code

- One phase at a time; stop for review after each.
- After each phase, add 2–5 lines to `docs/DECISIONS.md` (what we chose and why) and to `docs/AI_USE.md` (what AI helped with).
- Prefer simple, well-named functions over abstractions. Comment the *why*, not the *what*.
- Matching and plan logic stay as pure, tested functions.
- Never hardcode keys. Never log tokens or emails.
- If a library's API differs from this plan (tldraw, Daily, Backboard), check its current docs, follow the docs, and note the change in DECISIONS.md.
- Ask before adding any new paid service or collecting any new kind of user data.
