from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class DangerCheckSubmit(BaseModel):
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    yes_signs: List[str] = []
    pregnancy_week: Optional[int] = None

class DangerCheckResponse(BaseModel):
    id: str
    patient_id: str
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    yes_signs: List[str]
    level: str
    pregnancy_week: Optional[int]
    logged_at: datetime

    class Config:
        from_attributes = True

class ClinicalAlertResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    alert_type: str
    title: str
    message: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AlertResolveRequest(BaseModel):
    doctor_notes: Optional[str] = None
