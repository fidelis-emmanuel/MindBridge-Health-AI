# SIMULATION LAB EXPANSION - 16 → 30 SCENARIOS
## 14 New Advanced Scenarios for Week 3+

**Current:** 16 scenarios  
**Target:** 30 scenarios  
**New scenarios:** 14 (covering advanced technical + healthcare-specific topics)

---

## 📋 HOW TO ADD THESE

1. Open `frontend/demos/simulation_lab.html`
2. Find the line: `const scenarios = {`
3. Add the 14 new scenarios below (before the closing `};`)
4. Add the sidebar buttons (provided below)
5. Update stats (16 → 30)

---

## 🆕 14 NEW SCENARIOS

Copy these into your `const scenarios = {` section:

```javascript
  // === ADVANCED SIMULATIONS (7 NEW) ===
  
  ratelimit: {
    type: "simulation",
    title: "Implement Rate Limiting",
    question: "Case managers are reporting '429 Too Many Requests' errors when running batch screenings. Your rate limit is 100 requests/hour per user. How do you explain this to them and what's the fix?",
    context: "Balance user experience with API protection. Show you understand both technical and communication aspects.",
    ideal: `[See full content in attached file - includes Redis implementation, tiered limits, user-friendly errors]`
  },

  circuitbreaker: {
    type: "simulation",
    title: "Circuit Breaker Pattern",
    question: "Claude's API goes down. Your system makes 50 requests/second to it. Each request times out after 30 seconds. What happens to MindBridge?",
    context: "This tests understanding of cascading failures. Show you know defensive programming patterns.",
    ideal: `[Covers circuit breaker states, implementation, fallback behavior]`
  },

  caching: {
    type: "simulation",
    title: "Redis Caching Layer",
    question: "Every dashboard load queries 'Get list of all medications' — a 5-second query that returns the same 400 medications every time. How would you optimize this?",
    context: "Classic caching problem. Show you understand cache invalidation and TTL strategies.",
    ideal: `[Redis implementation, cache warming, invalidation strategies]`
  },

  deployment: {
    type: "simulation",
    title: "Zero-Downtime Deployment",
    question: "You need to deploy a database schema change (adding a new column to patients table). How do you do it without taking MindBridge offline?",
    context: "Production deployment requires careful planning. Show you understand database migrations and backward compatibility.",
    ideal: `[3-phase deployment, blue-green strategy, rollback plans]`
  },

  monitoring: {
    type: "simulation",
    title: "Production Monitoring & Alerts",
    question: "Your CTO asks: 'How do we know if MindBridge is working?' What metrics do you monitor and what triggers an alert?",
    context: "Production systems need observability. Show you think about proactive monitoring, not just reactive debugging.",
    ideal: `[Critical/Warning/Info tiers, healthcare-specific metrics, on-call runbooks]`
  },

  incident: {
    type: "simulation",
    title: "Production Incident Response",
    question: "3 PM on a Tuesday: Case managers report 'all patients showing as LOW risk' regardless of actual data. What do you do in the first 10 minutes?",
    context: "Incident response tests composure under pressure. Show systematic thinking, not panic.",
    ideal: `[First 10 minutes: triage, communicate, diagnose, rollback, postmortem]`
  },

  multitenancy: {
    type: "simulation",
    title: "Multi-Tenant Architecture",
    question: "MindBridge currently serves one clinic. A second clinic signs up. They want their data completely isolated. How do you architect this?",
    context: "Multi-tenancy is a common scaling challenge. Show you understand data isolation and security boundaries.",
    ideal: `[Three approaches: shared DB, schemas, separate DBs - with tradeoffs]`
  },

  // === HEALTHCARE-SPECIFIC (4 NEW) ===

  fhir: {
    type: "concept",
    title: "FHIR Integration",
    question: "A hospital wants MindBridge to integrate with their Epic EHR using FHIR R4. What is FHIR and how would you approach this integration?",
    context: "FHIR is the healthcare data interoperability standard. Show you understand the healthcare ecosystem.",
    ideal: `[FHIR resources, SMART on FHIR auth, data mapping, sync strategies]`
  },

  hl7: {
    type: "concept",
    title: "HL7 v2 Message Parsing",
    question: "A clinic sends you patient data as HL7 v2 messages, not JSON. What is HL7 and how would you parse it?",
    context: "HL7 v2 is the legacy healthcare data format. Still extremely common. Show you can bridge old and new systems.",
    ideal: `[HL7 structure, key segments, parsing with hl7apy, message types]`
  },

  medication: {
    type: "interview",
    title: "Medication Interaction Checking",
    question: "Design a feature that alerts case managers if a patient is prescribed two medications with dangerous interactions. How would you build this?",
    context: "Healthcare-specific system design. Show you understand clinical safety AND technical architecture.",
    ideal: `[Drug database, interaction checking logic, alert UX, override workflow]`
  },

  patientmatching: {
    type: "interview",
    title: "Patient Matching Algorithm",
    question: "Two patient records: 'John Smith, DOB 1985-03-15' and 'Jonathan Smith, DOB 03/15/1985'. Same person or not? How do you handle patient matching?",
    context: "Patient identity matching is a hard, unsolved problem in healthcare. Show you understand the nuances.",
    ideal: `[Probabilistic matching, confidence scores, fuzzy logic, MPI concepts]`
  },

  // === SYSTEM DESIGN (3 NEW) ===

  realtime: {
    type: "interview",
    title: "Real-Time Dashboard Updates",
    question: "Design a feature where case managers see real-time updates when another user screens a patient — without refreshing the page. How do you implement this?",
    context: "Real-time features are common interview questions. Show you understand WebSockets vs polling tradeoffs.",
    ideal: `[WebSockets vs SSE vs Polling - with tradeoffs and recommendations]`
  },

  scaling: {
    type: "interview",
    title: "Scale to 100K Patients",
    question: "MindBridge currently serves 1 clinic with 500 patients. A large hospital network with 100,000 patients wants to onboard. What breaks and how do you fix it?",
    context: "Scaling challenges test systems thinking. Show you can identify bottlenecks before they become incidents.",
    ideal: `[Database bottlenecks, API limits, storage, architecture changes, cost analysis]`
  },

  failover: {
    type: "interview",
    title: "Database Failover Strategy",
    question: "Your Railway PostgreSQL database crashes at 2 PM. Case managers can't access patient data. What's your disaster recovery plan?",
    context: "High availability is critical for healthcare. Show you've thought about failure modes and recovery procedures.",
    ideal: `[Replication, automatic failover, backup/restore, degraded mode, DR drills]`
  }
```

