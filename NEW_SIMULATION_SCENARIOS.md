# NEW SCENARIOS TO ADD TO SIMULATION LAB
# Add these to your simulation_lab.html scenarios object

---

## 6 NEW SCENARIOS (Docker + FastAPI from Day 8)

Copy these into the `scenarios = {` section of your simulation_lab.html:

```javascript
  // === NEW DAY 8 SCENARIOS ===
  
  debug500: {
    type: "simulation",
    title: "Debug 500 Error in Production",
    question: "Your FastAPI endpoint suddenly returns 500 Internal Server Error. Users are calling support. Walk me through debugging it step by step.",
    context: "This tests real-world debugging under pressure. Show methodical thinking, not panic.",
    ideal: `<strong>STEP 1 — Check the logs immediately:</strong><br>
tail -f logs/app.log or check CloudWatch/Railway logs. The 500 error will have a stack trace showing exactly where it failed.<br><br>
<strong>STEP 2 — Identify the error type:</strong><br>
DatabaseError = connection pool exhausted or DB down. Check: docker compose ps or Railway dashboard.<br>
ClientError (Anthropic) = API key invalid or rate limit hit. Check: Anthropic dashboard.<br>
ValidationError = data schema mismatch. Check: Pydantic model definitions.<br>
AttributeError = code trying to access None. Check: null checks before field access.<br><br>
<strong>STEP 3 — Common MindBridge 500 causes and fixes:</strong><br>
'Connection pool exhausted' → Increase pool_size in SQLAlchemy (default 5 is too low for production).<br>
'anthropic.APIError: Invalid API key' → Environment variable not set correctly in production.<br>
'NoneType has no attribute' → Database returned null, code didn't check. Fix: Add if patient is not None check.<br><br>
<strong>STEP 4 — Reproduce locally:</strong><br>
Copy the exact request from logs, replay in Postman/curl. Fix the bug and deploy.<br><br>
<strong>STEP 5 — Add monitoring:</strong><br>
After fixing, add logging around the failure point so next time you catch it earlier.<br><br>
<strong>Interview gold:</strong> "Read the logs first. The stack trace tells you exactly what failed. Most 500 errors are fixed in under 10 minutes if you read the error message carefully instead of guessing."`
  },

  slowapi: {
    type: "simulation",
    title: "API Performance - It's Too Slow",
    question: "A case manager reports the API is 'slow'. The dashboard takes 10 seconds to load. How do you diagnose and fix it?",
    context: "Performance debugging is a core skill. Show you know how to measure before optimizing.",
    ideal: `<strong>STEP 1 — Define 'slow':</strong><br>
Get specifics: Which endpoint? How slow (2 seconds? 30 seconds?)? Happens always or intermittently?<br><br>
<strong>STEP 2 — Check the obvious:</strong><br>
Is Claude API down? (Check status.anthropic.com)<br>
Is database connection pool exhausted? (Check logs for 'Timeout waiting for connection')<br>
Is the network slow? (Check CloudWatch/Railway metrics)<br><br>
<strong>STEP 3 — Add timing logs:</strong><br>
import time; start = time.time(); result = await db.query(...); print(f'Query took {time.time()-start}s')<br>
This shows which part is slow: database? Claude API? Data processing?<br><br>
<strong>STEP 4 — Common MindBridge performance issues:</strong><br>
<strong>N+1 queries</strong> — Loading 50 patients then fetching each patient's screenings individually. Fix: Use JOIN or eager loading.<br>
<strong>Missing database index</strong> — Querying WHERE clinic_id without an index scans entire table. Fix: CREATE INDEX idx_patients_clinic ON patients(clinic_id).<br>
<strong>Large response payloads</strong> — Returning 10MB of data when frontend only needs 50KB. Fix: Use Pydantic response model to include only necessary fields.<br>
<strong>Synchronous blocking</strong> — Claude API call blocks all other requests. Already fixed with async.<br><br>
<strong>STEP 5 — Verify the fix:</strong><br>
Before: Dashboard loads in 10 seconds.<br>
After: Dashboard loads in 0.5 seconds.<br>
Log the improvement. Update monitoring.<br><br>
<strong>Interview gold:</strong> "Performance issues are usually database queries. Add timing, find the slow query, add an index. 90% of the time that's the fix. The other 10% is usually oversized API responses."`
  },

  corserror: {
    type: "simulation",
    title: "CORS Error - Frontend Can't Reach Backend",
    question: "Your Next.js frontend suddenly can't reach the FastAPI backend. Browser console shows: 'CORS policy: No Access-Control-Allow-Origin header'. What do you do?",
    context: "CORS errors confuse many developers. Show you understand web security fundamentals.",
    ideal: `<strong>What CORS is:</strong><br>
