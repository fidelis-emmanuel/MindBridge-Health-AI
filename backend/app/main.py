from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv
from app.ai.clinical_scribe.router import router as scribe_router
from app.routers.agent_router import router as agent_router

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")

db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            ssl="require"
        )
        app.state.pool = db_pool
        print("[OK] Database pool created")
    except Exception as e:
        print(f"[WARN] Database connection error: {type(e).__name__}: {e}")
        print(f"[WARN] DATABASE_URL starts with: {DATABASE_URL[:30] if DATABASE_URL else 'EMPTY'}")
        db_pool = None
        app.state.pool = None
    yield
    if db_pool:
        await db_pool.close()

app = FastAPI(
    title="MindBridge Health AI",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://mind-bridge-health-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(scribe_router)
app.include_router(agent_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MindBridge Health AI",
        "version": "1.0.0",
        "database": "connected" if db_pool else "unavailable"
    }

@app.get("/api/patients")
async def get_patients():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                id,
                patient_name,
                risk_level,
                medication_adherence,
                appointments_missed,
                crisis_calls_30days,
                diagnosis
            FROM patients
            ORDER BY id ASC
        """)
    return {
        "success": True,
        "patients": [dict(row) for row in rows],
        "count": len(rows),
        "source": "FastAPI + Railway PostgreSQL"
    }

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: int):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM patients WHERE id = $1
        """, patient_id)
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"success": True, "patient": dict(row)}
