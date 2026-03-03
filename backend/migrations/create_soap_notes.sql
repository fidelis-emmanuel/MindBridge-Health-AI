CREATE TABLE IF NOT EXISTS soap_notes (
    id              SERIAL PRIMARY KEY,
    patient_id      INTEGER REFERENCES patients(id),
    encounter_date  TIMESTAMPTZ DEFAULT NOW(),
    provider_name   TEXT,
    raw_input       TEXT,
    subjective      TEXT,
    objective       TEXT,
    assessment      TEXT,
    plan            TEXT,
    icd10_codes     JSONB,
    medications     JSONB,
    risk_flags      JSONB,
    follow_up       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
