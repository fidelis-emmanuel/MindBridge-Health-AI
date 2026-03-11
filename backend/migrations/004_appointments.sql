-- ============================================================
-- MindBridge Health AI — Migration 004: Appointment Scheduling
-- Run once against Railway PostgreSQL via asyncpg
-- ============================================================

-- btree_gist enables the equality operator (=) on UUID inside
-- a GiST exclusion constraint for clinician-overlap detection.
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- ── Clinicians ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS clinicians (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR(255) NOT NULL,
    email          VARCHAR(255) UNIQUE,
    specialty      VARCHAR(100),
    license_number VARCHAR(100),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Seed 3 test clinicians so appointments have real FKs to test against
INSERT INTO clinicians (name, email, specialty, license_number) VALUES
    ('Dr. Sarah Chen',
     'sarah.chen@mindbridge.health',
     'Psychiatry',
     'PSY-2024-001'),
    ('Dr. Marcus Williams',
     'marcus.williams@mindbridge.health',
     'Clinical Psychology',
     'PSY-2024-002'),
    ('Dr. Aisha Patel',
     'aisha.patel@mindbridge.health',
     'Licensed Therapist',
     'LCSW-2024-003')
ON CONFLICT (email) DO NOTHING;

-- ── Enums (idempotent) ────────────────────────────────────────

DO $$ BEGIN
    CREATE TYPE appointment_type AS ENUM (
        'individual', 'group', 'telehealth', 'intake', 'crisis'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE appointment_status AS ENUM (
        'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ── Appointments ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS appointments (
    id                  SERIAL             PRIMARY KEY,
    patient_id          INTEGER            NOT NULL
                            REFERENCES patients(id) ON DELETE CASCADE,
    clinician_id        UUID               NOT NULL
                            REFERENCES clinicians(id),
    appointment_type    appointment_type   NOT NULL DEFAULT 'individual',
    status              appointment_status NOT NULL DEFAULT 'scheduled',
    scheduled_at        TIMESTAMPTZ        NOT NULL,
    duration_minutes    INTEGER            NOT NULL DEFAULT 50
                            CHECK (duration_minutes BETWEEN 15 AND 240),
    notes               TEXT,
    location            TEXT,
    reminder_24h_sent   BOOLEAN            NOT NULL DEFAULT FALSE,
    reminder_1h_sent    BOOLEAN            NOT NULL DEFAULT FALSE,
    -- ends_at is maintained by the trigger below; stored explicitly so
    -- the GiST index can reference two plain TIMESTAMPTZ columns (an
    -- expression index over timestamptz arithmetic is not IMMUTABLE in PG).
    ends_at             TIMESTAMPTZ        NOT NULL
                            DEFAULT NOW(),      -- overwritten immediately by trigger
    cancelled_at        TIMESTAMPTZ,
    cancellation_reason TEXT,
    created_at          TIMESTAMPTZ        NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ        NOT NULL DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_appointments_patient_id
    ON appointments (patient_id);

CREATE INDEX IF NOT EXISTS idx_appointments_clinician_id
    ON appointments (clinician_id);

CREATE INDEX IF NOT EXISTS idx_appointments_scheduled_at
    ON appointments (scheduled_at);

CREATE INDEX IF NOT EXISTS idx_appointments_status
    ON appointments (status);

-- GiST index on the stored ends_at column — both operands are plain
-- TIMESTAMPTZ columns, which PostgreSQL accepts in IMMUTABLE index contexts.
CREATE INDEX IF NOT EXISTS idx_appointments_time_slot
    ON appointments USING GIST (
        tstzrange(scheduled_at, ends_at, '[)')
    );

-- Partial btree index for active appointments (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_appointments_active
    ON appointments (clinician_id, scheduled_at)
    WHERE status NOT IN ('cancelled', 'no_show');

-- ── Exclusion constraint (DB-level conflict guard) ────────────
-- Requires btree_gist (added above).

ALTER TABLE appointments
    ADD CONSTRAINT appointments_no_clinician_overlap
    EXCLUDE USING GIST (
        clinician_id WITH =,
        tstzrange(scheduled_at, ends_at, '[)') WITH &&
    )
    WHERE (status NOT IN ('cancelled', 'no_show'));

-- ── Trigger: keep ends_at and updated_at in sync ─────────────

CREATE OR REPLACE FUNCTION trg_appointments_sync()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.ends_at    = NEW.scheduled_at
                     + (NEW.duration_minutes * INTERVAL '1 minute');
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS appointments_sync ON appointments;
CREATE TRIGGER appointments_sync
    BEFORE INSERT OR UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION trg_appointments_sync();
