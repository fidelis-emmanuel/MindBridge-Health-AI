"""
Appointment Scheduling test suite.

Covers:
  - test_create_appointment_success
  - test_conflict_returns_409
  - test_noshow_rate_calculation
  - test_fhir_appointment_serialization

Uses synchronous TestClient + MagicMock/AsyncMock (same pattern as
test_scribe_router.py) — no live database required.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.appointments import router as appt_router
from app.fhir.appointment import router as fhir_router

# ── Test application ──────────────────────────────────────────────────────────

app = FastAPI()
app.include_router(appt_router, prefix="/appointments")
app.include_router(fhir_router, prefix="/fhir")


# ── Fixtures & helpers ────────────────────────────────────────────────────────

_CLINICIAN_ID = str(uuid.uuid4())
_PATIENT_ID   = 1
_APPT_ID      = 99

# A future UTC datetime on a Tuesday (weekday=1) within business hours
_FUTURE_APPT  = datetime(2027, 6, 15, 14, 0, 0, tzinfo=timezone.utc)  # Mon 14:00


def _make_appt_record(**overrides: Any) -> dict:
    ends = _FUTURE_APPT + timedelta(minutes=50)
    base = {
        "id":                  _APPT_ID,
        "patient_id":          _PATIENT_ID,
        "clinician_id":        uuid.UUID(_CLINICIAN_ID),
        "appointment_type":    "individual",
        "status":              "scheduled",
        "scheduled_at":        _FUTURE_APPT,
        "ends_at":             ends,
        "duration_minutes":    50,
        "notes":               None,
        "location":            None,
        "reminder_24h_sent":   False,
        "reminder_1h_sent":    False,
        "cancelled_at":        None,
        "cancellation_reason": None,
        "created_at":          _FUTURE_APPT,
        "updated_at":          _FUTURE_APPT,
    }
    base.update(overrides)
    return base


def _make_pool(
    fetchrow_return=None,
    fetchval_return=None,
    fetch_return=None,
    execute_return="INSERT 0 1",
):
    """Build a minimal mock asyncpg pool for router tests."""
    mock_conn = MagicMock()
    mock_conn.fetchrow  = AsyncMock(return_value=fetchrow_return)
    mock_conn.fetchval  = AsyncMock(return_value=fetchval_return)
    mock_conn.fetch     = AsyncMock(return_value=fetch_return or [])
    mock_conn.execute   = AsyncMock(return_value=execute_return)

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_ctx.__aexit__  = AsyncMock(return_value=False)

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=mock_ctx)

    return mock_pool, mock_conn


# ══════════════════════════════════════════════════════════════════════════════
# Test 1 — Create appointment success
# ══════════════════════════════════════════════════════════════════════════════

def test_create_appointment_success():
    """POST /appointments/ returns 201 with the created appointment."""
    record = _make_appt_record()
    mock_pool, mock_conn = _make_pool(fetchrow_return=record)

    # conflict_checker.check_conflict must not raise
    with patch(
        "app.routers.appointments.check_conflict",
        new=AsyncMock(return_value=None),
    ):
        app.state.pool = mock_pool
        client = TestClient(app)
        resp = client.post(
            "/appointments/",
            json={
                "patient_id":       _PATIENT_ID,
                "clinician_id":     _CLINICIAN_ID,
                "appointment_type": "individual",
                "scheduled_at":     _FUTURE_APPT.isoformat(),
                "duration_minutes": 50,
            },
        )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] == _APPT_ID
    assert data["status"] == "scheduled"
    assert data["appointment_type"] == "individual"
    assert data["duration_minutes"] == 50


# ══════════════════════════════════════════════════════════════════════════════
# Test 2 — Conflict detection returns 409
# ══════════════════════════════════════════════════════════════════════════════

def test_conflict_returns_409():
    """POST /appointments/ returns 409 when the clinician has a time conflict."""
    from fastapi import HTTPException

    mock_pool, _ = _make_pool()

    with patch(
        "app.routers.appointments.check_conflict",
        new=AsyncMock(
            side_effect=HTTPException(
                status_code=409,
                detail="Clinician already has an appointment at this time "
                       "(conflicts with appointment id=7)",
            )
        ),
    ):
        app.state.pool = mock_pool
        client = TestClient(app)
        resp = client.post(
            "/appointments/",
            json={
                "patient_id":       _PATIENT_ID,
                "clinician_id":     _CLINICIAN_ID,
                "appointment_type": "individual",
                "scheduled_at":     _FUTURE_APPT.isoformat(),
                "duration_minutes": 50,
            },
        )

    assert resp.status_code == 409
    assert "conflicts with appointment" in resp.json()["detail"]


# ══════════════════════════════════════════════════════════════════════════════
# Test 3 — No-show rate calculation
# ══════════════════════════════════════════════════════════════════════════════

def test_noshow_rate_calculation():
    """GET /appointments/analytics/noshow?patient_id= returns correct rate."""
    # 2 no-shows out of 5 total → 40.0 %
    analytics_row = {
        "no_shows":     2,
        "total":        5,
        "no_show_rate": 40.0,
    }
    mock_pool, _ = _make_pool(fetchrow_return=analytics_row)
    app.state.pool = mock_pool

    client = TestClient(app)
    resp = client.get(f"/appointments/analytics/noshow?patient_id={_PATIENT_ID}")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["patient_id"] == _PATIENT_ID
    assert data["no_shows"] == 2
    assert data["total_appointments"] == 5
    assert data["no_show_rate_pct"] == pytest.approx(40.0)


# ══════════════════════════════════════════════════════════════════════════════
# Test 4 — FHIR Appointment serialization
# ══════════════════════════════════════════════════════════════════════════════

def test_fhir_appointment_serialization():
    """GET /fhir/Appointment/{id} returns a valid FHIR R4 Appointment resource."""
    fhir_row = {
        "id":               _APPT_ID,
        "status":           "scheduled",
        "appointment_type": "telehealth",
        "scheduled_at":     _FUTURE_APPT,
        "ends_at":          _FUTURE_APPT + timedelta(minutes=50),
        "duration_minutes": 50,
        "notes":            "Initial telehealth intake",
        "patient_id":       _PATIENT_ID,
        "clinician_id":     uuid.UUID(_CLINICIAN_ID),
        "patient_name":     "Alice Okonkwo",
        "clinician_name":   "Dr. Sarah Chen",
    }
    mock_pool, _ = _make_pool(fetchrow_return=fhir_row)
    app.state.pool = mock_pool

    client = TestClient(app)
    resp = client.get(f"/fhir/Appointment/{_APPT_ID}")

    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Required FHIR R4 fields
    assert data["resourceType"] == "Appointment"
    assert data["id"] == str(_APPT_ID)
    assert data["status"] == "booked"           # scheduled → booked
    assert data["minutesDuration"] == 50

    # start / end
    assert "start" in data
    assert "end" in data

    # Participants
    actors = [p["actor"]["reference"] for p in data["participant"]]
    assert f"Patient/{_PATIENT_ID}" in actors
    assert f"Practitioner/{_CLINICIAN_ID}" in actors

    # serviceType coding
    service_code = data["serviceType"][0]["coding"][0]["code"]
    assert service_code == "telehealth"
