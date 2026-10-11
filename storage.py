"""Storage with two backends.

By default the app writes to a local SQLite file, which is right for running it
on your own machine and for cognitive interviews.

When a connection string is configured it writes to a Postgres database
instead. That is what a deployed session needs: a hosted Streamlit app has no
permanent filesystem, so a SQLite file there is lost whenever the app restarts.
The connection string comes from `DATABASE_URL`, either as an environment
variable or in Streamlit secrets, and nothing else in the app changes.

Three tables, deliberately kept apart:
  sessions   one row per participant
  responses  one row per screen, with the situation at that moment and the
             time the screen took
  followup   mail address for the questionnaire one week later, linked only by
             the pseudonym code

The follow-up contact lives in its own table so that it can be held separately
from the session data and deleted on its own.
"""

from __future__ import annotations

import csv
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sessions.db"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    code             TEXT PRIMARY KEY,
    started_at       TEXT,
    completed_at     TEXT,
    track            INTEGER,
    seed             INTEGER,
    solo             INTEGER,
    startup_name     TEXT,
    industry         TEXT,
    consent          INTEGER,
    is_founder       INTEGER,
    withdrawn        INTEGER DEFAULT 0,
    app_version      TEXT,
    codebook_version TEXT
);
CREATE TABLE IF NOT EXISTS responses (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    code             TEXT,
    screen_id        TEXT,
    node             TEXT,
    domain           TEXT,
    block_position   INTEGER,
    node_position    INTEGER,
    screen_index     INTEGER,
    option_key       TEXT,
    option_index     INTEGER,
    numeric_value    REAL,
    text_value       TEXT,
    response_seconds REAL,
    state_json       TEXT,
    answered_at      TEXT,
    UNIQUE (code, screen_id)
);
CREATE TABLE IF NOT EXISTS followup (
    code        TEXT PRIMARY KEY,
    email       TEXT,
    created_at  TEXT,
    sent_at     TEXT
);
"""

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    code             TEXT PRIMARY KEY,
    started_at       TEXT,
    completed_at     TEXT,
    track            INTEGER,
    seed             BIGINT,
    solo             INTEGER,
    startup_name     TEXT,
    industry         TEXT,
    consent          INTEGER,
    is_founder       INTEGER,
    withdrawn        INTEGER DEFAULT 0,
    app_version      TEXT,
    codebook_version TEXT
);
CREATE TABLE IF NOT EXISTS responses (
    id               BIGSERIAL PRIMARY KEY,
    code             TEXT,
    screen_id        TEXT,
    node             TEXT,
    domain           TEXT,
    block_position   INTEGER,
    node_position    INTEGER,
    screen_index     INTEGER,
    option_key       TEXT,
    option_index     INTEGER,
    numeric_value    DOUBLE PRECISION,
    text_value       TEXT,
    response_seconds DOUBLE PRECISION,
    state_json       TEXT,
    answered_at      TEXT,
    UNIQUE (code, screen_id)
);
CREATE TABLE IF NOT EXISTS followup (
    code        TEXT PRIMARY KEY,
    email       TEXT,
    created_at  TEXT,
    sent_at     TEXT
);
"""

TABLES = ("sessions", "responses", "followup")


# ---------------------------------------------------------------------------
# Which backend
# ---------------------------------------------------------------------------

