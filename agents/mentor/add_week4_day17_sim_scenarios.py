import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "mentor.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create sim_scenarios table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sim_scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day INTEGER NOT NULL,
        title TEXT NOT NULL,
        scenario TEXT NOT NULL,
        challenge TEXT NOT NULL,
        ideal_response TEXT NOT NULL,
        difficulty TEXT DEFAULT 'intermediate',
        created_at TEXT DEFAULT (date('now'))
    )
""")

scenarios = [
    (
        17,
        "ClinicalScribe: Ambiguous Clinical Notes",
        "A nurse hands you a voice transcript: 'Pt came in. Looks bad. Says things aren't good at home. Meds same as before. Follow up next week.' ClinicalScribe processes this through Claude with the structured JSON system prompt.",
        "What will ClinicalScribe extract into each SOAP section? What will be null? What risk flags might trigger?",
        "Subjective: 'Patient reports things are not good at home' (only patient-reported content). Objective: null — no vitals, no MSE, no scores documented. Assessment: null — no diagnosis can be inferred. Plan: 'Follow up next week; medications unchanged.' Medications: may extract prior medications if mentioned elsewhere, but 'meds same as before' is too vague for extraction — likely null or empty. Risk flags: 'things aren't good at home' could trigger a domestic_situation flag at low level depending on Claude's interpretation. The note is dangerously incomplete — a good system should surface the null fields visually so the clinician knows to add objective findings before signing.",
        "intermediate"
    ),
    (
        17,
        "Database Agent: Query Critical Patients on Missing Medication",
        "A medical director asks the database agent: 'Show me all patients who are HIGH risk and have medication adherence below 70%.' The agent has access to the patients table with columns: id, patient_name, risk_level, medication_adherence, appointments_missed, crisis_calls_30days, diagnosis.",
        "Write the query the database agent would generate and send to query_database. What parameterized SQL would it use?",
        "The agent calls query_database with: sql = 'SELECT id, patient_name, risk_level, medication_adherence, diagnosis FROM patients WHERE risk_level = $1 AND medication_adherence < $2 ORDER BY medication_adherence ASC', params = ['HIGH', 0.70]. Key points: (1) Parameterized with $1, $2 — never string interpolation. (2) ORDER BY medication_adherence ASC shows worst adherence first. (3) SELECT specific columns — not SELECT * — reduces data exposure. (4) The agent should summarize results clinically: 'Found 3 HIGH-risk patients with adherence below 70%: [names, adherence rates, diagnoses]' — not a raw SQL dump.",
        "intermediate"
    ),
    (
        17,
        "Database Agent: run_cleanup Dry Run on Old Appointment Records",
        "An administrator asks the database agent to 'clean up appointment records older than 2 years.' The agent has the run_cleanup tool available.",
        "Walk through the exact sequence of tool calls the agent should make. What safeguards does run_cleanup enforce?",
        "Step 1 — ALWAYS dry_run first: run_cleanup(table='appointments', condition='appointment_date < NOW() - INTERVAL 2 years', dry_run=True). This returns: {'would_delete': 847, 'sample_records': [...first 5 records...]}. Step 2 — Agent reports to user: 'Dry run complete. This would delete 847 appointment records older than 2 years. Sample: [records]. Shall I proceed with actual deletion?' Step 3 — User confirms. Step 4 — run_cleanup with dry_run=False, which writes an audit log entry before deleting. The agent is explicitly instructed to ALWAYS dry_run first and ALWAYS ask for confirmation. Skipping the dry run is a critical mistake — irreversible deletions without preview violate the tool's safety contract.",
        "advanced"
    ),
    (
        17,
        "ClinicalScribe: Behavioral Health Crisis Encounter",
        "A therapist dictates after a crisis visit: 'Patient Marcus W., 34M, presented in acute distress. Reports active suicidal ideation with a plan to use medication overdose. Denies access to firearms. PHQ-9 score 24. Affect constricted, tearful, poor eye contact. Currently on Lithium 300mg TID and Sertraline 50mg daily. Safety plan initiated, contacted crisis team, patient agrees to voluntary hospitalization. Follow-up: admit to inpatient unit, hold all outpatient medications pending inpatient evaluation.'",
        "What does ClinicalScribe extract? Which risk flags trigger? What ICD-10 codes are appropriate?",
        "Subjective: 'Patient reports active suicidal ideation with a plan to use medication overdose. Denies access to firearms.' Objective: 'PHQ-9 score 24 (severe). Affect constricted, tearful, poor eye contact. Acute distress observed.' Assessment: 'Suicidal ideation with plan. Major depressive disorder, severe (F32.2). Safety risk: HIGH.' Plan: 'Safety plan initiated. Crisis team contacted. Voluntary hospitalization agreed. Hold outpatient medications pending inpatient evaluation.' ICD-10: F32.2 (MDD severe without psychosis), T43.595A (poisoning by other antidepressants, undetermined intent — for SI with overdose plan). Risk flags: [{flag: suicide_risk, level: high, note: SI with specific plan — medication overdose}, {flag: hospitalization_indicated, level: high, note: voluntary admission initiated}]. Medications: Lithium 300mg TID, Sertraline 50mg daily.",
        "advanced"
    ),
    (
        17,
        "ICD-10 Code Selection: Dual Diagnosis Patient",
        "Clinical notes: 'Patient presents with 6-week depressive episode meeting MDD criteria AND reports daily alcohol use averaging 8 drinks/day for the past 3 months, with withdrawal symptoms in the morning. Currently managing both in an integrated treatment program.'",
        "What ICD-10 codes should ClinicalScribe extract? How should dual diagnosis be coded?",
        "Dual diagnosis (co-occurring disorders) requires coding BOTH conditions separately. Primary: F32.1 — Major depressive disorder, single episode, moderate (or F32.2 if severe). Secondary: F10.20 — Alcohol use disorder, moderate (8 drinks/day + withdrawal symptoms meets DSM-5 criteria for moderate AUD). F10.232 could apply if alcohol withdrawal is the presenting issue. Important nuance: depression during active alcohol use disorder may remit with sobriety — the clinical note should capture this uncertainty. ClinicalScribe should extract both codes. The clinician must determine primary vs. secondary based on which is driving the current presentation. Common mistake: coding only the mental health condition and missing the substance use disorder, which affects treatment planning and billing.",
        "advanced"
    ),
    (
        17,
        "pg_stat_activity: Diagnosing a Blocking Query",
        "A clinician reports the MindBridge dashboard is loading very slowly. You suspect a blocking query. The database agent has the check_blocking tool.",
        "What does the database agent do? What does pg_stat_activity show, and how do you interpret a lock chain?",
        "Step 1: Agent calls check_blocking(). This queries pg_stat_activity and pg_locks for blocking sessions. Step 2: Output shows something like: Session 1234 (state: idle in transaction, 8 minutes) is holding a lock on patients. Session 5678 (state: active, waiting: true) is blocked waiting for the same lock. Step 3: Interpret the lock chain — Session 1234 opened a transaction (possibly a long-running report query), never committed, and is now blocking all writes. Step 4: Resolution options — (a) terminate session 1234 with pg_terminate_backend(1234) if safe, (b) investigate why the transaction was left open (application bug, connection leak). Root cause: likely a connection that wasn't properly returned to the pool after an error. Prevention: always use async with pool.acquire() as conn: which auto-returns on exception.",
        "advanced"
    ),
    (
        17,
        "Database Agent: create_view for High-Risk Dashboard",
        "The clinical director wants a reusable query that shows all HIGH risk patients with more than 2 crisis calls in 30 days and medication adherence below 80%. This will be run multiple times per week.",
        "What create_view call does the database agent make? Why is a VIEW appropriate here instead of a repeated query?",
        "Agent calls create_view with: name = 'high_risk_crisis_patients', sql = 'SELECT id, patient_name, risk_level, crisis_calls_30days, medication_adherence, diagnosis FROM patients WHERE risk_level = $1 AND crisis_calls_30days > 2 AND medication_adherence < 0.80 ORDER BY crisis_calls_30days DESC'. Wait — VIEWs cannot have parameters ($1). The agent should use literal values or ask for clarification. Correct SQL: WHERE risk_level = 'HIGH' AND crisis_calls_30days > 2 AND medication_adherence < 0.80. Why VIEW: (1) Encapsulates complex business logic — clinicians call 'SELECT * FROM high_risk_crisis_patients' without knowing SQL internals. (2) Single source of truth — change the criteria once, all consumers see the update. (3) Performance — can be materialized if needed. (4) Naming enforces clinical semantics.",
        "intermediate"
    ),
    (
        17,
        "Frontend Debugging: Fetch Fails on Patient Detail Page",
        "A clinician reports the patient detail page at /patients/42 shows an error. The Next.js page fetches from the Railway FastAPI backend. You open the browser DevTools.",
        "Walk through the debugging steps. What are the three most likely causes and how do you confirm each?",
        "Step 1 — Check browser Network tab: look at the request to the FastAPI URL. Status code tells you the category. 404: patient ID 42 doesn't exist in the database — check FastAPI /api/patients/42 directly. 500: FastAPI server error — check Railway logs. CORS error (blocked): missing or wrong CORS origin — FastAPI allow_origins must include the Vercel deployment URL. Step 2 — Check Railway logs for FastAPI: look for Python tracebacks. Common: asyncpg connection error (DATABASE_URL wrong/expired), asyncpg.exceptions.NoDataFoundError. Step 3 — Check environment variables: NEXT_PUBLIC_API_URL on Vercel pointing to the correct Railway URL? If the variable is wrong, ALL API calls fail, not just this patient. Step 4 — Check the patients table: does patient 42 exist? The FastAPI handler raises 404 if not found. Fix: ensure the frontend handles 404 gracefully rather than crashing.",
        "intermediate"
    ),
    (
        17,
        "FastAPI 422: Malformed Claude JSON Response in Production",
        "A clinician submits a clinical note and receives a 422 error: 'ClinicalScribe returned malformed output'. You need to debug this in production.",
        "What caused this error? What are the three scenarios that produce it, and how do you add observability?",
        "The error means Claude's response failed json.loads() in _parse_scribe_response(). Three causes: (1) Claude returned markdown-fenced JSON — e.g., ```json {...} ``` instead of raw JSON. This happens when the system prompt instruction 'Return ONLY valid JSON, no markdown fences' is not followed perfectly. Fix: strip markdown fences before parsing. (2) Claude returned a refusal or safety message — 'I cannot generate medical documentation for...' This is plain text, not JSON. Fix: detect non-JSON responses and return a specific error. (3) Claude's response was truncated due to max_tokens limit being hit. Fix: increase MAX_TOKENS or detect incomplete JSON. Observability: log the raw Claude response text before parsing — this is the single most useful debug tool. Add: logger.debug('Claude raw response: %s', raw_text[:500]). Without this log, you're debugging blind.",
        "advanced"
    ),
    (
        17,
        "Paper Chart to Digital: ClinicalScribe End-to-End Demo",
        "A nurse transcribes this handwritten paper chart entry: 'Seen 3/3/26. Maria S., 28F. Came in anxious, shaking. Heart racing. Avoids crowded places, hasn't been to work in 2 months. On Escitalopram 10mg QD x 3 months, misses doses sometimes. PHQ-9=8, GAD-7=18. Impression: GAD moderate to severe. Plan: increase Escitalopram to 20mg, add hydroxyzine 25mg PRN anxiety, refer CBT. Return 4 weeks.'",
        "Trace the complete ClinicalScribe flow from HTTP request to database row. What is in each field?",
        "Request: POST /scribe/generate {patient_id: [Maria's ID], raw_input: [the note above], provider_name: 'Nurse [Name]'}. Router validates patient exists (fetchval). run_scribe() calls Claude with system prompt + note as user message. Claude returns JSON: {subjective: 'Patient reports anxiety, shaking, racing heart. Avoids crowded places. Has not been to work in 2 months.', objective: 'PHQ-9 score 8 (mild depression). GAD-7 score 18 (severe anxiety). Observable shaking noted.', assessment: 'Generalized anxiety disorder, moderate to severe (F41.1).', plan: 'Increase Escitalopram to 20mg daily. Add hydroxyzine 25mg PRN anxiety. Refer to cognitive behavioral therapy. Return in 4 weeks.', icd10_codes: [{code: F41.1, description: GAD}], medications: [{name: Escitalopram, dose: 20mg, frequency: daily}, {name: hydroxyzine, dose: 25mg, frequency: PRN}], risk_flags: [{flag: medication_non_compliance, level: moderate, note: reports missing doses sometimes}], follow_up: 'Return in 4 weeks.'}. INSERT into soap_notes with JSONB columns. Response: {soap_note_id: N, ...all fields}. Paper chart → structured database row in ~3 seconds.",
        "intermediate"
    ),
]

inserted = 0
skipped = 0

for scenario in scenarios:
    try:
        cursor.execute("""
            INSERT INTO sim_scenarios (day, title, scenario, challenge, ideal_response, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        """, scenario)
        inserted += 1
    except sqlite3.IntegrityError:
        skipped += 1

conn.commit()
conn.close()

print(f"✅ Day 17 simulation scenarios loaded: {inserted} inserted, {skipped} skipped")
print(f"🧪 Scenarios cover:")
print(f"   - ClinicalScribe ambiguous input handling")
print(f"   - Database agent: patient queries, cleanup, view creation")
print(f"   - SOAP crisis note extraction (suicidal ideation)")
print(f"   - ICD-10 dual diagnosis coding")
print(f"   - pg_stat_activity blocking query diagnosis")
print(f"   - FastAPI 422 debugging and observability")
print(f"   - Full paper chart → digital SOAP note flow")
print(f"🎯 {inserted} new scenarios added to sim_scenarios table")
