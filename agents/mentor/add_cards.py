#!/usr/bin/env python3
"""
Add remaining Week 1 cards + Week 2 cards to mentor database.
Run once: python agents/mentor/add_cards.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mentor.db")


def add_cards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ── WEEK 1: Remaining Cards (Cards 7-12) ────────────────────────
    week1_remaining = [
        (
            "Docker & PostgreSQL", 1,
            "What is connection pooling and why does MindBridge need it?",
            "Connection pooling reuses database connections instead of opening a new one for every request. Opening a PostgreSQL connection takes 50-100ms. If 100 case managers hit the dashboard simultaneously, that's 100 × 100ms = 10 seconds of just connection overhead. SQLAlchemy's async engine maintains a pool so concurrent requests reuse existing connections — critical for a multi-user healthcare platform.",
            "concept"
        ),
        (
            "Docker & PostgreSQL", 1,
            "What is a partial index and why does MindBridge use one?",
            "A partial index only indexes rows matching a condition. Our idx_patients_risk has WHERE deleted_at IS NULL — it only indexes active patients. Since HIPAA requires soft deletes (we never hard-delete patient records), our table grows over time with deleted records. Without a partial index, every query scans deleted patients too. With it, dashboard queries only touch the active patient subset — faster queries, smaller index.",
            "concept"
        ),
        (
            "Docker & PostgreSQL", 1,
            "SIMULATION: You're a case manager. Walk me through what happens when I log into MindBridge.",
            "AUTHENTICATION FLOW: (1) You enter email + password on the Next.js login page. (2) NextAuth.js sends credentials to FastAPI POST /api/auth/verify. (3) FastAPI validates against PostgreSQL — checks password hash using bcrypt. (4) If MFA is enabled, prompts for second factor. (5) FastAPI returns JWT token + your role (case_manager). (6) NextAuth stores session in httpOnly cookie (can't be stolen by JavaScript). (7) Dashboard loads — FastAPI queries only YOUR patients based on your user_id. Every action is logged to the HIPAA audit trail.",
            "simulation"
        ),
        (
            "Docker & PostgreSQL", 1,
            "What is the difference between docker compose up and docker compose up --build?",
            "'docker compose up' starts containers using existing images. 'docker compose up --build' rebuilds images first. Use --build when you've changed Dockerfile or requirements.txt (new dependencies). Skip --build when you only changed Python code (volume mount handles hot-reload). Rule of thumb: changed requirements.txt? Use --build. Changed app/main.py? Just restart.",
            "concept"
        ),
        (
            "Docker & PostgreSQL", 1,
            "INTERVIEW SIMULATION: 'Why should we hire you over someone with a Computer Science degree?'",
            "IDEAL ANSWER: 'Computer Science degrees teach algorithms and theory — valuable, but they don't teach you why a patient misses their medication or what a crisis call at 2 AM looks like. In my 10 years as a Mental Health Technician and CNA, I've seen exactly the problems that MindBridge solves. I know that a high-risk flag at 8 PM means a real person in crisis, not just a database record. I can build the AI system AND tell you when the AI is wrong based on clinical context. You can teach a CS grad to use FastAPI in 6 months. You cannot teach 10 years of behavioral health experience.'",
            "simulation"
        ),
        (
            "Docker & PostgreSQL", 1,
            "What is a health check in Docker and why does MindBridge use it?",
            "A health check is a command Docker runs periodically to verify a container is working. PostgreSQL runs 'pg_isready -U mindbridge' every 5 seconds. If it fails 5 times, Docker marks the container unhealthy. The backend has 'depends_on: db: condition: service_healthy' — FastAPI won't start until PostgreSQL is confirmed ready. Without this, the backend could crash on startup trying to connect to a database still initializing.",
            "concept"
        ),
    ]

    # ── WEEK 2: FastAPI & REST APIs (12 cards) ──────────────────────
    week2_cards = [
        (
            "FastAPI & REST APIs", 2,
            "What is FastAPI and why did MindBridge choose it over Flask or Django?",
            "FastAPI is a modern Python web framework built on Starlette and Pydantic. Three reasons we chose it: (1) Async-first — handles concurrent requests without blocking, critical when 50 case managers hit the dashboard simultaneously. (2) Auto-documentation — generates Swagger UI automatically from type hints, so our API is always documented. (3) Pydantic validation — request/response data is validated automatically, preventing malformed patient data from reaching the database. Django was overkill (we don't need its ORM or admin). Flask lacks async support.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is a REST API and what are the HTTP methods used in MindBridge?",
            "REST (Representational State Transfer) is an architectural style where resources are accessed via URLs using standard HTTP methods. In MindBridge: GET /api/patients — retrieve patient list. POST /api/patients — create new patient. PUT /api/patients/{id} — update patient. DELETE /api/patients/{id} — soft delete (HIPAA: never hard delete). POST /api/analysis — run AI risk screening. GET /api/reports — list generated reports. Each endpoint is scoped to the authenticated user's role.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is Pydantic and how does MindBridge use it?",
            "Pydantic is a data validation library that uses Python type hints. In MindBridge, every API request and response has a Pydantic schema. When a case manager submits patient data, Pydantic automatically validates: medication_adherence must be 0.0-1.0 (float), appointments_missed must be >= 0 (int), crisis_calls_30days must be >= 0 (int). If validation fails, FastAPI returns a 422 error before the data touches the database. This prevents garbage data from corrupting risk assessments — a patient safety issue.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "SIMULATION: Walk me through a patient risk screening API request end-to-end.",
            "FULL FLOW: (1) Case manager clicks 'Screen Patient' in dashboard. (2) Next.js sends POST /api/analysis with patient_id in Bearer token header. (3) FastAPI middleware validates JWT — confirms user is authenticated. (4) RBAC check — confirms user has 'case_manager' or 'admin' role. (5) Analysis Service fetches patient from PostgreSQL. (6) Claude AI receives structured prompt with patient data. (7) AI returns risk_level, primary_factor, recommended_action. (8) Results saved to screenings table. (9) If HIGH risk — Notification Service sends email alert. (10) Audit Logger records the access (HIPAA). (11) FastAPI returns JSON response to Next.js. (12) Dashboard updates with color-coded risk badge.",
            "simulation"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is async/await in Python and why does MindBridge use it?",
            "Async/await allows code to pause while waiting for slow operations (database queries, API calls) without blocking other requests. Without async: if a Claude API call takes 3 seconds, the server is frozen for ALL users during that 3 seconds. With async: while waiting for Claude's response, FastAPI handles 50 other requests. In MindBridge: async def get_patients() — waits for PostgreSQL without blocking. async def analyze_patient() — waits for Claude API without blocking. This is why async is non-negotiable for a multi-user healthcare platform.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What are HTTP status codes and which ones does MindBridge return?",
            "Status codes tell the client what happened. MindBridge returns: 200 OK — successful GET/PUT. 201 Created — patient successfully created. 400 Bad Request — invalid data (failed Pydantic validation). 401 Unauthorized — missing or invalid JWT token. 403 Forbidden — authenticated but wrong role (case manager trying to access admin endpoint). 404 Not Found — patient doesn't exist or belongs to another clinic. 422 Unprocessable Entity — data format correct but values invalid. 500 Internal Server Error — unexpected failure (always logged to HIPAA audit trail).",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is middleware in FastAPI and what middleware does MindBridge use?",
            "Middleware runs on every request before it reaches your route handlers. MindBridge uses: (1) CORS middleware — allows the Next.js frontend (different domain) to call our API. (2) Rate limiting middleware — prevents abuse, limits each IP to 100 requests/minute. (3) Auth middleware — validates JWT tokens on every protected route. (4) Logging middleware — logs every request with user_id, endpoint, timestamp for HIPAA audit trail. Middleware is the security perimeter — it catches problems before they reach business logic.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "SIMULATION: A junior developer asks why we don't just store the API key in the code. What do you say?",
            "ANSWER: 'Three reasons this is a patient safety issue, not just bad practice. (1) GitHub is public — if you commit an API key, it's exposed to millions of people within minutes. Bots scan GitHub 24/7 for secrets. (2) Version history is permanent — even if you delete the file, the key lives in git history forever. git log shows everything. (3) For healthcare apps, exposed credentials mean exposed patient data — that's a HIPAA breach, not a bug. We use environment variables: os.environ.get(\"ANTHROPIC_API_KEY\"). In production, we use AWS Secrets Manager. The key never touches the codebase.'",
            "simulation"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is dependency injection in FastAPI and how does MindBridge use it?",
            "Dependency injection provides shared resources to route handlers automatically. In MindBridge: Depends(get_db) — injects a database session into every route that needs it, automatically closing the connection after the request. Depends(get_current_user) — validates the JWT and injects the authenticated user object. Depends(require_role('admin')) — ensures only admins can reach certain endpoints. Without dependency injection, every route would manually open DB connections and validate tokens — duplicated code that's easy to forget and causes security gaps.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is the difference between PUT and PATCH in REST APIs?",
            "PUT replaces the entire resource. PATCH updates only specific fields. In MindBridge: PUT /api/patients/{id} — sends the complete patient object, replaces everything. PATCH /api/patients/{id} — sends only changed fields (e.g., just medication_adherence). We use PATCH for partial updates because: (1) Safer — can't accidentally wipe fields you didn't intend to change. (2) More efficient — less data over the network. (3) Better audit trail — HIPAA audit log shows exactly which fields changed. Clinical note: a case manager updating medication adherence shouldn't have to resend the entire patient record.",
            "concept"
        ),
        (
            "FastAPI & REST APIs", 2,
            "INTERVIEW SIMULATION: 'Describe your API design process for MindBridge.'",
            "ANSWER FRAMEWORK: 'I started with the clinical workflow, not the technical spec. I interviewed (mentally) the end users — case managers — and mapped their daily tasks: screening patients, reviewing risk levels, generating reports. Each task became an API endpoint. Then I applied REST principles: resources are nouns (patients, screenings, reports), actions are HTTP methods (GET, POST, PUT). I used Pydantic schemas to enforce data contracts — medication_adherence must be 0-1, never null. Every endpoint has RBAC — case managers see only their patients. And every data access is logged for HIPAA. The API design came from the clinical workflow, not the other way around.'",
            "simulation"
        ),
        (
            "FastAPI & REST APIs", 2,
            "What is CORS and why does MindBridge need it configured?",
            "CORS (Cross-Origin Resource Sharing) is a browser security feature that blocks requests from different domains by default. MindBridge needs CORS because: Next.js frontend runs on app.mindbridge.com (port 3000 in dev). FastAPI backend runs on api.mindbridge.com (port 8000 in dev). Without CORS configuration, browsers block ALL frontend-to-backend calls. We configure: allow_origins=['https://app.mindbridge.com'], allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Authorization','Content-Type']. In production, NEVER use allow_origins=['*'] — that allows any website to call your patient data API.",
            "concept"
        ),
    ]

    # Add Week 1 remaining cards
    added_w1 = 0
    for topic, week, question, answer, card_type in week1_remaining:
        c.execute("SELECT id FROM flashcards WHERE question = ?", (question,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO flashcards (topic, week, question, ideal_answer) VALUES (?, ?, ?, ?)",
                (topic, week, question, answer),
            )
            added_w1 += 1

    # Add Week 2 cards
    added_w2 = 0
    for topic, week, question, answer, card_type in week2_cards:
        c.execute("SELECT id FROM flashcards WHERE question = ?", (question,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO flashcards (topic, week, question, ideal_answer) VALUES (?, ?, ?, ?)",
                (topic, week, question, answer),
            )
            added_w2 += 1

    # Unlock Week 2
    c.execute(
        "UPDATE curriculum_progress SET status = 'available' WHERE week = 2 AND status = 'locked'"
    )

    conn.commit()

    # Show summary
    c.execute("SELECT COUNT(*) FROM flashcards")
    total = c.fetchone()[0]

    conn.close()

    print("=" * 70)
    print("✅ Cards Added Successfully!")
    print("=" * 70)
    print(f"\n   Week 1 cards added: {added_w1} (now 12 total)")
    print(f"   Week 2 cards added: {added_w2} (FastAPI & REST APIs)")
    print(f"   Total cards in deck: {total}")
    print(f"\n   Week 2: 🔓 UNLOCKED")
    print(f"\n📚 Card Types Now Available:")
    print(f"   💡 Concept cards  - Core technical knowledge")
    print(f"   🎭 Simulation cards - Real-world scenarios")
    print(f"   🎤 Interview cards - Practice your answers")
    print(f"\n🎯 Daily Quiz: 10 cards (mix of review + new)")
    print("=" * 70)


if __name__ == "__main__":
    add_cards()
