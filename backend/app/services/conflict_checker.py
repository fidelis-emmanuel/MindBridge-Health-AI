"""
Appointment conflict detection using PostgreSQL tstzrange overlap (&&).

Raises HTTPException(409) if the requested clinician already has a
non-cancelled, non-no_show appointment whose time window overlaps with
the proposed [scheduled_at, scheduled_at + duration_minutes).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import asyncpg
from fastapi import HTTPException

_CONFLICT_SQL = """
    SELECT id
    FROM   appointments
    WHERE  clinician_id = $1
      AND  status NOT IN ('cancelled', 'no_show')
      AND  tstzrange(scheduled_at, ends_at, '[)')
           &&
           tstzrange(
               $2::timestamptz,
               $2::timestamptz + ($3 * INTERVAL '1 minute'),
               '[)'
           )
      AND  ($4::int IS NULL OR id != $4)
"""


async def check_conflict(
    conn: asyncpg.Connection,
    clinician_id: uuid.UUID,
    scheduled_at: datetime,
    duration_minutes: int,
    exclude_id: Optional[int] = None,
) -> None:
    """
    Query for any overlapping active appointment for this clinician.
    Raises HTTPException(409) on conflict; returns None if the slot is free.

    Pass exclude_id when rescheduling an existing appointment so it
    doesn't conflict with itself.
    """
    row = await conn.fetchrow(
        _CONFLICT_SQL,
        clinician_id,
        scheduled_at,
        duration_minutes,
        exclude_id,
    )
    if row:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Clinician already has an appointment at this time "
                f"(conflicts with appointment id={row['id']})"
            ),
        )
