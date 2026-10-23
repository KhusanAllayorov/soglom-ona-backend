import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class ScreeningSubmission(Base):
    __tablename__ = "screening_submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    questionnaire_id = Column(String(64), ForeignKey("questionnaires.id", ondelete="CASCADE"), nullable=False)
    
    total_score = Column(Integer, nullable=False)
    severity_level = Column(String(32), nullable=False)  # "minimal", "mild", "moderate", "severe"
    is_urgent = Column(Boolean, default=False)          # Shoshilinch yordam kerakmi
    
    # Javoblar (indekslar yoki ballar): [0, 2, 1, 3...]
    answers = Column(JSON, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)

    patient = relationship("PatientProfile", back_populates="screenings")
    questionnaire = relationship("Questionnaire", back_populates="submissions")
