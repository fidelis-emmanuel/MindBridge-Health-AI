"""
Audit logging for the MindBridge Database Agent.
Every run_cleanup operation is recorded here — dry runs and actual deletions.
"""
import json
from typing import Any

import asyncpg


async def ensure_audit_table(conn: asyncpg.Connection) -> None:
    """
    Create the audit_log table if it does not already exist.
    Called once at the start of each agent session.
    """
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id              SERIAL PRIMARY KEY,
            operation       TEXT NOT NULL,
            table_name      TEXT,
            affected_rows   INTEGER DEFAULT 0,
            where_clause    TEXT,
            params          JSONB,
            reason          TEXT,
            dry_run         BOOLEAN DEFAULT TRUE,
            performed_by    TEXT,
            metadata        JSONB,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """)


async def log_audit_event(
    conn: asyncpg.Connection,
    *,
    operation: str,
    table_name: str | None = None,
    affected_rows: int = 0,
    where_clause: str | None = None,
    params: list[Any] | None = None,
    reason: str | None = None,
    dry_run: bool = True,
    performed_by: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Insert one row into audit_log recording a database agent operation.

    Args:
        conn:          Active asyncpg connection.
        operation:     Short label, e.g. 'run_cleanup', 'query_database'.
        table_name:    Target table, if applicable.
        affected_rows: Number of rows deleted (0 for dry runs).
        where_clause:  The WHERE condition used (for cleanup operations).
        params:        Query parameters, stored as JSONB.
        reason:        Human-readable justification for the operation.
        dry_run:       True if preview only; False if records were actually modified.
        performed_by:  Identifier of the requesting user or system.
        metadata:      Any additional context to store.
    """
    await conn.execute(
        """
        INSERT INTO audit_log (
            operation, table_name, affected_rows, where_clause,
            params, reason, dry_run, performed_by, metadata
        ) VALUES (
            $1, $2, $3, $4,
            $5::jsonb, $6, $7, $8, $9::jsonb
        )
        """,
        operation,
        table_name,
        affected_rows,
        where_clause,
        json.dumps(params) if params is not None else None,
        reason,
        dry_run,
        performed_by,
        json.dumps(metadata) if metadata is not None else None,
    )
