"""
FHIR R4 Appointment resource serializer.

GET /fhir/Appointment/{id}
Maps the internal appointments row to a conformant FHIR R4 Appointment
resource (https://hl7.org/fhir/R4/appointment.html).
"""
from __future__ import annotations

from datetime import timedelta

import asyncpg
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["FHIR"])

# Internal status → FHIR AppointmentStatus binding
_FHIR_STATUS: dict[str, str] = {
    "scheduled": "booked",
    "confirmed": "booked",
    "completed": "fulfilled",
    "cancelled": "cancelled",
    "no_show":   "noshow",
}

# Internal appointment_type → FHIR serviceType code
_SERVICE_TYPE_DISPLAY: dict[str, str] = {
    "individual": "Individual Therapy",
    "group":      "Group Therapy",
    "telehealth": "Telehealth Consultation",
    "intake":     "Intake Assessment",
    "crisis":     "Crisis Intervention",
}


def _get_pool(request: Request) -> asyncpg.Pool:
    pool = request.app.state.pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return pool


@router.get("/Appointment/{appointment_id}")
async def get_fhir_appointment(appointment_id: int, request: Request):
    """
    Serialize a MindBridge appointment as a FHIR R4 Appointment resource.

    Mapping:
      scheduled_at                  → start
      scheduled_at + duration_min   → end
      duration_minutes              → minutesDuration
      status                        → FHIR AppointmentStatus enum
      appointment_type              → serviceType coding
    """
    pool = _get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                a.id,
                a.status,
                a.appointment_type,
                a.scheduled_at,
                a.duration_minutes,
                a.notes,
                a.patient_id,
                a.clinician_id,
                p.patient_name,
                c.name AS clinician_name
            FROM  appointments a
            JOIN  patients    p ON p.id = a.patient_id
            JOIN  clinicians  c ON c.id = a.clinician_id
            WHERE a.id = $1
            """,
            appointment_id,
        )

    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    end_time = row["scheduled_at"] + timedelta(minutes=row["duration_minutes"])
    appt_type = row["appointment_type"]

    return {
        "resourceType":  "Appointment",
        "id":            str(row["id"]),
        "status":        _FHIR_STATUS.get(row["status"], "proposed"),
        "start":         row["scheduled_at"].isoformat(),
        "end":           end_time.isoformat(),
        "minutesDuration": row["duration_minutes"],
        "comment":       row["notes"],
        "serviceType": [
            {
                "coding": [
                    {
                        "system":  "http://terminology.hl7.org/CodeSystem/service-type",
                        "code":    appt_type,
                        "display": _SERVICE_TYPE_DISPLAY.get(appt_type, appt_type),
                    }
                ]
            }
        ],
        "participant": [
            {
                "actor": {
                    "reference": f"Patient/{row['patient_id']}",
                    "display":   row["patient_name"],
                },
                "required": "required",
                "status":   "accepted",
            },
            {
                "actor": {
                    "reference": f"Practitioner/{row['clinician_id']}",
                    "display":   row["clinician_name"],
                },
                "required": "required",
                "status":   "accepted",
            },
        ],
    }
