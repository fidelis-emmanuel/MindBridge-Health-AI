#!/usr/bin/env python3
"""
MindBridge Patient Seeder — scripts/seed_patients.py
Adds patients to reach a total of 50 in Railway PostgreSQL.

Usage:
    Windows PowerShell:
        $env:DATABASE_URL="postgresql://..."; python scripts/seed_patients.py
    Linux/macOS:
        DATABASE_URL="postgresql://..." python3 scripts/seed_patients.py

Install dependency if missing:
    pip install psycopg2-binary
"""
import os
import sys

# ── Driver check ────────────────────────────────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("❌  psycopg2 not found. Install it with:")
    print("       pip install psycopg2-binary")
    sys.exit(1)

# ── Connection ───────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("❌  DATABASE_URL environment variable is not set.")
    print("    Run:  $env:DATABASE_URL=\"postgresql://...\"; python scripts/seed_patients.py")
    sys.exit(1)

# ── Patient data ─────────────────────────────────────────────────────────────
# Columns: (patient_name, risk_level, medication_adherence, appointments_missed,
#            crisis_calls_30days, diagnosis)
#
# risk_level values: LOW | MEDIUM | HIGH | CRITICAL
# medication_adherence: 0.0–1.0 float
# appointments_missed:  0–8
# crisis_calls_30days:  0–5

NEW_PATIENTS = [
    # ── CRITICAL (6) ──────────────────────────────────────────────────────
    ("Robert Kim",       "CRITICAL", 0.15, 7, 5, "Schizophrenia, paranoid type"),
    ("Priya Patel",      "CRITICAL", 0.10, 8, 5, "Schizoaffective Disorder, depressive type"),
    ("Hannah Kim",       "CRITICAL", 0.08, 8, 4, "Major Depressive Disorder, severe, recurrent, with suicidal ideation"),
    ("Ethan Robinson",   "CRITICAL", 0.12, 7, 5, "Schizoaffective Disorder, bipolar type"),
    ("Zoe Martinez",     "CRITICAL", 0.05, 8, 5, "Schizophrenia, catatonic type"),
    ("Brianna Jackson",  "CRITICAL", 0.20, 6, 4, "Schizoaffective Disorder, depressive type, with psychosis"),

    # ── HIGH (12) ─────────────────────────────────────────────────────────
    ("Maria Santos",     "HIGH", 0.45, 3, 2, "Bipolar I Disorder, manic episode with psychotic features"),
    ("Derek Washington", "HIGH", 0.38, 5, 3, "Major Depressive Disorder, severe, with psychotic features"),
    ("Sofia Okonkwo",    "HIGH", 0.42, 4, 2, "Bipolar II Disorder, hypomanic, rapid cycling"),
    ("Jamal Brown",      "HIGH", 0.33, 5, 3, "Borderline Personality Disorder with self-harm history"),
    ("Grace Liu",        "HIGH", 0.40, 4, 2, "Schizophrenia, undifferentiated type"),
    ("Keisha Davis",     "HIGH", 0.35, 4, 2, "Major Depressive Disorder, recurrent severe"),
    ("Marcus Williams",  "HIGH", 0.28, 6, 3, "Bipolar I Disorder, mixed features"),
    ("Jordan Reed",      "HIGH", 0.48, 3, 2, "Borderline Personality Disorder with dissociative episodes"),
    ("Leila Mansouri",   "HIGH", 0.36, 4, 2, "Major Depressive Disorder, recurrent, treatment-resistant"),
    ("Elijah Foster",    "HIGH", 0.42, 3, 2, "PTSD, assault-related, severe"),
    ("Isabelle Martin",  "HIGH", 0.31, 5, 3, "Major Depressive Disorder, severe, with melancholic features"),
    ("Mateo Gonzalez",   "HIGH", 0.39, 4, 2, "Schizophrenia, residual type"),

    # ── MEDIUM (12) ───────────────────────────────────────────────────────
    ("Aisha Johnson",    "MEDIUM", 0.72, 2, 1, "PTSD, combat-related"),
    ("Linda Nguyen",     "MEDIUM", 0.65, 2, 0, "Generalized Anxiety Disorder"),
    ("Nathan Clarke",    "MEDIUM", 0.78, 1, 0, "Social Anxiety Disorder, moderate"),
    ("Vincent Morales",  "MEDIUM", 0.68, 2, 1, "PTSD, civilian, motor vehicle accident"),
    ("Fatima Al-Hassan", "MEDIUM", 0.74, 1, 0, "Panic Disorder with agoraphobia"),
    ("Alexander Petrov", "MEDIUM", 0.70, 2, 0, "Generalized Anxiety Disorder with comorbid depression"),
    ("Amara Diallo",     "MEDIUM", 0.66, 2, 1, "PTSD, childhood trauma"),
    ("Nina Sharma",      "MEDIUM", 0.71, 2, 0, "Social Anxiety Disorder with selective mutism history"),
    ("Tyler Anderson",   "MEDIUM", 0.73, 1, 0, "Generalized Anxiety Disorder"),
    ("Darius Johnson",   "MEDIUM", 0.67, 2, 1, "Bipolar II Disorder, depressive phase"),
    ("Aaliyah White",    "MEDIUM", 0.76, 1, 0, "Panic Disorder with infrequent episodes"),
    ("Charlotte Evans",  "MEDIUM", 0.69, 2, 0, "Generalized Anxiety Disorder with somatic symptoms"),

    # ── LOW (10) ──────────────────────────────────────────────────────────
    ("Thomas O'Brien",   "LOW", 0.88, 0, 0, "OCD, primarily obsessional type, in remission"),
    ("Carlos Rivera",    "LOW", 0.92, 0, 0, "Adjustment Disorder with depressed mood"),
    ("Rebecca Thompson", "LOW", 0.90, 0, 0, "Specific Phobia, situational type, in treatment"),
    ("Samuel Carter",    "LOW", 0.85, 1, 0, "Persistent Depressive Disorder, mild"),
    ("Mei Chen",         "LOW", 0.93, 0, 0, "OCD, contamination subtype, well-controlled"),
    ("Connor Sullivan",  "LOW", 0.87, 1, 0, "Major Depressive Disorder, mild, first episode"),
    ("Isaiah Brooks",    "LOW", 0.91, 0, 0, "Adjustment Disorder with anxiety, situational"),
    ("Valentina Cruz",   "LOW", 0.89, 0, 0, "OCD, hoarding subtype, in maintenance therapy"),
    ("Owen Hughes",      "LOW", 0.94, 0, 0, "Specific Phobia, natural environment type"),
    ("Sebastian Park",   "LOW", 0.86, 1, 0, "ADHD, primarily inattentive presentation, managed"),
]

