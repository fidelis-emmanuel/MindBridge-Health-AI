#!/usr/bin/env python3
"""
SQLite tracker for job applications.
Auto-creates agents/job_apply/jobs.db on first import.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"

VALID_STATUSES = {"draft", "applied", "interview", "offer", "rejected"}

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS applications (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    company       TEXT NOT NULL,
    title         TEXT NOT NULL,
    fit_score     INTEGER,
    status        TEXT DEFAULT 'draft',
    job_text      TEXT,
    cover_letter  TEXT,
    notes         TEXT,
    applied_at    TEXT,
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute(CREATE_SQL)
    con.commit()
    return con

def add_job(company: str, title: str, fit_score: int,
            job_text: str = "", cover_letter: str = "") -> int:
    """Insert a new application. Returns the new row id."""
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO applications
               (company, title, fit_score, job_text, cover_letter)
               VALUES (?, ?, ?, ?, ?)""",
            (company, title, fit_score, job_text, cover_letter),
        )
        return cur.lastrowid

def update_status(app_id: int, status: str, notes: str = "") -> bool:
    """Update status and optional notes. Returns False if id not found."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Choose: {VALID_STATUSES}")
    applied_at = datetime.now().isoformat() if status == "applied" else None
    with _conn() as con:
        cur = con.execute(
            """UPDATE applications
               SET status=?, notes=COALESCE(?, notes), applied_at=COALESCE(?, applied_at)
               WHERE id=?""",
            (status, notes if notes else None, applied_at, app_id),
        )
        return cur.rowcount > 0

def list_jobs(status: str | None = None) -> list[sqlite3.Row]:
    """Return all applications, optionally filtered by status."""
    with _conn() as con:
        if status:
            return con.execute(
                "SELECT * FROM applications WHERE status=? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        return con.execute(
            "SELECT * FROM applications ORDER BY created_at DESC"
        ).fetchall()

def get_stats() -> dict:
    """Return counts by status and average fit score."""
    with _conn() as con:
        rows = con.execute(
            "SELECT status, COUNT(*) as n FROM applications GROUP BY status"
        ).fetchall()
        avg = con.execute(
            "SELECT AVG(fit_score) FROM applications WHERE fit_score IS NOT NULL"
        ).fetchone()[0]
    counts = {r["status"]: r["n"] for r in rows}
    counts["_total"] = sum(counts.values())
    counts["_avg_fit"] = round(avg or 0, 1)
    return counts
