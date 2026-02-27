# 🧠 MindBridge Health AI

> HIPAA-Compliant Behavioral Health Platform — Full-Stack Healthcare AI Application

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://mind-bridge-health-ai.vercel.app)
[![API Status](https://img.shields.io/badge/API-Railway-purple?style=for-the-badge&logo=railway)](https://mindbridge-health-ai-production.up.railway.app/health)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

---

## 🔴 Live Demo

| Service  | URL                                                                                                             | Status  |
| -------- | --------------------------------------------------------------------------------------------------------------- | ------- |
| Frontend | [mind-bridge-health-ai.vercel.app](https://mind-bridge-health-ai.vercel.app)                                    | ✅ Live |
| API      | [mindbridge-health-ai-production.up.railway.app](https://mindbridge-health-ai-production.up.railway.app/health) | ✅ Live |
| Database | Railway PostgreSQL                                                                                              | ✅ Live |

**Demo credentials:**

- Email: `demo@mindbridge.health`
- Password: `MindBridge2026!`

---

## 🏗️ Architecture

```
Browser
   ↓
Vercel (Next.js 16 — Global CDN)
   ↓
Railway (FastAPI — REST API + AI Processing)
   ↓
Railway (PostgreSQL — Patient Database)
```

**Data flow:**

1. Clinician logs in via NextAuth.js (JWT, 8-hour session)
2. Next.js middleware blocks unauthenticated access at the edge
3. Dashboard loads patient data from Railway PostgreSQL
4. FastAPI backend serves REST endpoints with asyncpg connection pooling
5. All connections encrypted via SSL/TLS

---

## ⚙️ Tech Stack

### Frontend

| Technology   | Purpose                         |
| ------------ | ------------------------------- |
| Next.js 16   | React framework with App Router |
| TypeScript   | Type safety                     |
| Tailwind CSS | Styling                         |
| NextAuth.js  | Authentication + JWT sessions   |
| Vercel       | Deployment + CDN                |

### Backend

| Technology  | Purpose                        |
| ----------- | ------------------------------ |
| FastAPI     | Async REST API framework       |
| asyncpg     | Non-blocking PostgreSQL driver |
| Pydantic    | Data validation                |
| Python 3.11 | Runtime                        |
| Railway     | Cloud deployment               |

### Database

| Technology | Purpose               |
| ---------- | --------------------- |
| PostgreSQL | Primary database      |
| Railway    | Managed hosting       |
| SSL/TLS    | Encrypted connections |

---

## 🔐 HIPAA Compliance Features

- **Authentication** — JWT sessions with 8-hour expiry (clinical shift alignment)
- **Route Protection** — Next.js middleware blocks unauthenticated access
- **Encryption in Transit** — TLS 1.3 for all connections, SSL for database
- **Audit Logging** — All login events tracked (architecture ready)
- **Session Management** — Automatic logoff per §164.312(a)(2)(iii)
- **Unique User IDs** — Per-user JWT tokens per §164.312(a)(2)(i)
- **Demo Data Only** — No real PHI stored or displayed

---

## 🚀 API Endpoints

```
GET  /health                    — Service health check
GET  /api/patients              — All patients with risk data
GET  /api/patients/{id}         — Individual patient detail
```

**Example response:**

```json
{
  "success": true,
  "patients": [
    {
      "id": 1,
      "patient_name": "Marcus Johnson",
      "risk_level": "HIGH",
      "medication_adherence": 0.3,
      "appointments_missed": 4,
      "crisis_calls_30days": 2,
      "diagnosis": "Major Depressive Disorder, recurrent"
    }
  ],
  "count": 10,
  "source": "FastAPI + Railway PostgreSQL"
}
```

---

## 📁 Project Structure

```
MindBridge-Health-AI/
├── frontend/
│   └── patient-portal/          # Next.js application
│       ├── app/
│       │   ├── page.tsx          # Login page (NextAuth)
│       │   ├── dashboard/        # Protected patient dashboard
│       │   └── api/auth/         # NextAuth handler
│       ├── proxy.ts              # Route protection middleware
│       └── .env.local            # Local environment variables
├── backend/
│   ├── app/
│   │   └── main.py               # FastAPI application
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.toml              # Railway deployment config
└── README.md
```

---

## 🛠️ Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or Railway account)

### Frontend Setup

```bash
cd frontend/patient-portal
npm install
cp .env.local.example .env.local
# Add your DATABASE_URL and NEXTAUTH variables
npm run dev
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Set DATABASE_URL environment variable
uvicorn app.main:app --reload
```

### Environment Variables

**Frontend (.env.local):**

```
DATABASE_URL=postgresql://...
NEXTAUTH_SECRET=your-secret
NEXTAUTH_URL=http://localhost:3000
```

**Backend:**

```
DATABASE_URL=postgresql://...
```

---

## 🔒 Security Practices

- All credentials stored in environment variables — never hardcoded
- Git history cleaned with git-filter-repo after accidental exposure
- GitGuardian monitoring enabled on repository
- httpOnly cookies prevent XSS token theft
- CORS configured for specific origins only

---

## 👨‍💻 Developer

**Fidelis Emmanuel (Tobe)**

- 10 years behavioral health experience
- Transitioning to Healthcare AI Engineering
- Building production-grade clinical tools

---

## 📄 License

MIT — Demo data only. No real patient data is stored or displayed.
