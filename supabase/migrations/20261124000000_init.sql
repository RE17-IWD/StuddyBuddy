-- StudySwap initial schema (PLAN.md section 6) + Row Level Security.
-- The FastAPI backend uses the service-role key, which bypasses RLS,
-- for matching and session creation. These policies only govern what
-- a signed-in student can do directly with the anon key.

create extension if not exists pgcrypto;

-- ---------- Tables ----------

create table schools (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  email_domain text not null unique
);

-- We deliberately do NOT store age, birthday, last name, phone, photo, or location.
create table profiles (
  id             uuid primary key references auth.users (id) on delete cascade,
  first_name     text not null check (char_length(first_name) between 1 and 40),
  school_id      uuid references schools (id),
  pref_noise     text check (pref_noise in ('quiet', 'talk')),
  pref_time      text check (pref_time in ('morning', 'afternoon', 'evening')),
  pref_camera_on boolean not null default false,
  is_demo        boolean not null default false,
  created_at     timestamptz not null default now()
);

create table courses (
  id        uuid primary key default gen_random_uuid(),
  school_id uuid not null references schools (id) on delete cascade,
  name      text not null
);

create table units (
  id        uuid primary key default gen_random_uuid(),
  course_id uuid not null references courses (id) on delete cascade,
  name      text not null,
  position  int not null
);

create table enrollments (
  user_id   uuid not null references profiles (id) on delete cascade,
  course_id uuid not null references courses (id) on delete cascade,
  primary key (user_id, course_id)
);

-- 1 = weak, 2 = ok, 3 = strong
create table unit_ratings (
  user_id uuid not null references profiles (id) on delete cascade,
  unit_id uuid not null references units (id) on delete cascade,
  rating  smallint not null check (rating in (1, 2, 3)),
  primary key (user_id, unit_id)
);

-- Local school time; everyone at one school shares a time zone (see DECISIONS.md).
create table availability (
  user_id uuid not null references profiles (id) on delete cascade,
  day     smallint not null check (day between 0 and 6),
  hour    smallint not null check (hour between 8 and 21),
  primary key (user_id, day, hour)
);

create table matches (
  id         uuid primary key default gen_random_uuid(),
  course_id  uuid not null references courses (id) on delete cascade,
  user_a     uuid not null references profiles (id) on delete cascade,
  user_b     uuid not null references profiles (id) on delete cascade,
  score      real not null,
  breakdown  jsonb not null,
  a_accepted boolean,
  b_accepted boolean,
  status     text not null default 'proposed'
             check (status in ('proposed', 'active', 'declined', 'ended')),
  created_at timestamptz not null default now(),
  check (user_a <> user_b)
);
create index matches_user_a_idx on matches (user_a);
create index matches_user_b_idx on matches (user_b);

create table sessions (
  id              uuid primary key default gen_random_uuid(),
  match_id        uuid not null references matches (id) on delete cascade,
  daily_room_name text,
  tldraw_room_id  uuid not null default gen_random_uuid(),
  plan            jsonb,
  started_at      timestamptz not null default now(),
  ended_at        timestamptz
);

create table session_feedback (
  session_id uuid not null references sessions (id) on delete cascade,
  user_id    uuid not null references profiles (id) on delete cascade,
  helpful    smallint check (helpful between 1 and 5),
  learned    text check (char_length(learned) <= 500),
  primary key (session_id, user_id)
);

create table reports (
  id         uuid primary key default gen_random_uuid(),
  reporter   uuid not null references profiles (id) on delete cascade,
  reported   uuid not null references profiles (id) on delete cascade,
  session_id uuid references sessions (id) on delete set null,
  reason     text not null,
  created_at timestamptz not null default now()
);

create table blocks (
  blocker uuid not null references profiles (id) on delete cascade,
  blocked uuid not null references profiles (id) on delete cascade,
  primary key (blocker, blocked),
  check (blocker <> blocked)
);

-- ---------- Row Level Security ----------

alter table schools          enable row level security;
alter table profiles         enable row level security;
alter table courses          enable row level security;
alter table units            enable row level security;
alter table enrollments      enable row level security;
alter table unit_ratings     enable row level security;
alter table availability     enable row level security;
alter table matches          enable row level security;
alter table sessions         enable row level security;
alter table session_feedback enable row level security;
alter table reports          enable row level security;
alter table blocks           enable row level security;

-- Catalog data: any signed-in user can read it.
create policy "read schools" on schools for select to authenticated using (true);
create policy "read courses" on courses for select to authenticated using (true);
create policy "read units"   on units   for select to authenticated using (true);

-- Own profile only. Partner first names are served by the API, not read directly.
create policy "own profile select" on profiles for select to authenticated using (id = auth.uid());
create policy "own profile insert" on profiles for insert to authenticated with check (id = auth.uid());
create policy "own profile update" on profiles for update to authenticated using (id = auth.uid()) with check (id = auth.uid());

-- Own onboarding data: full read/write.
create policy "own enrollments" on enrollments for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "own ratings" on unit_ratings for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "own availability" on availability for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

-- Matches and sessions: read only if you are in them. All writes go through the API.
create policy "my matches" on matches for select to authenticated
  using (auth.uid() in (user_a, user_b));
create policy "my sessions" on sessions for select to authenticated
  using (exists (
    select 1 from matches m
    where m.id = sessions.match_id and auth.uid() in (m.user_a, m.user_b)
  ));

-- Feedback: your own rows only.
create policy "own feedback" on session_feedback for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

-- Reports: you can file one, but you can't read anyone's (admins use the service role).
create policy "file report" on reports for insert to authenticated with check (reporter = auth.uid());

-- Blocks: create and see your own.
create policy "own blocks select" on blocks for select to authenticated using (blocker = auth.uid());
create policy "own blocks insert" on blocks for insert to authenticated with check (blocker = auth.uid());
