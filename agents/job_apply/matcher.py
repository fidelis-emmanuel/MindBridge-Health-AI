#!/usr/bin/env python3
"""
Scores a job posting against Tobe's profile using keyword matching.
No API calls — fast local scoring.

Score bands:
  85-100  Excellent match
  70-84   Strong match
  40-69   Moderate match
  0-39    Weak match
"""
import re
from agents.job_apply.profile import PROFILE

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+(?:[.\-][a-z0-9]+)*", text.lower()))

def score(job_text: str) -> dict:
    """
    Score a job posting against PROFILE.

    Returns:
        {
            "score": int (0-100),
            "band": str,
            "matched_skills": list[str],
            "matched_roles": list[str],
            "matched_healthcare": list[str],
            "breakdown": dict,
        }
    """
    tokens = _tokens(job_text)

    # Skill hits (+4 each, cap at 45)
    # Match on full phrase OR any significant token (>=2 chars) within multi-word skills
    def _skill_matches(skill: str) -> bool:
        if skill.lower() in job_text.lower():
            return True
        words = skill.lower().split()
        if len(words) > 1:
            return bool(_tokens(skill) & tokens - {w for w in _tokens(skill) if len(w) < 2})
        return False

    matched_skills = [s for s in PROFILE.skills if _skill_matches(s)]
    skill_pts = min(len(matched_skills) * 4, 45)

    # Target role title overlap (+15 if any title word matches)
    matched_roles = []
    for role in PROFILE.target_roles:
        role_words = set(role.lower().split())
        job_words = _tokens(job_text)
        if len(role_words & job_words) >= 2:
            matched_roles.append(role)
    role_pts = 15 if matched_roles else 0

    # Healthcare domain terms (+5 if 2+ present, +10 if 5+)
    matched_hc = [k for k in PROFILE.healthcare_keywords if k.lower() in job_text.lower()]
    hc_pts = 10 if len(matched_hc) >= 5 else (5 if len(matched_hc) >= 2 else 0)

    # AI / data engineering bonus (+5 if present)
    ai_terms = {"machine learning", "artificial intelligence", "ai", "llm",
                "data engineering", "data pipeline", "analytics", "bi", "reporting"}
    ai_pts = 5 if ai_terms & _tokens(job_text) else 0

    raw = skill_pts + role_pts + hc_pts + ai_pts
    final = min(raw, 100)

    bands = [(85, "Excellent"), (70, "Strong"), (40, "Moderate"), (0, "Weak")]
    band = next(label for threshold, label in bands if final >= threshold)

    return {
        "score": final,
        "band": band,
        "matched_skills": matched_skills,
        "matched_roles": matched_roles,
        "matched_healthcare": matched_hc,
        "breakdown": {
            "skills": skill_pts,
            "role_title": role_pts,
            "healthcare": hc_pts,
            "ai_data": ai_pts,
        },
    }
