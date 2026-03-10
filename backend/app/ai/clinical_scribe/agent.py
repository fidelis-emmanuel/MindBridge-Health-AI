"""
ClinicalScribe AI — single-shot SOAP note extraction.
One Claude call, structured JSON output, no tool loops.
"""
import json
import os
from typing import Any

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048

SYSTEM_PROMPT = """You are ClinicalScribe AI, a medical documentation assistant \
trained on SOAP note format. You work at a behavioral health facility.

Given raw clinical input (voice transcript or handwritten notes),
extract and return ONLY a JSON object with this exact structure:

{
  "subjective": "patient's reported symptoms, complaints, history in their own words",
  "objective": "clinician observations, vitals, mental status exam findings",
  "assessment": "clinical impression, diagnosis, severity",
  "plan": "treatment plan, medications, interventions, disposition",
  "icd10_codes": [{"code": "F32.1", "description": "Major depressive disorder, single episode, moderate"}],
  "medications": [{"name": "Sertraline", "dose": "100mg", "frequency": "daily"}],
  "risk_flags": [{"flag": "suicide_risk", "level": "moderate", "note": "SI without plan"}],
  "follow_up": "next appointment, referrals, pending orders"
}

Return ONLY valid JSON. No preamble, no explanation, no markdown fences. \
If a field cannot be determined from the input, use null.
Be medically precise. Use proper clinical terminology.
Flag ANY mention of: suicidal ideation, homicidal ideation, self-harm, \
substance use, medication non-compliance, or missed appointments as risk_flags.

Important: This is for a behavioral health platform. \
Prioritize mental health ICD-10 codes (F-codes)."""


def _parse_scribe_response(raw_text: str) -> dict[str, Any]:
    """Parse Claude's JSON response. Raises ValueError if malformed."""
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"ClinicalScribe returned malformed output: {e}") from e


async def run_scribe(
    raw_input: str,
    patient_id: int,
    provider_name: str,
) -> dict[str, Any]:
    """
    Call Claude once to extract a structured SOAP note from raw clinical input.

    Returns a dict with all SOAP fields ready for DB insertion.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
    client = anthropic.AsyncAnthropic(api_key=api_key)

    response = await client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_input}],
    )

    raw_text = response.content[0].text
    parsed = _parse_scribe_response(raw_text)

    return {
        "patient_id": patient_id,
        "provider_name": provider_name,
        "raw_input": raw_input,
        **parsed,
    }
