"""
Supabase Client — Shared DB connection for all modules.
Project ID: yvdpybqlvjgemcltqhjn
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_supabase() -> Client:
    """
    Returns a singleton Supabase client.
    Reads SUPABASE_URL and SUPABASE_ANON_KEY from environment.
    """
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env\n"
                f"  SUPABASE_URL={url}\n"
                f"  SUPABASE_ANON_KEY={'set' if key else 'MISSING'}"
            )

        _client = create_client(url, key)
    return _client


# ─── DB Helper Functions ──────────────────────────────────────────────────────

def insert_row(table: str, data: dict) -> dict:
    """Insert a row into a Supabase table and return the inserted row."""
    client = get_supabase()
    response = client.table(table).insert(data).execute()
    if response.data:
        return response.data[0]
    raise RuntimeError(f"Insert to '{table}' failed: {response}")


def fetch_row(table: str, match: dict) -> dict | None:
    """Fetch a single row from a Supabase table matching given columns."""
    client = get_supabase()
    query = client.table(table).select("*")
    for col, val in match.items():
        query = query.eq(col, val)
    response = query.limit(1).execute()
    if response.data:
        return response.data[0]
    return None


def fetch_rows(table: str, match: dict) -> list[dict]:
    """Fetch all rows from a Supabase table matching given columns."""
    client = get_supabase()
    query = client.table(table).select("*")
    for col, val in match.items():
        query = query.eq(col, val)
    response = query.execute()
    return response.data or []


def update_row(table: str, match: dict, updates: dict) -> dict:
    """Update rows in a Supabase table and return updated row."""
    client = get_supabase()
    query = client.table(table).update(updates)
    for col, val in match.items():
        query = query.eq(col, val)
    response = query.execute()
    if response.data:
        return response.data[0]
    raise RuntimeError(f"Update on '{table}' failed: {response}")
