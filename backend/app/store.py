"""SQLite store with idempotent upsert + run history. Demonstrates the
'repeatable runs, data consistency, safe retries' discipline the JD asks for."""
import os
import sqlite3
import threading
import json
from app.config import DB_PATH
from app.models import Lead

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
_lock = threading.Lock()


def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _lock, _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identity_key TEXT UNIQUE,
            email TEXT, name TEXT, company TEXT, title TEXT,
            source TEXT, industry TEXT, company_size TEXT,
            score REAL, qualified INTEGER, sf_id TEXT,
            last_sync_status TEXT, raw TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started TEXT, finished TEXT, status TEXT,
            discovered INTEGER, qualified INTEGER, synced INTEGER, notes TEXT
        )""")


def upsert_lead(lead: Lead) -> Lead:
    """Idempotent: same identity_key updates in place (dedup), never duplicates."""
    lead.normalized()
    key = lead.identity_key()
    with _lock, _conn() as c:
        row = c.execute("SELECT id FROM leads WHERE identity_key=?", (key,)).fetchone()
        if row:
            lid = row["id"]
            c.execute(
                """UPDATE leads SET email=?, name=?, company=?, title=?, source=?,
                   industry=?, company_size=?, score=?, qualified=?, sf_id=?,
                   last_sync_status=?, raw=? WHERE id=?""",
                (lead.email, lead.name, lead.company, lead.title, lead.source,
                 lead.industry, lead.company_size, lead.score, int(lead.qualified),
                 lead.sf_id, lead.last_sync_status, str(lead.raw), lid))
            lead.id = lid
        else:
            cur = c.execute(
                """INSERT INTO leads (identity_key, email, name, company, title, source,
                   industry, company_size, score, qualified, sf_id, last_sync_status, raw)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (key, lead.email, lead.name, lead.company, lead.title, lead.source,
                 lead.industry, lead.company_size, lead.score, int(lead.qualified),
                 lead.sf_id, lead.last_sync_status, json.dumps(lead.raw)))
            lead.id = cur.lastrowid
    return lead


def list_leads(qualified_only: bool = False):
    with _lock, _conn() as c:
        q = "SELECT * FROM leads"
        if qualified_only:
            q += " WHERE qualified=1"
        rows = c.execute(q).fetchall()
    return [Lead(**_row_to_dict(r)) for r in rows]


def get_lead(lid: int):
    with _lock, _conn() as c:
        r = c.execute("SELECT * FROM leads WHERE id=?", (lid,)).fetchone()
    return Lead(**_row_to_dict(r)) if r else None


def log_run(started, finished, status, discovered, qualified, synced, notes=""):
    with _lock, _conn() as c:
        cur = c.execute(
            "INSERT INTO runs (started, finished, status, discovered, qualified, synced, notes) VALUES (?,?,?,?,?,?,?)",
            (started, finished, status, discovered, qualified, synced, notes))
        return cur.lastrowid


def reset():
    """Clear all data (handoff/dev convenience)."""
    with _lock, _conn() as c:
        c.execute("DELETE FROM leads")
        c.execute("DELETE FROM runs")


def list_runs():
    with _lock, _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 20").fetchall()]


def _row_to_dict(r):
    d = dict(r)
    d["qualified"] = bool(d["qualified"])
    d.pop("identity_key", None)
    try:
        d["raw"] = json.loads(d["raw"]) if d["raw"] else {}
    except (json.JSONDecodeError, TypeError):
        d["raw"] = {}
    return d
