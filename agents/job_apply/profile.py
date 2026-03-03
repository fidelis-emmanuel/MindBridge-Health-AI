#!/usr/bin/env python3
"""
Tobe's professional profile for job matching and cover letter generation.
Edit this file to update skills, roles, or experience as you grow.
"""
from dataclasses import dataclass, field

@dataclass
class Profile:
    name: str
    title: str
    email: str
    location: str
    summary: str
    skills: list[str]
    target_roles: list[str]
    current_employer: str
    current_role: str
    projects: list[str]
    healthcare_keywords: list[str]

PROFILE = Profile(
    name="Tobe Fidelis Emmanuel",
    title="Healthcare AI Engineer (Transitioning)",
    email="",
    location="",
    summary=(
        "Healthcare professional transitioning into AI engineering with a background "
        "in behavioral health operations and data/business analysis. Currently building "
        "MindBridge Health AI — a full-stack platform using Next.js, FastAPI, PostgreSQL, "
        "and Claude API with AI agent architecture. Day 16 of a structured 90-day "
        "Healthcare AI Engineering program. Bridging clinical domain knowledge with "
        "modern AI engineering practices."
    ),
    skills=[
        "Python", "FastAPI", "PostgreSQL", "asyncpg", "Next.js", "React",
        "Claude API", "Anthropic SDK", "AI agent architecture", "SQLite",
        "REST API design", "asyncpg", "psycopg2", "Railway", "Docker",
        "EHR systems", "HIPAA compliance", "HL7", "FHIR",
        "healthcare workflows", "behavioral health",
        "data analysis", "business analysis", "SQL", "reporting",
        "TypeScript", "JavaScript", "Git",
    ],
    target_roles=[
        "Healthcare AI Engineer",
        "Sr. Business Analyst Digital Health",
        "Applications Support Analyst",
        "Data Reporting Analyst",
        "Clinical Data Analyst",
        "Health Informatics Analyst",
        "AI Product Manager Healthcare",
    ],
    current_employer="Wellstone Regional Hospital",
    current_role="Bridge role (started 03/02/2026)",
    projects=[
        "MindBridge Health AI — Next.js + FastAPI + PostgreSQL + Claude AI agents (Day 16 of 90-day program)",
        "AI Database Agent — natural language → SQL via Claude agentic loop",
        "Patient risk stratification system — 50-patient PostgreSQL dataset on Railway",
    ],
    healthcare_keywords=[
        "healthcare", "clinical", "behavioral health", "mental health",
        "EHR", "EMR", "HIPAA", "HL7", "FHIR", "patient", "hospital",
        "physician", "care coordination", "population health",
        "health informatics", "digital health", "telehealth",
    ],
)
