import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class DangerCheck(Base):
    __tablename__ = "danger_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    systolic_bp = Column(Integer, nullable=True)   # Masalan: 120
    diastolic_bp = Column(Integer, nullable=True)  # Masalan: 80
    
    # Belgilangan alomatlar id lari: ["high_bp", "headache", "seizure"]
    yes_signs = Column(JSON, default=list)
    
    # Natija darajasi: "stable" | "doctor_call" | "emergency"
    level = Column(String(32), nullable=False)
    pregnancy_week = Column(Integer, nullable=True)
    
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    patient = relationship("PatientProfile", back_populates="danger_checks")
