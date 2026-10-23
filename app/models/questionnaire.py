import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(String(64), primary_key=True)  # "epds", "phq9", yoki doctor_custom_uuid
    title = Column(String(256), nullable=False)
    subtitle = Column(String(512), nullable=True)
    description = Column(String(1024), nullable=True)
    category = Column(String(32), default="screening")  # "screening" | "monitoring" | "custom"
    created_by_doctor_id = Column(String(36), ForeignKey("doctor_profiles.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Shkala va darajalar qoidasi (JSON)
    # Masalan: [{"key": "minimal", "min": 0, "max": 9, "label": "Normal", "color": "#4CAF50"}, ...]
    bands = Column(JSON, nullable=True)

    doctor = relationship("DoctorProfile", back_populates="created_questionnaires")
    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan", order_by="Question.order")
    submissions = relationship("ScreeningSubmission", back_populates="questionnaire")

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    questionnaire_id = Column(String(64), ForeignKey("questionnaires.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, default=0)
    text = Column(String(1024), nullable=False)
    is_safety_critical = Column(Boolean, default=False)  # O'ziga zarar yetkazish / kritik savol

    # Variantlar (JSON list):
    # [{"label": "Hech qachon", "points": 0}, {"label": "Doimiy", "points": 3}]
    options = Column(JSON, nullable=False)

    questionnaire = relationship("Questionnaire", back_populates="questions")
