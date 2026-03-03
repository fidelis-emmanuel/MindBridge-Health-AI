import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "mentor.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cards = [
    # ── ClinicalScribe AI Architecture ──────────────────────────────────────
    (
        "What is the single-shot extraction pattern used by ClinicalScribe AI?",
        "Single-shot extraction means sending one carefully engineered request to Claude and receiving a complete structured response in a single API call — no tool loops, no back-and-forth. ClinicalScribe sends the raw clinical transcript as the user message, with a system prompt specifying the exact JSON schema to return. Claude returns ONLY valid JSON with all SOAP fields, ICD-10 codes, medications, and risk flags extracted in one pass. This works because the task is deterministic: given clinical text, always produce the same structured output. Contrast with the database_agent, which uses a tool-calling loop because it must decide which queries to run based on the response.",
        "CON", 0, 2.5, 1
    ),
    (
        "Why does ClinicalScribe use claude-sonnet-4-6 instead of claude-opus-4-5?",
        "Model selection should match task complexity. ClinicalScribe does single-shot structured extraction — given raw text, return JSON. This is a well-defined, deterministic task that does not require Opus-level reasoning. claude-sonnet-4-6 handles it accurately at ~3x lower cost per call and with faster response times, which matters for clinical staff waiting at a workstation. The database_agent uses claude-opus-4-5 because it faces genuinely complex multi-step reasoning: deciding which of 4 tools to call, interpreting query results, chaining multiple tool calls to answer ambiguous clinical questions. Rule of thumb: Sonnet for structured extraction, Opus for open-ended reasoning loops.",
        "CON", 0, 2.5, 1
    ),
    (
        "What happens when ClinicalScribe receives a response that is not valid JSON?",
        "_parse_scribe_response() attempts json.loads() on the stripped response text. If it fails with JSONDecodeError, it raises ValueError with the message 'ClinicalScribe returned malformed output: <error detail>'. The FastAPI router catches ValueError from run_scribe() and raises HTTPException(status_code=422, detail=str(e)). The client receives a 422 Unprocessable Entity response. This is the correct status code: the request was well-formed, but the AI's output could not be processed into the expected structure.",
        "CON", 0, 2.5, 1
    ),
    # ── SOAP Note Structure ──────────────────────────────────────────────────
    (
        "Define each section of a SOAP note and what it documents.",
        "S — Subjective: what the patient reports in their own words. Chief complaint, history of present illness, symptoms, duration, severity. Example: 'Patient reports feeling hopeless for 2 weeks, difficulty sleeping, decreased appetite.' O — Objective: what the clinician observes and measures. Vital signs, mental status exam findings (affect, cognition, behavior), lab results, screening scores (PHQ-9, GAD-7). Example: 'Flat affect, poor eye contact, PHQ-9 score 16.' A — Assessment: the clinician's clinical interpretation. Diagnosis, severity, clinical impression. Example: 'Major depressive disorder, single episode, moderate (F32.1).' P — Plan: what happens next. Medications, therapy referrals, follow-up appointments, pending orders. Example: 'Increase Sertraline to 150mg, refer to CBT, return in 2 weeks.'",
        "CON", 0, 2.5, 1
    ),
    (
        "Why does clinical documentation use SOAP format instead of free-text notes?",
        "SOAP format enforces completeness and standardization. A clinician who writes free-text may skip objective findings or omit the plan. SOAP creates a checklist: if Assessment is blank, the note is incomplete. For healthcare AI systems like ClinicalScribe, SOAP is ideal because it maps to a fixed schema — each section becomes a database column. This enables structured search ('find all patients where Assessment mentions MDD'), quality audits, and population health analytics. HIPAA requires complete, accurate medical records — SOAP format is a clinical best practice that supports this. Paper charting in SOAP format is standard; ClinicalScribe converts that free-text SOAP into structured, queryable database records.",
        "CON", 0, 2.5, 1
    ),
    # ── ICD-10 F-codes ───────────────────────────────────────────────────────
    (
        "What are the key ICD-10 F-codes for behavioral health and what do they represent?",
        "ICD-10 F-codes are the mental and behavioral disorder classification. Key codes: F32.x — Major depressive disorder, single episode (F32.0 mild, F32.1 moderate, F32.2 severe without psychosis, F32.3 severe with psychosis). F33.x — MDD, recurrent. F41.1 — Generalized anxiety disorder. F41.0 — Panic disorder. F20.x — Schizophrenia. F31.x — Bipolar disorder. F43.10 — PTSD. F43.20 — Adjustment disorder. ClinicalScribe's system prompt explicitly instructs Claude to prioritize F-codes (behavioral health ICD-10 codes) because the platform serves a behavioral health facility. Correct ICD-10 coding is required for insurance billing, care coordination, and population health reporting.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the difference between F32 and F33 in ICD-10?",
        "F32 — Major depressive disorder, single episode: the patient has had one depressive episode. F33 — Major depressive disorder, recurrent: the patient has had two or more separate depressive episodes with a period of at least 2 months between them where criteria were not met. The distinction matters clinically: recurrent MDD has higher risk of future episodes and suicide, and typically warrants longer-term maintenance treatment. For coding accuracy: F32.1 = single episode, moderate. F33.1 = recurrent episode, moderate. ClinicalScribe extracts ICD-10 codes from clinical context — if the transcript mentions 'third depressive episode,' the correct code is F33, not F32.",
        "CON", 0, 2.5, 1
    ),
    # ── FastAPI Dependency Injection ─────────────────────────────────────────
    (
        "How does FastAPI dependency injection work and how is it used in MindBridge?",
        "FastAPI's Depends() system automatically resolves and injects values into route functions. You define a dependency function, then declare it as a parameter type: async def endpoint(pool: asyncpg.Pool = Depends(get_pool)). FastAPI calls get_pool() before calling the endpoint, injects the result, and handles exceptions raised in the dependency. MindBridge uses two patterns: (1) database_agent router uses Depends(get_pool) with a function that reads request.app.state.pool. (2) ClinicalScribe router uses a direct helper _get_pool(request: Request) called inline — simpler for a single router with no shared dependency logic. Both patterns are valid; Depends() is cleaner when the dependency is reused across multiple routers.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is request.app.state in FastAPI and why does MindBridge use it for the DB pool?",
        "request.app.state is a namespace attached to the FastAPI application instance for storing application-level state that should be shared across all requests. MindBridge creates the asyncpg connection pool once at startup (inside the lifespan context manager) and stores it as app.state.pool. Each request then reads from this shared pool via request.app.state.pool. Why not a global variable? Global variables can cause issues with testing (hard to mock), multiple workers (each process has its own globals), and lifespan management. app.state is the FastAPI-idiomatic way to share state because it's scoped to the app instance, accessible in route handlers via request.app, and cleaned up when the lifespan exits.",
        "CON", 0, 2.5, 1
    ),
    # ── asyncpg Pool Patterns ────────────────────────────────────────────────
    (
        "What are the four main asyncpg methods used in MindBridge and when do you use each?",
        "fetchrow(query, *args) — returns one Record or None. Use when expecting exactly one result: SELECT * FROM patients WHERE id = $1. fetchval(query, *args) — returns a single scalar value (first column of first row). Use for COUNT(*), EXISTS, or single-value queries: SELECT COUNT(*) FROM patients WHERE id = $1. fetch(query, *args) — returns a list of Records. Use for multi-row results: SELECT * FROM soap_notes WHERE patient_id = $1. execute(query, *args) — runs a DML statement (INSERT/UPDATE/DELETE) and returns a status string. Use when you don't need the result back. All four are called within async with pool.acquire() as conn:, which checks out a connection from the pool and returns it when done.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is an asyncpg connection pool and why does MindBridge use min_size=2, max_size=10?",
        "A connection pool maintains a set of pre-established database connections, reusing them across requests instead of creating a new TCP connection for every query. Connection setup takes 50-200ms — unacceptable for a real-time dashboard. min_size=2 means 2 connections are always open, ready immediately even during quiet periods. max_size=10 caps peak concurrency: if 10 case managers query simultaneously, all get a connection. The 11th request waits until one is released. For a behavioral health clinic with 10-15 case managers per shift, max_size=10 is appropriate. A hospital system with hundreds of concurrent users would need a higher max_size or a connection pooler like PgBouncer in front of PostgreSQL.",
        "CON", 0, 2.5, 1
    ),
    # ── PostgreSQL JSONB ─────────────────────────────────────────────────────
    (
        "When should you use PostgreSQL JSONB columns instead of TEXT or normalized tables?",
        "Use JSONB when: (1) The structure varies between rows — different patients may have different numbers of medications. (2) You need to query into the JSON — JSONB supports indexes and operators like @> (contains). (3) The data is semi-structured but needs to stay with the parent row. soap_notes uses JSONB for icd10_codes, medications, and risk_flags because each note may have 0-10 codes/medications/flags, the structure is consistent but count varies, and querying 'all notes with ICD code F32.1' is possible with JSONB. Use TEXT for opaque storage (raw_input, follow_up). Use normalized tables when you need joins, foreign keys, or complex queries across the nested data — e.g., if you needed a medications history report across all patients, a separate medications table would be better than querying JSONB across 1000 notes.",
        "CON", 0, 2.5, 1
    ),
    (
        "How does asyncpg handle JSONB columns — what does _parse_jsonb() solve?",
        "asyncpg automatically deserializes JSONB columns from PostgreSQL into Python dicts/lists for SELECT queries. For INSERT, you must serialize Python objects to a JSON string and cast with ::jsonb. ClinicalScribe's _jsonb() helper does json.dumps(value) before passing to asyncpg INSERT. The _parse_jsonb() helper handles the reverse for the RETURNING clause: in testing, mock fetchrow() returns a plain JSON string (not a deserialized dict), so _parse_jsonb() checks isinstance(value, str) and json.loads() it. In production against real PostgreSQL, asyncpg returns the already-deserialized dict/list, so _parse_jsonb() returns it as-is. This dual handling makes the code work correctly in both production and test environments.",
        "CON", 0, 2.5, 1
    ),
    # ── AI Tool-Calling vs Single-Shot ───────────────────────────────────────
    (
        "What are the tradeoffs between AI tool-calling loops and single-shot extraction?",
        "Tool-calling loops (database_agent): Claude sees intermediate results and can adapt — if query returns 0 rows, it can try a different query. Handles ambiguous, open-ended tasks. Supports multi-step workflows (query → analyze → summarize). Cost: multiple API round trips (3-10x tokens), 5-30 second latency, harder to test (non-deterministic paths). Single-shot extraction (ClinicalScribe): One API call, predictable latency (2-4s), deterministic output, easy to unit test with mocks, 3x cheaper. Requires the task to be well-defined with a fixed output schema. Rule: use tool-calling when Claude needs to discover information or adapt based on intermediate results. Use single-shot when the transformation is fully defined (input → fixed schema output).",
        "CON", 0, 2.5, 1
    ),
    # ── Database Agent Tool Patterns ─────────────────────────────────────────
    (
        "What are the four tools available to the MindBridge database agent?",
        "check_blocking — queries pg_stat_activity to find slow or blocked queries in PostgreSQL. Returns lock chains, waiting queries, and the blocking session info. Used to diagnose performance issues. query_database — executes safe SELECT queries against patient data using parameterized queries ($1, $2...). Never allows DDL or DML. Used for clinical data retrieval. create_view — creates reusable PostgreSQL VIEWs with descriptive clinical names (e.g., high_risk_patients_missing_meds). Used to encapsulate common query patterns. run_cleanup — safely deletes records with audit logging. Always does a dry_run first (returns what WOULD be deleted), then requires confirmation before actual deletion. The agent is instructed to ALWAYS dry_run first and ask for confirmation before any cleanup.",
        "CON", 0, 2.5, 1
    ),
    # ── Clinical Risk Flags ──────────────────────────────────────────────────
    (
        "What clinical risk flags does ClinicalScribe detect and why does each matter?",
        "ClinicalScribe's system prompt instructs Claude to flag ANY mention of: Suicidal ideation (SI) — immediate safety risk, requires crisis protocol and documentation. Homicidal ideation (HI) — Tarasoff duty to warn, mandatory reporting. Self-harm — indicates non-suicidal self-injury, requires safety planning. Substance use — complicates psychiatric medications, affects diagnosis, may require separate substance use treatment. Medication non-compliance — increases relapse risk, may indicate side effects or financial barriers. Missed appointments — early warning of disengagement, dropout risk. Each flag includes: flag name, level (high/moderate/low), and a clinical note explaining the context. In the frontend, high flags show red badges, moderate show yellow — giving the reviewing clinician immediate visual triage.",
        "CON", 0, 2.5, 1
    ),
    (
        "INTERVIEW: How does ClinicalScribe AI improve patient safety at a behavioral health facility?",
        "Three mechanisms. First, completeness: paper charting relies on the clinician remembering to document every element. ClinicalScribe systematically extracts all SOAP sections, ICD-10 codes, and medications from the raw transcript — nothing gets missed because the clinician was rushed. Second, risk flagging: the system automatically scans every note for suicidal ideation, homicidal ideation, medication non-compliance, and substance use — surfacing them as color-coded badges before the clinician signs the note. A clinician might scan a 10-page paper chart and miss a passing mention of SI; AI catches it every time. Third, searchability: structured JSONB storage means the clinical team can query 'all patients with SI flag in the last 30 days' — impossible with paper charts. The system doesn't replace clinical judgment; it ensures the information is never lost.",
        "INT", 0, 2.5, 1
    ),
    # ── HIPAA and Clinical AI ────────────────────────────────────────────────
    (
        "What HIPAA considerations apply when sending clinical notes to an AI API?",
        "HIPAA's Privacy Rule covers Protected Health Information (PHI) — any information that could identify a patient combined with health data. Sending clinical notes containing patient names, dates, diagnoses to a third-party AI API requires: (1) A Business Associate Agreement (BAA) with the AI provider. Anthropic offers BAAs for enterprise customers. Without a BAA, this violates HIPAA. (2) The AI provider must not train on PHI without explicit consent. (3) Data must be encrypted in transit (TLS) — API calls always use HTTPS. (4) Access logging — who called the API with what data. For a demo/portfolio environment with fictional data (as MindBridge uses), HIPAA doesn't technically apply, but the architecture is designed to be HIPAA-compliant with real PHI by following these principles.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is a Business Associate Agreement (BAA) and when is it required for clinical AI?",
        "A BAA is a legal contract between a HIPAA-covered entity (hospital, clinic) and a business associate (any vendor who handles PHI on the entity's behalf). It specifies: how PHI will be protected, breach notification requirements, restrictions on PHI use, and liability. Required when: sending patient data to cloud APIs (AI providers, analytics platforms), using cloud storage for PHI, any third-party that processes PHI as part of your service. ClinicalScribe architecture: the hospital must have a BAA with Anthropic before sending real patient transcripts to the Claude API. Without it, even a single API call with real PHI is a HIPAA violation. MindBridge's demo environment uses fictional patient data specifically to avoid this requirement during development.",
        "CON", 0, 2.5, 1
    ),
    (
        "INTERVIEW: Walk me through how you'd build a HIPAA-compliant AI documentation system.",
        "Four layers. Architecture: clinical notes never leave the hospital network unencrypted. AI API calls use TLS. Consider on-premise LLM deployment for maximum PHI control. Legal: BAA with AI provider (Anthropic, Azure OpenAI, etc.) before any PHI touches the API. AI providers must commit to not training on your data. Access control: role-based — only treating clinicians can generate and view notes. Audit logging on every API call: who, when, what patient, what was generated. Data handling: raw transcripts stored encrypted at rest (AES-256). Generated SOAP notes stored in PostgreSQL with column-level encryption for PHI fields. Retention policies per state law (typically 7-10 years). The system I built — ClinicalScribe — implements all four layers in the architecture, with the BAA requirement documented as the production deployment prerequisite.",
        "INT", 0, 2.5, 1
    ),
]

inserted = 0
skipped = 0

for card in cards:
    try:
        cursor.execute("""
            INSERT INTO cards (question, answer, card_type, repetitions, ease_factor, interval)
            VALUES (?, ?, ?, ?, ?, ?)
        """, card)
        inserted += 1
    except sqlite3.IntegrityError:
        skipped += 1

conn.commit()
conn.close()

print(f"✅ Day 17 cards loaded: {inserted} inserted, {skipped} skipped")
print(f"📚 Topics: ClinicalScribe architecture, SOAP notes, ICD-10 F-codes, FastAPI DI,")
print(f"          asyncpg patterns, JSONB, AI extraction tradeoffs, risk flags, HIPAA")
print(f"🎯 {inserted} new cards added to mentor.db")
