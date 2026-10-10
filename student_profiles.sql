create table public.student_profiles (
    student_id text primary key,
    name text default '',
    current_level integer default 1,
    current_topic text default '',
    completed_topics jsonb default '[]'::jsonb,
    weak_topics jsonb default '[]'::jsonb,
    strong_topics jsonb default '[]'::jsonb,
    xp integer default 0,
    streak_days integer default 0,
    learning_state text default 'NOT_STARTED',
    learning_memory jsonb default '{}'::jsonb,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);
