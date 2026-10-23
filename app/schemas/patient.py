from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.screening import ScreeningResponse
from app.schemas.danger_check import DangerCheckResponse

class PatientListItem(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: str
    stage: str
    stage_date: Optional[datetime]
    risk_category: str
    last_bp: Optional[str] = None
    latest_screening_score: Optional[int] = None
    latest_danger_level: Optional[str] = None
    has_active_alert: bool = False

    class Config:
        from_attributes = True

class PatientDetail(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: str
    stage: str
    stage_date: Optional[datetime]
    blood_group: Optional[str]
    risk_category: str
    notes: Optional[str]
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None

    recent_screenings: List[ScreeningResponse] = []
    recent_danger_checks: List[DangerCheckResponse] = []

    class Config:
        from_attributes = True

class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    stage: Optional[str] = None
    stage_date: Optional[datetime] = None
    blood_group: Optional[str] = None
    doctor_id: Optional[str] = None

class PatientUpdate(BaseModel):
    risk_category: Optional[str] = None
    notes: Optional[str] = None
    doctor_id: Optional[str] = None
