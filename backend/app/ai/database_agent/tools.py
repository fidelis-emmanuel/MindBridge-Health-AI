"""
Tool implementations for the MindBridge Database Agent.
Each function maps to one tool Claude can call during the agentic loop.
All functions accept an asyncpg Connection as their first argument.
"""
import re
from typing import Any

import asyncpg

from app.ai.database_agent.audit import log_audit_event

# Tables the agent is permitted to delete from.
_CLEANUP_ALLOWLIST = frozenset({
    "appointments",
    "session_logs",
    "temp_uploads",
    "notification_queue",
})

# Keywords that must not appear in a query_database SQL string.
_BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)


# ── check_blocking ─────────────────────────────────────────────────────────────

async def check_blocking(
    conn: asyncpg.Connection,
    min_duration_ms: int = 1000,
) -> dict[str, Any]:
    """
    Query pg_stat_activity for sessions that are slow, blocked, or blocking others.

    Returns active sessions running longer than min_duration_ms, annotated with
    which pids are blocking each session (empty array means not blocked).
    """
    rows = await conn.fetch(
        """
        SELECT
            pid,
            state,
            wait_event_type,
            wait_event,
            query_start,
            EXTRACT(EPOCH FROM (now() - query_start)) * 1000 AS duration_ms,
            left(query, 300)                                  AS query_preview,
            pg_blocking_pids(pid)                             AS blocked_by
        FROM pg_stat_activity
        WHERE state != 'idle'
          AND query_start IS NOT NULL
          AND now() - query_start > (interval '1 millisecond' * $1)
        ORDER BY query_start ASC
        """,
        min_duration_ms,
    )

    sessions = []
    for row in rows:
        sessions.append({
            "pid":             row["pid"],
            "state":           row["state"],
            "wait_event_type": row["wait_event_type"],
            "wait_event":      row["wait_event"],
            "duration_ms":     round(row["duration_ms"] or 0, 1),
            "query_preview":   row["query_preview"],
            "blocked_by":      list(row["blocked_by"] or []),
        })

    blocking_pids = {pid for s in sessions for pid in s["blocked_by"]}

    return {
        "sessions_found": len(sessions),
        "min_duration_ms": min_duration_ms,
        "sessions": sessions,
        "blocking_pids": sorted(blocking_pids),
        "summary": (
            f"{len(sessions)} active session(s) exceeding {min_duration_ms}ms. "
            f"{len(blocking_pids)} session(s) are blocking others."
            if sessions else
            f"No sessions exceeding {min_duration_ms}ms threshold."
        ),
    }


# ── query_database ─────────────────────────────────────────────────────────────

async def query_database(
    conn: asyncpg.Connection,
    sql: str,
    params: list[Any] | None = None,
) -> dict[str, Any]:
    """
    Execute a safe SELECT query against the MindBridge database.

    Blocks any SQL containing INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER,
    CREATE, GRANT, REVOKE, or EXEC to prevent unintended data modification.
    """
    stripped = sql.strip()

    # Block dangerous keywords anywhere in the statement
    match = _BLOCKED_KEYWORDS.search(stripped)
    if match:
        return {
            "error": (
                f"Blocked keyword '{match.group().upper()}' detected. "
                "query_database only permits SELECT statements."
            )
        }

    if not stripped.upper().startswith("SELECT"):
        return {"error": "Only SELECT statements are permitted by query_database."}

    try:
        rows = await conn.fetch(stripped, *(params or []))
    except asyncpg.PostgresError as e:
        return {"error": f"Query failed: {e}"}

    results = [dict(row) for row in rows]

    return {
        "row_count": len(results),
        "rows": results,
        "truncated": False,
    }


# ── create_view ────────────────────────────────────────────────────────────────

async def create_view(
    conn: asyncpg.Connection,
    name: str,
    sql: str,
) -> dict[str, Any]:
    """
    Create or replace a reusable PostgreSQL VIEW.

    The name must be a valid identifier (letters, digits, underscores).
    The sql argument is the SELECT body — do not include CREATE VIEW syntax.
    """
    # Validate view name is a safe identifier
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        return {
            "error": (
                f"Invalid view name '{name}'. "
                "Use lowercase letters, digits, and underscores only, starting with a letter."
            )
        }

    # Block dangerous keywords in the view body
    match = _BLOCKED_KEYWORDS.search(sql)
    if match:
        return {
            "error": (
                f"Blocked keyword '{match.group().upper()}' in view SQL. "
                "View body must be a SELECT statement."
            )
        }

    try:
        await conn.execute(f"CREATE OR REPLACE VIEW {name} AS {sql}")
    except asyncpg.PostgresError as e:
        return {"error": f"Failed to create view '{name}': {e}"}

    return {
        "success": True,
        "view_name": name,
        "message": f"View '{name}' created (or replaced) successfully.",
    }


# ── run_cleanup ────────────────────────────────────────────────────────────────

async def run_cleanup(
    conn: asyncpg.Connection,
    table: str,
    condition: str,
    dry_run: bool = True,
    reason: str | None = None,
    performed_by: str | None = None,
) -> dict[str, Any]:
    """
    Delete records from an allowlisted table with audit logging.

    Always dry_run=True by default. The agent must call this twice:
      1. dry_run=True  → preview count, show user, get confirmation
      2. dry_run=False → actual deletion, after explicit user approval

    Only these tables are permitted: appointments, session_logs,
    temp_uploads, notification_queue.
    """
    if table not in _CLEANUP_ALLOWLIST:
        return {
            "error": (
                f"Table '{table}' is not in the cleanup allowlist. "
                f"Permitted tables: {sorted(_CLEANUP_ALLOWLIST)}."
            )
        }

    if dry_run:
        # Preview only — count matching rows, no deletion
        try:
            count = await conn.fetchval(
                f"SELECT COUNT(*) FROM {table} WHERE {condition}"
            )
        except asyncpg.PostgresError as e:
            return {"error": f"Dry run query failed: {e}"}

        await log_audit_event(
            conn,
            operation="run_cleanup",
            table_name=table,
            affected_rows=0,
            where_clause=condition,
            reason=reason,
            dry_run=True,
            performed_by=performed_by,
            metadata={"preview_count": count},
        )

        return {
            "dry_run": True,
            "table": table,
            "condition": condition,
            "would_delete": count,
            "message": (
                f"DRY RUN: {count} row(s) in '{table}' match the condition "
                f"'{condition}' and would be deleted. "
                "Confirm with dry_run=false to proceed."
            ),
        }

    # Actual deletion
    try:
        result = await conn.execute(
            f"DELETE FROM {table} WHERE {condition}"
        )
        # asyncpg returns e.g. "DELETE 42" — extract the count
        deleted = int(result.split()[-1]) if result else 0
    except asyncpg.PostgresError as e:
        return {"error": f"Cleanup failed: {e}"}

    await log_audit_event(
        conn,
        operation="run_cleanup",
        table_name=table,
        affected_rows=deleted,
        where_clause=condition,
        reason=reason,
        dry_run=False,
        performed_by=performed_by,
        metadata={"deleted_count": deleted},
    )

    return {
        "dry_run": False,
        "table": table,
        "condition": condition,
        "deleted": deleted,
        "message": f"Deleted {deleted} row(s) from '{table}' where {condition}. Audit log updated.",
    }
