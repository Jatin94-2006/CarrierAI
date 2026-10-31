-- SQL Schema for Supabase PostgreSQL Database
-- Run this script in your Supabase Project's SQL Editor

-- 1. Create interviews table
create table if not exists public.interviews (
  id uuid primary key default gen_random_uuid(),
  role text not null,
  candidate_name text not null,
  status text not null default 'in_progress', -- 'in_progress', 'completed', 'abandoned'
  total_questions integer not null default 0,
  answered_count integer not null default 0,
  skipped_count integer not null default 0,
  questions jsonb not null default '[]'::jsonb,
  items jsonb not null default '[]'::jsonb,
  raw_output jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Enable Row Level Security (RLS)
alter table public.interviews enable row level security;

-- 3. Policy to allow all operations with Supabase anon/service role key
create policy "Allow access to interviews"
  on public.interviews
  for all
  using (true)
  with check (true);

-- 4. Automatically update updated_at timestamp on row modification
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_interviews_updated_at on public.interviews;
create trigger set_interviews_updated_at
  before update on public.interviews
  for each row
  execute procedure public.handle_updated_at();
