"""
Pydantic models for the Appointment Scheduling module.

Validators enforce:
- scheduled_at must be in the future
- Business hours: Mon–Fri, 07:00–20:00
- duration_minutes: 15–240
"""
from __future__ import annotations

from datetime import datetime, time as dt_time, timezone
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ── Enums ─────────────────────────────────────────────────────────────────────

class AppointmentType(str, Enum):
    individual  = "individual"
    group       = "group"
    telehealth  = "telehealth"
    intake      = "intake"
    crisis      = "crisis"


class AppointmentStatus(str, Enum):
    scheduled  = "scheduled"
    confirmed  = "confirmed"
    completed  = "completed"
    cancelled  = "cancelled"
    no_show    = "no_show"


# ── Helpers ───────────────────────────────────────────────────────────────────

_BUSINESS_START = dt_time(7, 0)   # 07:00
_BUSINESS_END   = dt_time(20, 0)  # 20:00


def _to_utc(dt: datetime) -> datetime:
    """Return tz-aware datetime (assume UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# ── Request models ────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    patient_id:       int
    clinician_id:     uuid.UUID
    appointment_type: AppointmentType = AppointmentType.individual
    scheduled_at:     datetime
    duration_minutes: int = Field(default=50, ge=15, le=240)
    notes:            Optional[str] = None
    location:         Optional[str] = None

    @field_validator("scheduled_at")
    @classmethod
    def validate_future_date(cls, v: datetime) -> datetime:
        v = _to_utc(v)
        if v <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be a future datetime")
        return v

    @model_validator(mode="after")
    def validate_business_hours(self) -> "AppointmentCreate":
        if self.scheduled_at is None:
            return self
        sa = _to_utc(self.scheduled_at)
        if sa.weekday() > 4:  # Saturday=5, Sunday=6
            raise ValueError("Appointments must fall on a weekday (Mon–Fri)")
        t = sa.time()
        if not (_BUSINESS_START <= t < _BUSINESS_END):
            raise ValueError("Appointments must start between 07:00 and 20:00")
        return self


class AppointmentUpdate(BaseModel):
    appointment_type: Optional[AppointmentType] = None
    scheduled_at:     Optional[datetime]         = None
    duration_minutes: Optional[int]              = Field(default=None, ge=15, le=240)
    notes:            Optional[str]              = None
    location:         Optional[str]              = None
    cancellation_reason: Optional[str]           = None

    @field_validator("scheduled_at")
    @classmethod
    def validate_future_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        v = _to_utc(v)
        if v <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be a future datetime")
        return v


class AppointmentStatusUpdate(BaseModel):
    status:              AppointmentStatus
    cancellation_reason: Optional[str] = None


# ── Response model ────────────────────────────────────────────────────────────

class AppointmentResponse(BaseModel):
    id:                  int
    patient_id:          int
    clinician_id:        uuid.UUID
    appointment_type:    AppointmentType
    status:              AppointmentStatus
    scheduled_at:        datetime
    ends_at:             datetime
    duration_minutes:    int
    notes:               Optional[str]
    location:            Optional[str]
    reminder_24h_sent:   bool
    reminder_1h_sent:    bool
    cancelled_at:        Optional[datetime]
    cancellation_reason: Optional[str]
    created_at:          datetime
    updated_at:          datetime

    model_config = ConfigDict(from_attributes=True)