TARGET_TOTAL = 50


def main() -> None:
    print("=" * 65)
    print("🏥  MindBridge Patient Seeder")
    print("=" * 65)

    # ── Connect ──────────────────────────────────────────────────────────
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        conn.autocommit = False
        cur = conn.cursor()
        print("✅  Connected to Railway PostgreSQL")
    except Exception as e:
        print(f"❌  Connection failed: {e}")
        sys.exit(1)

    # ── Current count ─────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM patients;")
    current_count: int = cur.fetchone()[0]
    print(f"📊  Current patient count: {current_count}")

    if current_count >= TARGET_TOTAL:
        print(f"✅  Already at or above {TARGET_TOTAL} patients — nothing to insert.")
        cur.close()
        conn.close()
        return

    needed = TARGET_TOTAL - current_count
    to_insert = NEW_PATIENTS[:needed]
    print(f"➕  Inserting {len(to_insert)} patients to reach {TARGET_TOTAL} total...")

    # ── Insert ────────────────────────────────────────────────────────────
    try:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO patients
                (patient_name, risk_level, medication_adherence,
                 appointments_missed, crisis_calls_30days, diagnosis)
            VALUES %s
            """,
            to_insert,
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌  Insert failed: {e}")
        cur.close()
        conn.close()
        sys.exit(1)

    # ── Summary ───────────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM patients;")
    final_count: int = cur.fetchone()[0]

    cur.execute("""
        SELECT risk_level, COUNT(*) AS n
        FROM patients
        GROUP BY risk_level
        ORDER BY CASE risk_level
            WHEN 'CRITICAL' THEN 1
            WHEN 'HIGH'     THEN 2
            WHEN 'MEDIUM'   THEN 3
            WHEN 'LOW'      THEN 4
        END;
    """)
    distribution = cur.fetchall()

    cur.execute("""
        SELECT diagnosis, COUNT(*) AS n
        FROM patients
        GROUP BY diagnosis
        ORDER BY n DESC
        LIMIT 5;
    """)
    top_diagnoses = cur.fetchall()

    cur.close()
    conn.close()

    print()
    print("=" * 65)
    print(f"✅  Done — {final_count} patients now in Railway PostgreSQL")
    print("=" * 65)

    icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
    print("\nRISK DISTRIBUTION")
    print("-" * 35)
    for level, count in distribution:
        bar = "█" * count
        print(f"  {icons.get(level, '⚪')} {level:<8} {count:>3}  {bar}")

    print("\nTOP 5 DIAGNOSES")
    print("-" * 35)
    for diag, count in top_diagnoses:
        short = diag[:50] + ("…" if len(diag) > 50 else "")
        print(f"  {count:>3}x  {short}")

    print()
    print("🎯  50-patient dataset ready for MindBridge Database Agent demo.")
    print("=" * 65)


if __name__ == "__main__":
    main()
