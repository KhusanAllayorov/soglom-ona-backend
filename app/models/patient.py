import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base

class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctor_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    
    stage = Column(String(32), default="pregnant")  # "pregnant" | "postpartum"
    stage_date = Column(DateTime, nullable=True)     # Taxminiy tug'ruq sanasi yoki tug'ruq sanasi
    blood_group = Column(String(16), nullable=True)
    risk_category = Column(String(16), default="low")  # "low" | "medium" | "high"
    notes = Column(String(1024), nullable=True)

    user = relationship("User", back_populates="patient_profile")
    doctor = relationship("DoctorProfile", back_populates="patients")
    screenings = relationship("ScreeningSubmission", back_populates="patient", cascade="all, delete-orphan")
    danger_checks = relationship("DangerCheck", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("ClinicalAlert", back_populates="patient", cascade="all, delete-orphan")
