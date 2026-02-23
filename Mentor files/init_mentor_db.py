#!/usr/bin/env python3
"""Initialize the MindBridge Mentor database with schema and seed data."""
import sqlite3
import os
from datetime import date

# This will create mentor.db in the current directory
DB_PATH = "mentor.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Learning sessions — tracks what you've studied
    c.execute("""
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            subtopic TEXT,
            mode TEXT NOT NULL,
            score REAL,
            duration_minutes INTEGER,
            notes TEXT,
            session_date TEXT DEFAULT (date('now'))
        )
    """)

    # Flashcards — spaced repetition deck
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            week INTEGER NOT NULL,
            question TEXT NOT NULL,
            ideal_answer TEXT NOT NULL,
            your_best_answer TEXT,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review TEXT DEFAULT (date('now')),
            times_reviewed INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (date('now'))
        )
    """)

    # Interview practice attempts
    c.execute("""
        CREATE TABLE IF NOT EXISTS interview_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_type TEXT NOT NULL,
            questions_json TEXT,
            overall_score REAL,
            feedback TEXT,
            weak_areas TEXT,
            attempt_date TEXT DEFAULT (date('now'))
        )
    """)

    # Curriculum progress tracker
    c.execute("""
        CREATE TABLE IF NOT EXISTS curriculum_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL UNIQUE,
            topic TEXT NOT NULL,
            phase TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            status TEXT DEFAULT 'locked'
        )
    """)

    # Seed curriculum weeks
    curriculum = [
        (1, "Docker & PostgreSQL", "foundation"),
        (2, "FastAPI & REST APIs", "foundation"),
        (3, "Auth & HIPAA Audit", "foundation"),
        (4, "Patient CRUD & AI Integration", "foundation"),
        (5, "AI Product Thinking", "expertise"),
        (6, "Healthcare AI Landscape", "expertise"),
        (7, "AI Safety & Regulation", "expertise"),
        (8, "System Design for Healthcare", "expertise"),
        (9, "Your Story — STAR Method", "interview"),
        (10, "Technical Interviews", "interview"),
        (11, "Healthcare Domain Questions", "interview"),
        (12, "Full Mock Interview Loops", "interview"),
    ]

    c.execute("SELECT COUNT(*) FROM curriculum_progress")
    if c.fetchone()[0] == 0:
        for week, topic, phase in curriculum:
            status = "available" if week == 1 else "locked"
            c.execute(
                "INSERT INTO curriculum_progress (week, topic, phase, status) VALUES (?, ?, ?, ?)",
                (week, topic, phase, status),
            )

    # Seed Week 1 flashcards (12 high-value interview questions)
    week1_cards = [
        (
            "Docker & PostgreSQL", 1,
            "What is Docker and why do we use it for MindBridge?",
            "Docker packages our application and all its dependencies into containers that run identically everywhere. For MindBridge, this means a new developer can run 'docker compose up' and have the entire healthcare platform running in 60 seconds. Without Docker, 'it works on my machine' becomes a patient safety issue when code behaves differently in production."
        ),
        (
            "Docker & PostgreSQL", 1,
            "Why PostgreSQL over MongoDB for a healthcare application?",
            "Three reasons. First, ACID transactions — when recording a screening result, updating risk level, and writing an audit log, ALL three must succeed or NONE do. Second, JSONB columns let us store structured data alongside semi-structured AI responses. Third, Row-Level Security enforces that case managers only see their own patients at the DATABASE level."
        ),
        (
            "Docker & PostgreSQL", 1,
            "What is a database migration and why does MindBridge use Alembic?",
            "A migration is a version-controlled change to the database schema. Alembic tracks every schema change as a numbered migration file. This matters for healthcare because every schema change is auditable, you can roll back bad migrations, and multiple developers stay in sync."
        ),
        (
            "Docker & PostgreSQL", 1,
            "What is a UUID and why does MindBridge use UUIDs instead of auto-increment IDs?",
            "UUIDs are 128-bit universally unique identifiers. We use them for: (1) Security — sequential IDs leak information. (2) Multi-tenant safety — UUIDs never collide when merging databases. (3) HIPAA — UUIDs in URLs don't reveal patient count or ordering."
        ),
        (
            "Docker & PostgreSQL", 1,
            "What does the HIPAA Security Rule require for database storage?",
            "Three categories: Technical (encryption at rest/transit, access controls, audit logging), Physical (secured facilities via cloud BAA), Administrative (access policies, workforce training). For MindBridge: we encrypt PHI fields at application level AND use volume encryption."
        ),
        (
            "Docker & PostgreSQL", 1,
            "INTERVIEW: 'Tell me about a project you've built recently.'",
            "CLINICAL CONTEXT: 'In my 10 years as a Mental Health Technician, I watched case managers spend 6+ hours daily manually assessing patient risk.' TECHNICAL SOLUTION: 'I built MindBridge Health AI using FastAPI, PostgreSQL, and Claude AI that automates risk screening.' BUSINESS IMPACT: 'What took 6 hours now takes 2 minutes with 95%+ sensitivity and full HIPAA compliance.'"
        ),
    ]

    c.execute("SELECT COUNT(*) FROM flashcards WHERE week = 1")
    if c.fetchone()[0] == 0:
        for topic, week, question, answer in week1_cards:
            c.execute(
                "INSERT INTO flashcards (topic, week, question, ideal_answer) VALUES (?, ?, ?, ?)",
                (topic, week, question, answer),
            )

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")
    print(f"  - 12 curriculum weeks seeded")
    print(f"  - {len(week1_cards)} Week 1 flashcards loaded")
    print(f"\n🎯 Your 12-Week Curriculum:")
    for week, topic, phase in curriculum:
        status_icon = "🟢" if week == 1 else "🔒"
        print(f"  {status_icon} Week {week:2d}: {topic} ({phase})")


if __name__ == "__main__":
    init_db()
