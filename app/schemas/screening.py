from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class ScreeningSubmit(BaseModel):
    questionnaire_id: str
    answers: List[int]  # Tanlangan variantlar indekslari

class ScreeningResponse(BaseModel):
    id: str
    patient_id: str
    questionnaire_id: str
    total_score: int
    severity_level: str
    is_urgent: bool
    answers: List[int]
    submitted_at: datetime

    class Config:
        from_attributes = True