def database_url() -> str | None:
    """Connection string, from the environment or from Streamlit secrets."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url.strip() or None
    try:
        import streamlit as st
        value = st.secrets.get("DATABASE_URL")  # type: ignore[attr-defined]
        return str(value).strip() or None if value else None
    except Exception:
        return None


def backend() -> str:
    return "postgres" if database_url() else "sqlite"


def describe() -> str:
    if backend() == "sqlite":
        return f"local SQLite file at {DB_PATH}"
    url = database_url() or ""
    host = url.split("@")[-1].split("/")[0] if "@" in url else "configured host"
    return f"Postgres database at {host}"


def _sql(statement: str) -> str:
    """The SQL is written with ? placeholders; Postgres wants %s."""
    return statement.replace("?", "%s") if backend() == "postgres" else statement


_initialised = False


@contextmanager
def connect():
    """A connection with the schema in place, committed on a clean exit."""
    global _initialised
    if backend() == "postgres":
        import psycopg
        conn = psycopg.connect(database_url())
        try:
            if not _initialised:
                with conn.cursor() as cur:
                    cur.execute(POSTGRES_SCHEMA)
                conn.commit()
                _initialised = True
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=30)
        try:
            conn.executescript(SQLITE_SCHEMA)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def _execute(conn, statement: str, params: tuple = ()) -> None:
    if backend() == "postgres":
        with conn.cursor() as cur:
            cur.execute(_sql(statement), params)
    else:
        conn.execute(statement, params)


def _fetch(conn, statement: str, params: tuple = ()) -> list[dict]:
    if backend() == "postgres":
        with conn.cursor() as cur:
            cur.execute(_sql(statement), params)
            columns = [c.name for c in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    conn.row_factory = sqlite3.Row
    rows = conn.execute(statement, params).fetchall()
    return [dict(r) for r in rows]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def start_session(code: str, track: int, seed: int, app_version: str,
                  codebook_version: str) -> None:
    with connect() as conn:
        _execute(conn,
                 "INSERT INTO sessions "
                 "(code, started_at, track, seed, app_version, codebook_version) "
                 "VALUES (?,?,?,?,?,?) ON CONFLICT (code) DO NOTHING",
                 (code, _now(), track, seed, app_version, codebook_version))


def update_session(code: str, **fields) -> None:
    if not fields:
        return
    assignments = ", ".join(f"{k} = ?" for k in fields)
    with connect() as conn:
        _execute(conn, f"UPDATE sessions SET {assignments} WHERE code = ?",
                 (*fields.values(), code))


def complete_session(code: str) -> None:
    update_session(code, completed_at=_now())


def save_response(code: str, screen: dict, screen_index: int, *,
                  option_key: str | None = None, option_index: int | None = None,
                  numeric_value: float | None = None, text_value: str | None = None,
                  response_seconds: float | None = None,
                  state: dict | None = None) -> None:
    with connect() as conn:
        _execute(
            conn,
            "INSERT INTO responses "
            "(code, screen_id, node, domain, block_position, node_position, "
            " screen_index, option_key, option_index, numeric_value, text_value, "
            " response_seconds, state_json, answered_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT (code, screen_id) DO UPDATE SET "
            " option_key = EXCLUDED.option_key, option_index = EXCLUDED.option_index, "
            " numeric_value = EXCLUDED.numeric_value, text_value = EXCLUDED.text_value, "
            " response_seconds = EXCLUDED.response_seconds, "
            " state_json = EXCLUDED.state_json, answered_at = EXCLUDED.answered_at",
            (code, screen["id"], screen.get("node"), screen.get("domain"),
             screen.get("block_position"), screen.get("node_position"),
             screen_index, option_key, option_index, numeric_value, text_value,
             response_seconds, json.dumps(state) if state else None, _now()))


def save_followup(code: str, email: str) -> None:
    with connect() as conn:
        _execute(conn,
                 "INSERT INTO followup (code, email, created_at) VALUES (?,?,?) "
                 "ON CONFLICT (code) DO UPDATE SET email = EXCLUDED.email",
                 (code, email.strip(), _now()))


def withdraw(code: str) -> None:
    """Mark the data as withdrawn and drop the follow-up contact."""
    with connect() as conn:
        _execute(conn, "UPDATE sessions SET withdrawn = 1 WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM followup WHERE code = ?", (code,))


def delete(code: str) -> int:
    """Remove a participant's data entirely, for a withdrawal by mail.
    Returns the number of session rows removed."""
    with connect() as conn:
        before = _fetch(conn, "SELECT code FROM sessions WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM responses WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM followup WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM sessions WHERE code = ?", (code,))
        return len(before)


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def fetch_responses(code: str) -> list[dict]:
    with connect() as conn:
        return _fetch(conn,
                      "SELECT * FROM responses WHERE code = ? ORDER BY screen_index",
                      (code,))


def fetch_all(table: str) -> list[dict]:
    if table not in TABLES:
        raise ValueError(f"unknown table {table!r}")
    with connect() as conn:
        return _fetch(conn, f"SELECT * FROM {table}")


def counts() -> dict:
    with connect() as conn:
        started = _fetch(conn, "SELECT COUNT(*) AS n FROM sessions")[0]["n"]
        completed = _fetch(
            conn, "SELECT COUNT(*) AS n FROM sessions WHERE completed_at IS NOT NULL"
        )[0]["n"]
        withdrawn = _fetch(
            conn, "SELECT COUNT(*) AS n FROM sessions WHERE withdrawn = 1"
        )[0]["n"]
        answers = _fetch(conn, "SELECT COUNT(*) AS n FROM responses")[0]["n"]
        contacts = _fetch(conn, "SELECT COUNT(*) AS n FROM followup")[0]["n"]
    return {"started": started, "completed": completed, "withdrawn": withdrawn,
            "answers": answers, "followup_contacts": contacts}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def table_csv(table: str) -> str:
    """One table as a CSV string, for the download button on the admin page."""
    rows = fetch_all(table)
    if not rows:
        return ""
    import io
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def export_csv(out_dir: str | Path = "export",
               include_followup: bool = False) -> list[Path]:
    """Write one CSV per table. The follow-up contacts are left out unless
    explicitly asked for, so the usual export carries no contact data."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tables = ["sessions", "responses"] + (["followup"] if include_followup else [])
    written = []
    for table in tables:
        path = out / f"{table}.csv"
        path.write_text(table_csv(table), encoding="utf-8")
        written.append(path)
    return written
