"""
APScheduler-based reminder agent.

Jobs:
  reminder_24h  — runs every hour, emails clinicians for appointments
                  starting in the next 24 hours.
  reminder_1h   — runs every hour, emails clinicians for appointments
                  starting in the next 1 hour.
  daily_noshow  — runs daily at 02:00 UTC, flags patients with 3+
                  no-shows by setting their risk_level to HIGH.

Email is sent via Resend. If RESEND_API_KEY is not set the job runs in
dry-run mode (logs only) and does NOT crash the server.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

import asyncpg

logger = logging.getLogger(__name__)

# ── Resend setup (optional) ───────────────────────────────────────────────────

_RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
_resend_available = False

if _RESEND_API_KEY:
    try:
        import resend as _resend_lib
        _resend_lib.api_key = _RESEND_API_KEY
        _resend_available = True
        logger.info("Resend email client initialised")
    except ImportError:
        logger.warning("resend package not installed — email reminders disabled")
else:
    logger.warning(
        "RESEND_API_KEY not set — email reminders will run in dry-run mode"
    )

# ── Email sender ──────────────────────────────────────────────────────────────

_FROM_ADDRESS = "reminders@mindbridge.health"


async def _send_reminder_email(row: asyncpg.Record, hours_ahead: int) -> None:
    appt_time = row["scheduled_at"].strftime("%B %d, %Y at %I:%M %p UTC")
    subject = (
        f"[MindBridge] {'24-hour' if hours_ahead == 24 else '1-hour'} "
        f"appointment reminder"
    )
    html = (
        f"<p>This is a reminder that you have an appointment scheduled "
        f"with <strong>{row['patient_name']}</strong>.</p>"
        f"<p><strong>When:</strong> {appt_time}</p>"
        f"<p><strong>Duration:</strong> {row['duration_minutes']} minutes</p>"
        f"<p>Please log in to MindBridge to review the session details.</p>"
    )

    if not _resend_available:
        logger.info(
            "[DRY RUN] Would send %dh reminder for appointment %d to %s",
            hours_ahead,
            row["id"],
            row["clinician_email"],
        )
        return

    try:
        import resend as _resend_lib  # already imported above; re-import is fine
        _resend_lib.Emails.send(
            {
                "from": _FROM_ADDRESS,
                "to":   row["clinician_email"],
                "subject": subject,
                "html": html,
            }
        )
        logger.info(
            "Sent %dh reminder for appointment %d to %s",
            hours_ahead,
            row["id"],
            row["clinician_email"],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to send reminder for appointment %d: %s", row["id"], exc
        )


# ── Scheduled jobs ────────────────────────────────────────────────────────────

async def send_reminders(pool: asyncpg.Pool, hours_ahead: int) -> None:
    """
    Find appointments starting in [now + hours_ahead - 30min,
    now + hours_ahead + 30min] that have not yet had a reminder sent,
    send an email, and mark the flag.
    """
    now = datetime.now(timezone.utc)
    window_start = now + timedelta(hours=hours_ahead) - timedelta(minutes=30)
    window_end   = now + timedelta(hours=hours_ahead) + timedelta(minutes=30)

    sent_flag = "reminder_24h_sent" if hours_ahead == 24 else "reminder_1h_sent"

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT
                    a.id,
                    a.scheduled_at,
                    a.duration_minutes,
                    p.patient_name,
                    c.name   AS clinician_name,
                    c.email  AS clinician_email
                FROM  appointments a
                JOIN  patients   p ON p.id = a.patient_id
                JOIN  clinicians c ON c.id = a.clinician_id
                WHERE a.status IN ('scheduled', 'confirmed')
                  AND a.scheduled_at BETWEEN $1 AND $2
                  AND a.{sent_flag} = FALSE
                """,
                window_start,
                window_end,
            )

            for row in rows:
                await _send_reminder_email(row, hours_ahead)
                await conn.execute(
                    f"UPDATE appointments SET {sent_flag} = TRUE WHERE id = $1",
                    row["id"],
                )

        if rows:
            logger.info(
                "Reminder job (%dh): processed %d appointments", hours_ahead, len(rows)
            )
    except Exception as exc:  # noqa: BLE001
        logger.error("send_reminders(%dh) failed: %s", hours_ahead, exc)


async def flag_noshow_patients(pool: asyncpg.Pool) -> None:
    """
    Daily job: escalate risk_level to HIGH for any patient who has
    accumulated 3 or more no-shows.
    """
    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE patients
                SET    risk_level = 'HIGH'
                WHERE  id IN (
                    SELECT patient_id
                    FROM   appointments
                    WHERE  status = 'no_show'
                    GROUP  BY patient_id
                    HAVING COUNT(*) >= 3
                )
                AND risk_level NOT IN ('CRITICAL', 'HIGH')
                """
            )
        logger.info("daily_noshow: %s", result)
    except Exception as exc:  # noqa: BLE001
        logger.error("flag_noshow_patients failed: %s", exc)


# ── Scheduler lifecycle ───────────────────────────────────────────────────────

def start_reminder_scheduler(pool: asyncpg.Pool) -> None:
    """
    Start the APScheduler AsyncIOScheduler with all reminder jobs.
    Call this from the FastAPI lifespan after the DB pool is ready.
    """
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler(timezone="UTC")

    scheduler.add_job(
        send_reminders,
        trigger="interval",
        hours=1,
        args=[pool, 24],
        id="reminder_24h",
        replace_existing=True,
    )
    scheduler.add_job(
        send_reminders,
        trigger="interval",
        hours=1,
        args=[pool, 1],
        id="reminder_1h",
        replace_existing=True,
    )
    scheduler.add_job(
        flag_noshow_patients,
        trigger="cron",
        hour=2,
        minute=0,
        args=[pool],
        id="daily_noshow_flag",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Reminder scheduler started (3 jobs registered)")