CORS (Cross-Origin Resource Sharing) is a browser security feature that blocks requests between different domains by default.<br><br>
<strong>Why it's failing:</strong><br>
Frontend runs on app.mindbridge.com (or localhost:3000 in dev).<br>
Backend runs on api.mindbridge.com (or localhost:8000 in dev).<br>
Browser blocks the request because origins don't match.<br><br>
<strong>THE FIX — Add CORS middleware to FastAPI:</strong><br>
from fastapi.middleware.cors import CORSMiddleware<br>
app.add_middleware(CORSMiddleware, allow_origins=["https://app.mindbridge.com"], allow_credentials=True, allow_methods=["GET","POST","PUT","DELETE"], allow_headers=["Authorization","Content-Type"])<br><br>
<strong>Development config:</strong><br>
allow_origins=["http://localhost:3000"] — for local Next.js dev server<br><br>
<strong>CRITICAL — What NOT to do:</strong><br>
NEVER use allow_origins=["*"] in production for a healthcare app. That means ANY website can call your patient data API. For a HIPAA-compliant system, you must whitelist specific origins.<br><br>
<strong>How to test:</strong><br>
Open browser DevTools → Network tab → Try the API call → Response headers should show Access-Control-Allow-Origin: https://app.mindbridge.com<br><br>
<strong>Interview gold:</strong> "CORS is a browser security feature, not a server problem. The fix is always on the backend — add the CORS middleware with explicit origin whitelisting. Never use wildcards in healthcare applications."`
  },

  pooling: {
    type: "concept",
    title: "Connection Pooling Deep Dive",
    question: "You mentioned connection pooling in your resume. Explain what it is, why MindBridge needs it, and what happens when the pool is exhausted.",
    context: "This tests real production database knowledge, not just theory.",
    ideal: `<strong>What connection pooling is:</strong><br>
