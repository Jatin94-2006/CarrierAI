-- ============================================================
-- AI Career Guidance Platform — Supabase Schema
-- Project ID: yvdpybqlvjgemcltqhjn
-- Run this in Supabase SQL Editor to initialize all tables
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── users ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT UNIQUE NOT NULL,
  full_name   TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- ─── resumes ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resumes (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
  raw_text    TEXT NOT NULL,
  parsed_data JSONB,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- ─── job_descriptions ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_descriptions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
  title       TEXT,
  raw_text    TEXT NOT NULL,
  parsed_data JSONB,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- ─── gap_reports ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gap_reports (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
  resume_id      UUID REFERENCES resumes(id),
  job_id         UUID REFERENCES job_descriptions(id),
  session_id     UUID DEFAULT gen_random_uuid(),
  report_data    JSONB NOT NULL,
  schema_version TEXT DEFAULT '1.0',
  status         TEXT DEFAULT 'completed',
  created_at     TIMESTAMPTZ DEFAULT now()
);

-- ─── course_suggestions ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS course_suggestions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  gap_report_id UUID REFERENCES gap_reports(id),
  courses_data  JSONB NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- ─── interview_sessions ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS interview_sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  gap_report_id UUID REFERENCES gap_reports(id),
  resume_id     UUID REFERENCES resumes(id),
  session_data  JSONB NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- ─── learning_plans ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS learning_plans (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID REFERENCES users(id) ON DELETE CASCADE,
  gap_report_id        UUID REFERENCES gap_reports(id),
  course_suggestion_id UUID REFERENCES course_suggestions(id),
  plan_data            JSONB NOT NULL,
  plan_type            TEXT CHECK (plan_type IN ('30_day', '3_month', '6_month')),
  created_at           TIMESTAMPTZ DEFAULT now()
);
