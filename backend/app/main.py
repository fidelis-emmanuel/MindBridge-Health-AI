from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Annotated
from pydantic import BaseModel, Field, field_validator
import asyncpg
import os
from dotenv import load_dotenv
from app.ai.clinical_scribe.router import router as scribe_router
from app.routers.agent_router import router as agent_router

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")

VALID_RISK_LEVELS = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

class PatientCreate(BaseModel):
    patient_name: str
    diagnosis: str
    risk_level: str
    medication_adherence: float = 1.0
    appointments_missed: Annotated[int, Field(ge=0)] = 0
    crisis_calls_30days: Annotated[int, Field(ge=0)] = 0

    @field_validator("patient_name", "diagnosis")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field must not be blank")
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, v: str) -> str:
        if v not in VALID_RISK_LEVELS:
            raise ValueError(f"risk_level must be one of {VALID_RISK_LEVELS}")
        return v

    @field_validator("medication_adherence")
    @classmethod
    def validate_adherence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("medication_adherence must be between 0.0 and 1.0")
        return v

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
        async with db_pool.acquire() as conn:
            # Remove duplicate patient_name rows, keeping the lowest id
            deleted = await conn.execute("""
                DELETE FROM patients
                WHERE id NOT IN (
                    SELECT MIN(id) FROM patients GROUP BY patient_name
                )
            """)
            if deleted != "DELETE 0":
                print(f"[MIGRATION] Removed duplicate patients: {deleted}")
            # Add UNIQUE constraint if it doesn't already exist
            await conn.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'unique_patient_name'
                          AND conrelid = 'patients'::regclass
                    ) THEN
                        ALTER TABLE patients
                        ADD CONSTRAINT unique_patient_name UNIQUE (patient_name);
                        RAISE NOTICE 'unique_patient_name constraint added';
                    END IF;
                END
                $$;
            """)
            print("[MIGRATION] unique_patient_name constraint ensured")
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
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"success": True, "patient": dict(row)}

@app.post("/api/patients", status_code=201)
async def create_patient(data: PatientCreate):
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    async with db_pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
                INSERT INTO patients (
                    patient_name, diagnosis, risk_level,
                    medication_adherence, appointments_missed, crisis_calls_30days
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """,
                data.patient_name,
                data.diagnosis,
                data.risk_level,
                data.medication_adherence,
                data.appointments_missed,
                data.crisis_calls_30days,
            )
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(
                status_code=409,
                detail="Patient already exists"
            )
    return {"success": True, "patient": dict(row)}