Connection pooling reuses database connections instead of opening a new one for every request. Think of it like a shared bike system — bikes sit ready to use, you don't build a new bike each time.<br><br>
<strong>Why it matters for MindBridge:</strong><br>
Opening a PostgreSQL connection takes 50-100ms. If 100 case managers hit the dashboard simultaneously:<br>
WITHOUT pooling: 100 × 100ms = 10 seconds of pure connection overhead. The last user waits 10 seconds just to START their query.<br>
WITH pooling: 10 persistent connections ready. Requests queue and reuse existing connections. Max wait ≈ query time, not connection time.<br><br>
<strong>MindBridge configuration:</strong><br>
engine = create_async_engine('postgresql://...', pool_size=10, max_overflow=20)<br>
This means: 10 persistent connections, can burst to 30 under heavy load.<br><br>
<strong>What happens when pool exhausted:</strong><br>
Error: 'QueuePool limit of size 10 overflow 20 reached, connection timed out'<br>
Users see: 500 Internal Server Error<br>
Real impact: Dashboard stops working during peak hours (morning when all case managers log in)<br><br>
<strong>How to fix:</strong><br>
Increase pool_size (but don't go crazy — PostgreSQL has connection limits too)<br>
Find connection leaks (endpoints not closing DB sessions)<br>
Add connection pooling metrics to monitoring<br><br>
<strong>Interview gold:</strong> "Connection pooling is why MindBridge can handle 50 concurrent users on a single backend instance. Without it, we'd need 10× the server capacity or users would experience random timeouts."`
  },

  testing: {
    type: "interview",
    title: "Your Testing Strategy",
    question: "Walk me through your testing strategy for MindBridge. How do you ensure the AI doesn't give dangerous medical advice?",
    context: "Healthcare AI requires rigorous testing. Show you understand both technical testing AND clinical safety.",
    ideal: `<strong>Three-layer testing strategy:</strong><br><br>
<strong>LAYER 1 — Unit Tests (Technical Safety):</strong><br>
Test each function in isolation using pytest.<br>
Example: test_patient_risk_calculation() verifies that medication_adherence=0.3 + appointments_missed=4 correctly flags as HIGH risk.<br>
Example: test_pydantic_validation() ensures medication_adherence=5.0 is rejected (must be 0.0-1.0).<br>
Coverage target: 90% of backend code.<br><br>
<strong>LAYER 2 — Integration Tests (System Safety):</strong><br>
Test complete workflows end-to-end.<br>
Example: POST /api/analysis with real patient data → verify Claude API is called → verify response saved to database → verify audit log entry created.<br>
Example: Test authentication — 401 if no token, 403 if wrong role.<br><br>
<strong>LAYER 3 — Clinical Guardrails (Patient Safety):</strong><br>
This is where my 10 years of clinical experience matters.<br>
<strong>Guardrail 1:</strong> AI can never automatically downgrade a patient from HIGH to MEDIUM risk. Only a licensed clinician can do that.<br>
<strong>Guardrail 2:</strong> If patient has crisis_calls_30days > 0, risk level is minimum MEDIUM regardless of other factors.<br>
<strong>Guardrail 3:</strong> AI suggestions are always labeled "AI-Generated - Requires Clinical Review" in the UI.<br>
<strong>Guardrail 4:</strong> All AI assessments log the exact prompt and response to audit_log for post-incident review.<br><br>
<strong>Real-world testing:</strong><br>
I'd also pilot with 5 case managers for 2 weeks before full rollout. Track: How often do they override the AI? What patterns emerge? Are false positives causing alert fatigue?<br><br>
<strong>Interview gold:</strong> "In healthcare AI, testing isn't just about code correctness. It's about clinical safety. The AI is a tool to help clinicians, not replace their judgment. That's why the guardrails prevent automated decisions on critical actions."`
  },

  bulkimport: {
    type: "interview",
    title: "Design Challenge - Bulk CSV Import",
    question: "A clinic wants to import 500 existing patients from a CSV file. How would you design this feature from scratch?",
    context: "This tests system design thinking, not just coding. Show you think about users, errors, performance, and safety.",
    ideal: `<strong>USER WORKFLOW FIRST:</strong><br>
Case manager uploads CSV with 500 patients → System validates → Imports → Returns summary: "450 imported, 50 errors with reasons"<br><br>
<strong>TECHNICAL DESIGN:</strong><br><br>
<strong>STEP 1 — Endpoint Design:</strong><br>
POST /patients/import accepts file upload (multipart/form-data)<br>
Returns 202 Accepted immediately with task_id (don't block — 500 patients is too slow for sync request)<br><br>
<strong>STEP 2 — Validation (Fail Fast):</strong><br>
Check: Is it a valid CSV? Required columns present (name, DOB, medication_adherence)?<br>
Return 400 Bad Request immediately if malformed — don't waste time processing garbage.<br><br>
<strong>STEP 3 — Background Processing (Celery Worker):</strong><br>
500 patients × 2 seconds each = 1000 seconds (16 minutes). Can't block a web request that long.<br>
Use Celery to process async. Frontend polls GET /imports/{task_id} for status.<br><br>
<strong>STEP 4 — Row-Level Validation:</strong><br>
For each row: Pydantic validates data types. Check for duplicates (same name + DOB already in DB). Log invalid rows separately — don't fail entire import for one bad row.<br><br>
<strong>STEP 5 — Database Transaction:</strong><br>
Wrap ALL inserts in a single transaction. If DB fails mid-import, rollback everything — no partial imports (150 patients in, 350 missing = data corruption).<br><br>
<strong>STEP 6 — HIPAA Audit:</strong><br>
Log: Who uploaded (user_id). When (timestamp). Which file (filename, hash). How many patients (count). Store the original CSV temporarily for post-incident review if needed.<br><br>
<strong>STEP 7 — Result Endpoint:</strong><br>
GET /imports/{task_id} returns:<br>
{status: "processing|completed|failed", imported: 450, errors: [{row: 23, reason: "Invalid medication_adherence: must be 0.0-1.0"}]}<br><br>
<strong>SECURITY CONSIDERATIONS:</strong><br>
File size limit (10MB max — prevent DOS)<br>
Virus scan the CSV<br>
RBAC — only admins can bulk import<br>
Rate limit — 1 import per hour per user<br><br>
<strong>Interview gold:</strong> "I'd prototype with synchronous processing for 50 patients first, then add Celery when we hit scale. Always validate MVP assumptions with real usage before building complex async systems. Over-engineering early kills velocity."`
  },
```

---

## HOW TO ADD THESE TO YOUR SIMULATION LAB:

1. Open simulation_lab.html in VS Code
2. Find the line: `const scenarios = {`
3. Add the 6 scenarios above BEFORE the closing `};`
4. Update the sidebar buttons (I'll show you the HTML for that too)

### SIDEBAR BUTTONS TO ADD:

Find the `<div class="sidebar-section">` for Simulations and add:

```html
<button class="scenario-btn" onclick="loadScenario('debug500')" id="btn-debug500">
  <span class="icon">🐛</span>
  <span class="info">
    <div class="name">Debug 500 Error</div>
    <div class="tag tag-sim">Simulation</div>
  </span>
</button>

<button class="scenario-btn" onclick="loadScenario('slowapi')" id="btn-slowapi">
  <span class="icon">🐌</span>
  <span class="info">
    <div class="name">API Performance Issue</div>
    <div class="tag tag-sim">Simulation</div>
  </span>
</button>

<button class="scenario-btn" onclick="loadScenario('corserror')" id="btn-corserror">
  <span class="icon">🚫</span>
  <span class="info">
    <div class="name">CORS Error</div>
    <div class="tag tag-sim">Simulation</div>
  </span>
</button>
```

Find the Concepts section and add:

```html
<button class="scenario-btn" onclick="loadScenario('pooling')" id="btn-pooling">
  <span class="icon">🔄</span>
  <span class="info">
    <div class="name">Connection Pooling</div>
    <div class="tag tag-con">Concept</div>
  </span>
</button>
```

Find the Interview section and add:

```html
<button class="scenario-btn" onclick="loadScenario('testing')" id="btn-testing">
  <span class="icon">🧪</span>
  <span class="info">
    <div class="name">Testing Strategy</div>
    <div class="tag tag-int">Interview</div>
  </span>
</button>

<button class="scenario-btn" onclick="loadScenario('bulkimport')" id="btn-bulkimport">
  <span class="icon">📤</span>
  <span class="info">
    <div class="name">Bulk CSV Import Design</div>
    <div class="tag tag-int">Interview</div>
  </span>
</button>
```

Update the stats bar total from 19 to 25 scenarios.
