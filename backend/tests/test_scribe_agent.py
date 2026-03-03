import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_parse_valid_claude_response():
    """agent correctly parses a well-formed JSON response from Claude."""
    from app.ai.clinical_scribe.agent import _parse_scribe_response

    raw_json = json.dumps({
        "subjective": "Patient reports low mood for 2 weeks.",
        "objective": "Flat affect, poor eye contact.",
        "assessment": "Major depressive disorder, moderate.",
        "plan": "Start Sertraline 50mg daily.",
        "icd10_codes": [{"code": "F32.1", "description": "MDD single episode moderate"}],
        "medications": [{"name": "Sertraline", "dose": "50mg", "frequency": "daily"}],
        "risk_flags": [],
        "follow_up": "Return in 2 weeks."
    })

    result = _parse_scribe_response(raw_json)

    assert result["subjective"] == "Patient reports low mood for 2 weeks."
    assert result["icd10_codes"][0]["code"] == "F32.1"
    assert result["risk_flags"] == []


@pytest.mark.asyncio
async def test_parse_invalid_json_raises():
    """agent raises ValueError on malformed Claude response."""
    from app.ai.clinical_scribe.agent import _parse_scribe_response

    with pytest.raises(ValueError, match="malformed"):
        _parse_scribe_response("This is not JSON at all")


@pytest.mark.asyncio
async def test_run_scribe_calls_claude_and_returns_parsed_note():
    """run_scribe makes one Claude API call and returns structured note."""
    from app.ai.clinical_scribe.agent import run_scribe

    mock_response_text = json.dumps({
        "subjective": "Patient anxious.",
        "objective": "HR 90, restless.",
        "assessment": "Generalized anxiety disorder.",
        "plan": "CBT referral.",
        "icd10_codes": [{"code": "F41.1", "description": "GAD"}],
        "medications": [],
        "risk_flags": [],
        "follow_up": "4 weeks."
    })

    mock_block = MagicMock()
    mock_block.text = mock_response_text

    mock_message = MagicMock()
    mock_message.content = [mock_block]

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)

    with patch("app.ai.clinical_scribe.agent.anthropic.AsyncAnthropic", return_value=mock_client):
        result = await run_scribe(
            raw_input="Patient is very anxious, can't sleep.",
            patient_id=1,
            provider_name="Dr. Test"
        )

    assert result["assessment"] == "Generalized anxiety disorder."
    assert result["icd10_codes"][0]["code"] == "F41.1"
