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
  progress   where a running session stands, so that it can be resumed after a
             reload or a lost connection (0.14.0); not part of the analysis

The follow-up contact lives in its own table so that it can be held separately
from the session data and deleted on its own.
"""

from __future__ import annotations

import copy
import csv
import functools
import json
import os
import queue
import sqlite3
import threading
import time
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
    duration_seconds DOUBLE PRECISION,
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
    entered_at       TEXT,
    answered_at      TEXT,
    UNIQUE (code, screen_id)
);
CREATE TABLE IF NOT EXISTS followup (
    code        TEXT PRIMARY KEY,
    email       TEXT,
    created_at  TEXT,
    sent_at     TEXT
);
CREATE TABLE IF NOT EXISTS progress (
    code        TEXT PRIMARY KEY,
    token       TEXT UNIQUE,
    data        TEXT,
    updated_at  TEXT
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
    duration_seconds DOUBLE PRECISION,
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
    entered_at       TEXT,
    answered_at      TEXT,
    UNIQUE (code, screen_id)
);
CREATE TABLE IF NOT EXISTS followup (
    code        TEXT PRIMARY KEY,
    email       TEXT,
    created_at  TEXT,
    sent_at     TEXT
);
CREATE TABLE IF NOT EXISTS progress (
    code        TEXT PRIMARY KEY,
    token       TEXT UNIQUE,
    data        TEXT,
    updated_at  TEXT
);
"""

TABLES = ("sessions", "responses", "followup")

# Columns added after the first release. Older databases get them on first use.
MIGRATIONS = [("responses", "entered_at", "TEXT"),
              ("sessions", "duration_seconds", "DOUBLE PRECISION")]


def _migrate(conn) -> None:
    for table, column, kind in MIGRATIONS:
        if backend() == "postgres":
            with conn.cursor() as cur:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {kind}")
        else:
            cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            if column not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {kind}")


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

# ---------------------------------------------------------------------------
# Postgres: reuse connections instead of opening one per write.
# Opening a TLS connection from Streamlit Cloud (US) to a database in Frankfurt
# takes several round trips; doing that on every click made each page wait.
# ---------------------------------------------------------------------------

_POOL: "queue.LifoQueue" = queue.LifoQueue(maxsize=8)
_IDLE_CHECK_SECONDS = 60


def _pg_get():
    import psycopg
    while True:
        try:
            conn, last_used = _POOL.get_nowait()
        except queue.Empty:
            return psycopg.connect(database_url(), connect_timeout=15)
        if conn.closed or conn.broken:
            continue
        if time.monotonic() - last_used > _IDLE_CHECK_SECONDS:
            # The server may have dropped an idle connection; check before use.
            try:
                conn.execute("SELECT 1")
                conn.rollback()
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                continue
        return conn


def _pg_put(conn) -> None:
    if conn.closed or conn.broken:
        return
    try:
        _POOL.put_nowait((conn, time.monotonic()))
    except queue.Full:
        conn.close()


@contextmanager
def connect():
    """A connection with the schema in place, committed on a clean exit."""
    global _initialised
    if backend() == "postgres":
        conn = _pg_get()
        try:
            if not _initialised:
                with conn.cursor() as cur:
                    cur.execute(POSTGRES_SCHEMA)
                _migrate(conn)
                conn.commit()
                _initialised = True
            yield conn
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            _pg_put(conn)
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=30)
        try:
            conn.executescript(SQLITE_SCHEMA)
            _migrate(conn)
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


# ---------------------------------------------------------------------------
# Postgres: writes run in one background thread, in the order they were made,
# with retries. The page moves on at once instead of waiting for the database.
# Reads call flush() first, so they always see every write made before them.
# SQLite (local runs and tests) keeps writing directly.
# ---------------------------------------------------------------------------

_WRITES: "queue.Queue" = queue.Queue()
_WORKER: threading.Thread | None = None
_WORKER_LOCK = threading.Lock()
_FAILED: list[str] = []


def _worker_loop() -> None:
    while True:
        fn, args, kwargs = _WRITES.get()
        try:
            for attempt in range(5):
                try:
                    fn(*args, **kwargs)
                    break
                except Exception as exc:          # network blip, cold database
                    if attempt == 4:
                        _FAILED.append(f"{fn.__name__}: {exc!r}"[:300])
                    time.sleep(0.4 * 2 ** attempt)
        finally:
            _WRITES.task_done()


def _ensure_worker() -> None:
    global _WORKER
    with _WORKER_LOCK:
        if _WORKER is None or not _WORKER.is_alive():
            _WORKER = threading.Thread(target=_worker_loop, name="storage-writer",
                                       daemon=True)
            _WORKER.start()


