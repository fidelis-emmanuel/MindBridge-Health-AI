import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.ai.clinical_scribe.router import router

app = FastAPI()
app.include_router(router)


def _make_mock_pool(patient_exists=True, insert_id=42):
    """Build a mock asyncpg pool for router tests."""
    mock_conn = MagicMock()
    mock_conn.fetchval = AsyncMock(return_value=1 if patient_exists else 0)
    mock_conn.fetchrow = AsyncMock(return_value={
        "id": insert_id,
        "patient_id": 1,
        "encounter_date": "2026-03-03T00:00:00+00:00",
        "provider_name": "Dr. Test",
        "raw_input": "Patient anxious.",
        "subjective": "Patient anxious.",
        "objective": "HR 90.",
        "assessment": "GAD.",
        "plan": "CBT.",
        "icd10_codes": json.dumps([{"code": "F41.1", "description": "GAD"}]),
        "medications": json.dumps([]),
        "risk_flags": json.dumps([]),
        "follow_up": "4 weeks.",
    })

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=mock_ctx)

    return mock_pool, mock_conn


MOCK_SCRIBE_RESULT = {
    "patient_id": 1,
    "provider_name": "Dr. Test",
    "raw_input": "Patient anxious.",
    "subjective": "Patient anxious.",
    "objective": "HR 90.",
    "assessment": "GAD.",
    "plan": "CBT.",
    "icd10_codes": [{"code": "F41.1", "description": "GAD"}],
    "medications": [],
    "risk_flags": [],
    "follow_up": "4 weeks.",
}


def test_generate_returns_200_with_note():
    mock_pool, _ = _make_mock_pool()
    app.state.pool = mock_pool

    with patch("app.ai.clinical_scribe.router.run_scribe", AsyncMock(return_value=MOCK_SCRIBE_RESULT)):
        client = TestClient(app)
        resp = client.post("/scribe/generate", json={
            "patient_id": 1,
            "raw_input": "Patient anxious.",
            "provider_name": "Dr. Test"
        })

    assert resp.status_code == 200
    data = resp.json()
    assert data["soap_note_id"] == 42
    assert data["assessment"] == "GAD."


def test_generate_returns_404_for_unknown_patient():
    mock_pool, _ = _make_mock_pool(patient_exists=False)
    app.state.pool = mock_pool

    with patch("app.ai.clinical_scribe.router.run_scribe", AsyncMock(return_value=MOCK_SCRIBE_RESULT)):
        client = TestClient(app)
        resp = client.post("/scribe/generate", json={
            "patient_id": 9999,
            "raw_input": "...",
            "provider_name": "Dr. Test"
        })

    assert resp.status_code == 404


def test_generate_returns_422_on_malformed_claude_output():
    mock_pool, _ = _make_mock_pool()
    app.state.pool = mock_pool

    with patch("app.ai.clinical_scribe.router.run_scribe",
               AsyncMock(side_effect=ValueError("ClinicalScribe returned malformed output"))):
        client = TestClient(app)
        resp = client.post("/scribe/generate", json={
            "patient_id": 1,
            "raw_input": "...",
            "provider_name": "Dr. Test"
        })

    assert resp.status_code == 422
