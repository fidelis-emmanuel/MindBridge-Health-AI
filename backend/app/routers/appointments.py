"""
Appointment Scheduling router — mounts at /appointments in main.py.

Route order matters: literal paths (/availability, /analytics/noshow,
/patient/{id}) are defined BEFORE the catch-all /{id} so FastAPI
matches them first.
"""
from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, time as dt_time, timedelta, timezone
from typing import Optional

import asyncpg
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.models.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
    AppointmentUpdate,
    AppointmentStatus,
)
from app.services.conflict_checker import check_conflict

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Scheduling"])

# ── Dependency ────────────────────────────────────────────────────────────────

def _get_pool(request: Request) -> asyncpg.Pool:
    pool = request.app.state.pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return pool


# ── DB → response helper ──────────────────────────────────────────────────────

def _row_to_response(row: asyncpg.Record) -> AppointmentResponse:
    return AppointmentResponse(
        id=row["id"],
        patient_id=row["patient_id"],
        clinician_id=row["clinician_id"],
        appointment_type=row["appointment_type"],
        status=row["status"],
        scheduled_at=row["scheduled_at"],
        ends_at=row["ends_at"],
        duration_minutes=row["duration_minutes"],
        notes=row["notes"],
        location=row["location"],
        reminder_24h_sent=row["reminder_24h_sent"],
        reminder_1h_sent=row["reminder_1h_sent"],
        cancelled_at=row["cancelled_at"],
        cancellation_reason=row["cancellation_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ── Background tasks ──────────────────────────────────────────────────────────

async def _create_scribe_draft(appointment_id: int, pool: asyncpg.Pool) -> None:
    """Insert a blank SOAP note stub so the clinician has a draft to fill in."""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT a.patient_id, c.name AS clinician_name, a.scheduled_at
                FROM   appointments a
                JOIN   clinicians   c ON c.id = a.clinician_id
                WHERE  a.id = $1
                """,
                appointment_id,
            )
            if not row:
                return
            await conn.execute(
                """
                INSERT INTO soap_notes
                    (patient_id, provider_name, raw_input)
                VALUES ($1, $2, $3)
                """,
                row["patient_id"],
                row["clinician_name"],
                f"[AUTO-DRAFT] Appointment {appointment_id} completed "
                f"on {row['scheduled_at'].date()}",
            )
            logger.info("Scribe draft created for appointment %d", appointment_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("create_scribe_draft failed for appt %d: %s", appointment_id, exc)


async def _update_patient_risk(patient_id: int, pool: asyncpg.Pool) -> None:
    """Escalate risk to HIGH if the patient has 3+ no-shows."""
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM appointments "
                "WHERE patient_id = $1 AND status = 'no_show'",
                patient_id,
            )
            if count >= 3:
                await conn.execute(
                    "UPDATE patients SET risk_level = 'HIGH' "
                    "WHERE id = $1 AND risk_level NOT IN ('CRITICAL', 'HIGH')",
                    patient_id,
                )
                logger.info(
                    "Patient %d risk escalated to HIGH (%d no-shows)",
                    patient_id,
                    count,
                )
    except Exception as exc:  # noqa: BLE001
        logger.error("update_patient_risk failed for patient %d: %s", patient_id, exc)


# ── Availability helper ───────────────────────────────────────────────────────

_SLOT_STEP     = timedelta(minutes=30)
_DEFAULT_DUR   = 50
_BIZ_START     = dt_time(7, 0)
_BIZ_END       = dt_time(20, 0)


def _generate_slots(target: date, duration: int = _DEFAULT_DUR) -> list[datetime]:
    """
    Return all 30-minute-boundary start times on *target* for which a
    *duration*-minute appointment would fit inside business hours.
    All times are UTC.
    """
    slots: list[datetime] = []
    cursor = datetime.combine(target, _BIZ_START, tzinfo=timezone.utc)
    end_wall = datetime.combine(target, _BIZ_END, tzinfo=timezone.utc)
    slot_len = timedelta(minutes=duration)
    while cursor + slot_len <= end_wall:
        slots.append(cursor)
        cursor += _SLOT_STEP
    return slots


# ══════════════════════════════════════════════════════════════════════════════
# Routes — literal paths FIRST so they are not swallowed by /{appointment_id}
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/availability")
async def get_availability(
    clinician_id: uuid.UUID,
    date: date,
    duration: int = _DEFAULT_DUR,
    request: Request = ...,
):
    """
    Return available start-time slots for a clinician on a given date.
    Duration defaults to 50 min; slots are generated every 30 minutes
    across business hours (07:00–20:00 UTC, Mon–Fri).
    """
    if date.weekday() > 4:
        return {"clinician_id": str(clinician_id), "date": str(date), "slots": []}

    pool = _get_pool(request)
    candidates = _generate_slots(date, duration)

    async with pool.acquire() as conn:
        # Fetch all active appointments that day for this clinician
        rows = await conn.fetch(
            """
            SELECT scheduled_at, duration_minutes
            FROM   appointments
            WHERE  clinician_id = $1
              AND  status NOT IN ('cancelled', 'no_show')
              AND  scheduled_at::date = $2
            """,
            clinician_id,
            date,
        )

    booked: list[tuple[datetime, datetime]] = [
        (
            r["scheduled_at"],
            r["scheduled_at"] + timedelta(minutes=r["duration_minutes"]),
        )
        for r in rows
    ]

    slot_len = timedelta(minutes=duration)
    available = []
    for slot_start in candidates:
        slot_end = slot_start + slot_len
        conflict = any(
            slot_start < b_end and slot_end > b_start
            for b_start, b_end in booked
        )
        if not conflict:
            available.append(slot_start.isoformat())

    return {
        "clinician_id": str(clinician_id),
        "date": str(date),
        "duration_minutes": duration,
        "slots": available,
    }


@router.get("/analytics/noshow")
async def get_noshow_analytics(
    patient_id: Optional[int] = None,
    request: Request = ...,
):
    """
    No-show rate analytics.
    If patient_id is given, return that patient's rate.
    Otherwise return the top patients by no-show count.
    """
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        if patient_id is not None:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE status = 'no_show')          AS no_shows,
                    COUNT(*) FILTER (WHERE status != 'cancelled')        AS total,
                    ROUND(
                        COUNT(*) FILTER (WHERE status = 'no_show')::numeric
                        / NULLIF(
                            COUNT(*) FILTER (WHERE status != 'cancelled'), 0
                          ) * 100,
                        1
                    ) AS no_show_rate
                FROM appointments
                WHERE patient_id = $1
                """,
                patient_id,
            )
            return {
                "patient_id": patient_id,
                "no_shows": row["no_shows"],
                "total_appointments": row["total"],
                "no_show_rate_pct": float(row["no_show_rate"] or 0),
            }

        rows = await conn.fetch(
            """
            SELECT
                patient_id,
                COUNT(*) FILTER (WHERE status = 'no_show')   AS no_shows,
                COUNT(*) FILTER (WHERE status != 'cancelled') AS total
            FROM appointments
            GROUP BY patient_id
            HAVING COUNT(*) FILTER (WHERE status = 'no_show') > 0
            ORDER BY no_shows DESC
            """
        )
        return [
            {
                "patient_id": r["patient_id"],
                "no_shows": r["no_shows"],
                "total_appointments": r["total"],
            }
            for r in rows
        ]


@router.get("/patient/{patient_id}")
async def get_patient_appointments(patient_id: int, request: Request):
    """Patient appointment history with total no-show count."""
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT *
            FROM   appointments
            WHERE  patient_id = $1
            ORDER  BY scheduled_at DESC
            """,
            patient_id,
        )
        no_show_count = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments "
            "WHERE patient_id = $1 AND status = 'no_show'",
            patient_id,
        )

    return {
        "patient_id": patient_id,
        "no_show_count": no_show_count,
        "appointments": [_row_to_response(r).model_dump() for r in rows],
        "count": len(rows),
    }


# ── POST /appointments ────────────────────────────────────────────────────────

@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(body: AppointmentCreate, request: Request):
    """Create a new appointment. Returns 409 if the clinician has a conflict."""
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        await check_conflict(
            conn,
            body.clinician_id,
            body.scheduled_at,
            body.duration_minutes,
        )
        row = await conn.fetchrow(
            """
            INSERT INTO appointments
                (patient_id, clinician_id, appointment_type,
                 scheduled_at, duration_minutes, notes, location)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
            """,
            body.patient_id,
            body.clinician_id,
            body.appointment_type.value,
            body.scheduled_at,
            body.duration_minutes,
            body.notes,
            body.location,
        )
    return _row_to_response(row)


# ── GET /appointments/{id} ────────────────────────────────────────────────────

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int, request: Request):
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM appointments WHERE id = $1", appointment_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return _row_to_response(row)


# ── PATCH /appointments/{id}/status ──────────────────────────────────────────

@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    body: AppointmentStatusUpdate,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """
    Update appointment status.
    - completed  → enqueue scribe draft creation
    - no_show    → enqueue patient risk-score update
    - cancelled  → soft-delete (set status + cancelled_at)
    """
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT * FROM appointments WHERE id = $1", appointment_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if body.status == AppointmentStatus.cancelled:
            row = await conn.fetchrow(
                """
                UPDATE appointments
                SET    status = 'cancelled',
                       cancelled_at = NOW(),
                       cancellation_reason = $2
                WHERE  id = $1
                RETURNING *
                """,
                appointment_id,
                body.cancellation_reason,
            )
        else:
            row = await conn.fetchrow(
                """
                UPDATE appointments
                SET    status = $2
                WHERE  id = $1
                RETURNING *
                """,
                appointment_id,
                body.status.value,
            )

    if body.status == AppointmentStatus.completed:
        background_tasks.add_task(_create_scribe_draft, appointment_id, pool)

    if body.status == AppointmentStatus.no_show:
        background_tasks.add_task(
            _update_patient_risk, existing["patient_id"], pool
        )

    return _row_to_response(row)


# ── DELETE /appointments/{id} — soft delete ───────────────────────────────────

@router.delete("/{appointment_id}", status_code=204)
async def cancel_appointment(appointment_id: int, request: Request):
    """Soft-delete: set status to 'cancelled'."""
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE appointments
            SET    status = 'cancelled',
                   cancelled_at = NOW()
            WHERE  id = $1
              AND  status != 'cancelled'
            """,
            appointment_id,
        )
    if result == "UPDATE 0":
        raise HTTPException(
            status_code=404,
            detail="Appointment not found or already cancelled",
        )