def _deferred(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if backend() != "postgres":
            return fn(*args, **kwargs)
        _ensure_worker()
        _WRITES.put((fn, copy.deepcopy(args), copy.deepcopy(kwargs)))
        return None
    return wrapper


def flush(timeout: float = 20.0) -> bool:
    """Wait until every queued write is stored. True if the queue is empty."""
    if backend() != "postgres":
        return True
    end = time.monotonic() + timeout
    while _WRITES.unfinished_tasks and time.monotonic() < end:
        time.sleep(0.05)
    return not _WRITES.unfinished_tasks


def failed_writes() -> list[str]:
    """Writes that failed after all retries (shown on the data page)."""
    return list(_FAILED)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

@_deferred
def start_session(code: str, track: int, seed: int, app_version: str,
                  codebook_version: str) -> None:
    with connect() as conn:
        _execute(conn,
                 "INSERT INTO sessions "
                 "(code, started_at, track, seed, app_version, codebook_version) "
                 "VALUES (?,?,?,?,?,?) ON CONFLICT (code) DO NOTHING",
                 (code, _now(), track, seed, app_version, codebook_version))


@_deferred
def update_session(code: str, **fields) -> None:
    if not fields:
        return
    assignments = ", ".join(f"{k} = ?" for k in fields)
    with connect() as conn:
        _execute(conn, f"UPDATE sessions SET {assignments} WHERE code = ?",
                 (*fields.values(), code))


@_deferred
def complete_session(code: str) -> None:
    """Mark the session complete and store its total duration in seconds."""
    now = datetime.now(timezone.utc)
    with connect() as conn:
        rows = _fetch(conn, "SELECT started_at FROM sessions WHERE code = ?", (code,))
    duration = None
    if rows and rows[0]["started_at"]:
        started = datetime.fromisoformat(rows[0]["started_at"])
        duration = round((now - started).total_seconds(), 1)
    update_session(code, completed_at=now.isoformat(timespec="seconds"),
                   duration_seconds=duration)


@_deferred
def save_response(code: str, screen: dict, screen_index: int, *,
                  option_key: str | None = None, option_index: int | None = None,
                  numeric_value: float | None = None, text_value: str | None = None,
                  response_seconds: float | None = None,
                  state: dict | None = None,
                  entered_at: str | None = None) -> None:
    with connect() as conn:
        _execute(
            conn,
            "INSERT INTO responses "
            "(code, screen_id, node, domain, block_position, node_position, "
            " screen_index, option_key, option_index, numeric_value, text_value, "
            " response_seconds, state_json, entered_at, answered_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT (code, screen_id) DO UPDATE SET "
            " option_key = EXCLUDED.option_key, option_index = EXCLUDED.option_index, "
            " numeric_value = EXCLUDED.numeric_value, text_value = EXCLUDED.text_value, "
            " response_seconds = EXCLUDED.response_seconds, "
            " state_json = EXCLUDED.state_json, entered_at = EXCLUDED.entered_at,"
            " answered_at = EXCLUDED.answered_at",
            (code, screen["id"], screen.get("node"), screen.get("domain"),
             screen.get("block_position"), screen.get("node_position"),
             screen_index, option_key, option_index, numeric_value, text_value,
             response_seconds, json.dumps(state) if state else None, entered_at,
             _now()))


@_deferred
def save_followup(code: str, email: str) -> None:
    with connect() as conn:
        _execute(conn,
                 "INSERT INTO followup (code, email, created_at) VALUES (?,?,?) "
                 "ON CONFLICT (code) DO UPDATE SET email = EXCLUDED.email",
                 (code, email.strip(), _now()))


# ---------------------------------------------------------------------------
# Resume (0.14.0): where a running session stands, under a random token.
# The token is the only thing in the URL; the session code and the email never
# are. The email is not part of the saved data either.
# ---------------------------------------------------------------------------

@_deferred
def save_progress(code: str, token: str, data: dict) -> None:
    with connect() as conn:
        _execute(conn,
                 "INSERT INTO progress (code, token, data, updated_at) VALUES (?,?,?,?) "
                 "ON CONFLICT (code) DO UPDATE SET token = EXCLUDED.token, "
                 " data = EXCLUDED.data, updated_at = EXCLUDED.updated_at",
                 (code, token, json.dumps(data), _now()))


def load_progress(token: str) -> dict | None:
    """The saved progress for a token, with `updated_at`, `completed` and
    `withdrawn` of its session; None if the token is unknown."""
    if not token:
        return None
    flush()
    with connect() as conn:
        rows = _fetch(conn,
                      "SELECT p.code, p.data, p.updated_at, s.completed_at, s.withdrawn "
                      "FROM progress p LEFT JOIN sessions s ON s.code = p.code "
                      "WHERE p.token = ?", (token,))
    if not rows:
        return None
    r = rows[0]
    try:
        data = json.loads(r["data"])
    except (TypeError, ValueError):
        return None
    return {"code": r["code"], "data": data, "updated_at": r["updated_at"],
            "completed": bool(r["completed_at"]) or bool(data.get("completed")),
            "withdrawn": bool(r["withdrawn"])}


def open_progress_for_email(email: str, exclude: str | None = None):
    """(code, token) of the latest session with this email that is neither
    completed nor withdrawn and has saved progress, otherwise None."""
    flush()
    with connect() as conn:
        rows = _fetch(conn,
                      "SELECT p.code, p.token FROM followup f "
                      "JOIN sessions s ON s.code = f.code "
                      "JOIN progress p ON p.code = f.code "
                      "WHERE f.email = ? AND s.completed_at IS NULL "
                      "AND (s.withdrawn IS NULL OR s.withdrawn = 0) "
                      "ORDER BY p.updated_at DESC",
                      (email.strip().lower(),))
    for r in rows:
        if r["code"] != exclude:
            return r["code"], r["token"]
    return None


def code_for_email(email: str) -> str | None:
    """Session id stored with an email address, for a withdrawal by mail."""
    flush()
    with connect() as conn:
        rows = _fetch(conn, "SELECT code FROM followup WHERE email = ?",
                      (email.strip().lower(),))
    return rows[0]["code"] if rows else None


def codes_for_email(email: str) -> list[str]:
    """Every session id stored with an email address (a reload can start more
    than one session), for a withdrawal by mail."""
    flush()
    with connect() as conn:
        rows = _fetch(conn, "SELECT code FROM followup WHERE email = ?",
                      (email.strip().lower(),))
    return [r["code"] for r in rows]


def completed_with_email(email: str) -> bool:
    """True if a completed session already exists for this email address."""
    flush()
    with connect() as conn:
        rows = _fetch(conn, "SELECT s.code FROM followup f JOIN sessions s ON s.code = f.code "
                            "WHERE f.email = ? AND s.completed_at IS NOT NULL "
                            "AND (s.withdrawn IS NULL OR s.withdrawn = 0)",
                      (email.strip().lower(),))
    return bool(rows)


def withdraw(code: str) -> None:
    """Mark the data as withdrawn and drop the follow-up contact."""
    flush()
    with connect() as conn:
        _execute(conn, "UPDATE sessions SET withdrawn = 1 WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM followup WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM progress WHERE code = ?", (code,))


def delete(code: str) -> int:
    """Remove a participant's data entirely, for a withdrawal by mail.
    Returns the number of session rows removed."""
    flush()
    with connect() as conn:
        before = _fetch(conn, "SELECT code FROM sessions WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM responses WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM followup WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM progress WHERE code = ?", (code,))
        _execute(conn, "DELETE FROM sessions WHERE code = ?", (code,))
        return len(before)


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def fetch_responses(code: str) -> list[dict]:
    flush()
    with connect() as conn:
        return _fetch(conn,
                      "SELECT * FROM responses WHERE code = ? ORDER BY screen_index",
                      (code,))


def fetch_all(table: str) -> list[dict]:
    flush()
    if table not in TABLES:
        raise ValueError(f"unknown table {table!r}")
    with connect() as conn:
        return _fetch(conn, f"SELECT * FROM {table}")


def track_load(tracks, window_minutes: int = 45) -> dict:
    """Per track: completed sessions plus sessions started in the last
    `window_minutes` that are still running. Counting the running ones keeps
    participants who start at the same time from all landing in one track.
    Withdrawn sessions and non-founders are left out."""
    with connect() as conn:
        rows = _fetch(conn, "SELECT track, started_at, completed_at, withdrawn, is_founder "
                            "FROM sessions")
    cutoff = datetime.now(timezone.utc).timestamp() - window_minutes * 60
    load = {t: 0 for t in tracks}
    for r in rows:
        if r["track"] not in load or r.get("withdrawn") or r.get("is_founder") == 0:
            continue
        if r["completed_at"]:
            load[r["track"]] += 1
            continue
        try:
            started = datetime.fromisoformat(str(r["started_at"])).timestamp()
        except (TypeError, ValueError):
            continue
        if started >= cutoff:
            load[r["track"]] += 1
    return load


def counts() -> dict:
    flush()
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