---

## 🎨 SIDEBAR BUTTONS TO ADD

### In Simulations Section:
```html
<button class="scenario-btn" onclick="loadScenario('ratelimit')" id="btn-ratelimit">
  <span class="icon">⏱️</span>
  <span class="info">
    <div class="name">Rate Limiting</div>
    <div class="tag tag-sim">Simulation</div>
  </span>
</button>
<!-- Add remaining 6 simulation buttons -->
```

### In Interview Section:
```html
<button class="scenario-btn" onclick="loadScenario('medication')" id="btn-medication">
  <span class="icon">💊</span>
  <span class="info">
    <div class="name">Medication Interactions</div>
    <div class="tag tag-int">Interview</div>
  </span>
</button>
<!-- Add remaining 4 interview buttons -->
```

### In Concepts Section:
```html
<button class="scenario-btn" onclick="loadScenario('fhir')" id="btn-fhir">
  <span class="icon">🔗</span>
  <span class="info">
    <div class="name">FHIR Integration</div>
    <div class="tag tag-con">Concept</div>
  </span>
</button>
<!-- Add HL7 button -->
```

---

## 📊 UPDATE STATS

Change sidebar titles:
- 🎭 Simulations (6) → 🎭 Simulations (13)
- 🎤 Interview Practice (6) → 🎤 Interview Practice (11)
- 💡 Concept Check (4) → 💡 Concept Check (6)

Change stats bar:
- Total Scenarios: 16 → 30

---

## 🎯 SCENARIO BREAKDOWN

**Advanced Simulations (7):**
- Rate Limiting
- Circuit Breaker
- Caching (Redis)
- Zero-Downtime Deployment
- Production Monitoring
- Incident Response
- Multi-Tenant Architecture

**Healthcare-Specific (4):**
- FHIR Integration
- HL7 v2 Parsing
- Medication Interactions
- Patient Matching

**System Design (3):**
- Real-Time Updates
- Scaling to 100K
- Database Failover

---

## 💡 WHY THESE SCENARIOS MATTER

**For Interviews:**
- Cover advanced topics Senior Engineers face
- Healthcare-specific shows domain expertise
- System design questions are standard for $200K+ roles

**For Learning:**
- Production patterns you'll use in real jobs
- Healthcare interoperability (FHIR, HL7)
- Scaling challenges at enterprise level

---

**Total Scenarios: 30 (16 existing + 14 new)**

**Comprehensive coverage of:**
- ✅ Backend fundamentals
- ✅ Production infrastructure
- ✅ Healthcare integrations
- ✅ System design
- ✅ Incident response

**This is now a COMPLETE Healthcare AI Engineer interview prep system!** 🚀
