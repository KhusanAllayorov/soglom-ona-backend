import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

class ClinicalAlert(Base):
    __tablename__ = "clinical_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # "high_bp" | "emergency_sign" | "self_harm" | "severe_depression"
    alert_type = Column(String(32), nullable=False)
    title = Column(String(256), nullable=False)
    message = Column(String(1024), nullable=False)
    
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    patient = relationship("PatientProfile", back_populates="alerts")
    doctor = relationship("DoctorProfile", back_populates="alerts")
