import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialty = Column(String(128), default="Akusher-ginekolog")  # Akusher-ginekolog / Psixolog / Oilaviy shifokor
    clinic_name = Column(String(256), nullable=True)
    license_number = Column(String(64), nullable=True)

    user = relationship("User", back_populates="doctor_profile")
    patients = relationship("PatientProfile", back_populates="doctor")
    created_questionnaires = relationship("Questionnaire", back_populates="doctor")
    alerts = relationship("ClinicalAlert", back_populates="doctor")
