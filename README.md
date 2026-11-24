# StudySwap

Pairs students who can teach each other, then gives them exactly what to do in their first session.

Built for the CSC Winter Sparkathon (Nov 2026). The full build plan is in [PLAN.md](PLAN.md).

> Status: **Phase 0 (setup)**. The matching engine from Phase 1 is already in `api/app/matching.py` with tests.
> A clickable design prototype (fake data, no backend) is in [`prototype/index.html`](prototype/index.html). Open it in a browser.

## Repo layout

```
web/          Next.js + TypeScript + Tailwind frontend
api/          FastAPI backend (matching, sessions, AI plans)
supabase/     SQL migrations (schema + Row Level Security)
scripts/      seed data + greedy vs. max-weight comparison
docs/         DECISIONS.md and AI_USE.md
prototype/    single-file clickable prototype
```

## Run it locally

You need **Python 3.11+** and **Node 20+**.

### API (port 8000)

```bash
cd api
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in values
uvicorn app.main:app --reload --port 8000
```

Check it: open http://localhost:8000/health and you should see `{"status":"ok"}`.

Run the tests:

```bash
cd api
pytest
```

### Web (port 3000)

```bash
cd web
npm install
cp .env.example .env.local  # then fill in values
npm run dev
```

Open http://localhost:3000.

### Database (Supabase)

1. Create a free project at supabase.com.
2. Open **SQL Editor**, paste `supabase/migrations/20261124000000_init.sql`, and run it.
   (Or with the Supabase CLI: `supabase link` then `supabase db push`.)
3. Copy the project URL and keys into `api/.env` and `web/.env.local`.

## Safety

- Sign-in only with an allowed school email domain.
- Only first names are shown. We never collect age, last name, phone, photo, or location.
- Both students must accept a match before a session can start.
- Calls are voice-first: camera is off by default. Rooms are private, max 2 people, and expire after 2 hours.
- Report and Block are always one click away. Blocked pairs are never matched again.
- No direct messaging outside a session.
- The demo uses seeded fake students only.

## AI use

See [docs/AI_USE.md](docs/AI_USE.md).
