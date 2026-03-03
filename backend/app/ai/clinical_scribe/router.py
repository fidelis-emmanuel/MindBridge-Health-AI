"""
ClinicalScribe FastAPI router.
Mounts at /scribe in main.py.
"""
import json
from typing import Any

import asyncpg
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.ai.clinical_scribe.agent import run_scribe

router = APIRouter(prefix="/scribe", tags=["ClinicalScribe"])


# ── Request / Response models ─────────────────────────────────────────────────

class ScribeRequest(BaseModel):
    patient_id: int
    raw_input: str
    provider_name: str


class ScribeResponse(BaseModel):
    soap_note_id: int
    patient_id: int
    encounter_date: str
    provider_name: str
    subjective: str | None
    objective: str | None
    assessment: str | None
    plan: str | None
    icd10_codes: list[dict] | None
    medications: list[dict] | None
    risk_flags: list[dict] | None
    follow_up: str | None


# ── Dependency ────────────────────────────────────────────────────────────────

def _get_pool(request: Request) -> asyncpg.Pool:
    pool = request.app.state.pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return pool


# ── Helpers ───────────────────────────────────────────────────────────────────

def _jsonb(value: Any) -> str | None:
    """Serialize a Python value to JSONB-safe string, or None."""
    if value is None:
        return None
    return json.dumps(value)


def _parse_jsonb(value: Any) -> list | None:
    """Deserialize asyncpg JSONB value (may already be parsed)."""
    if value is None:
        return None
    if isinstance(value, str):
        return json.loads(value)
    return value  # asyncpg returns dicts/lists for JSONB columns


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=ScribeResponse)
async def generate_soap_note(body: ScribeRequest, request: Request):
    """
    Generate a structured SOAP note from raw clinical input.
    Saves the note to the soap_notes table linked to patient_id.
    """
    pool = _get_pool(request)

    async with pool.acquire() as conn:
        # Verify patient exists
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM patients WHERE id = $1", body.patient_id
        )
        if not count:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Call Claude
        try:
            note = await run_scribe(
                raw_input=body.raw_input,
                patient_id=body.patient_id,
                provider_name=body.provider_name,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        # Insert into soap_notes
        row = await conn.fetchrow(
            """
            INSERT INTO soap_notes (
                patient_id, provider_name, raw_input,
                subjective, objective, assessment, plan,
                icd10_codes, medications, risk_flags, follow_up
            ) VALUES (
                $1, $2, $3,
                $4, $5, $6, $7,
                $8::jsonb, $9::jsonb, $10::jsonb, $11
            )
            RETURNING id, patient_id, encounter_date, provider_name,
                      subjective, objective, assessment, plan,
                      icd10_codes, medications, risk_flags, follow_up
            """,
            body.patient_id, body.provider_name, body.raw_input,
            note.get("subjective"), note.get("objective"),
            note.get("assessment"), note.get("plan"),
            _jsonb(note.get("icd10_codes")),
            _jsonb(note.get("medications")),
            _jsonb(note.get("risk_flags")),
            note.get("follow_up"),
        )

    return ScribeResponse(
        soap_note_id=row["id"],
        patient_id=row["patient_id"],
        encounter_date=str(row["encounter_date"]),
        provider_name=row["provider_name"],
        subjective=row["subjective"],
        objective=row["objective"],
        assessment=row["assessment"],
        plan=row["plan"],
        icd10_codes=_parse_jsonb(row["icd10_codes"]),
        medications=_parse_jsonb(row["medications"]),
        risk_flags=_parse_jsonb(row["risk_flags"]),
        follow_up=row["follow_up"],
    )


@router.get("/notes/{patient_id}")
async def get_patient_notes(patient_id: int, request: Request):
    """Return all SOAP notes for a patient, newest first."""
    pool = _get_pool(request)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, patient_id, encounter_date, provider_name,
                   subjective, objective, assessment, plan,
                   icd10_codes, medications, risk_flags, follow_up,
                   created_at
            FROM soap_notes
            WHERE patient_id = $1
            ORDER BY encounter_date DESC
            """,
            patient_id,
        )

    return {
        "patient_id": patient_id,
        "notes": [
            {**dict(row), "encounter_date": str(row["encounter_date"])}
            for row in rows
        ],
        "count": len(rows),
    }
