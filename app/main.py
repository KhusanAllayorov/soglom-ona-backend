from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.models import (
    user,
    doctor,
    patient,
    questionnaire,
    screening,
    danger_check,
    alert,
)
from app.services.seed_data import seed_default_questionnaires
from app.routers import auth, questionnaire as questionnaire_router, patient as patient_router, doctor as doctor_router

# Jadvallarni yaratish (Agar mavjud bo'lmasa)
Base.metadata.create_all(bind=engine)

# Standart testlarni kiritish
with SessionLocal() as db:
    seed_default_questionnaires(db)

app = FastAPI(
    title="Sog'lom Ona API",
    description="Homilador va tug'ruqdan keyingi ayollar hamda shifokorlar uchun monitoring tizimi API",
    version="1.0.0",
)

# CORS sozlamalari (Mobil ilova va barcha mijozlar uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlarni ulash
app.include_router(auth.router)
app.include_router(questionnaire_router.router)
app.include_router(patient_router.router)
app.include_router(doctor_router.router)

@app.get("/")
def root():
    return {
        "service": "Sog'lom Ona Backend API",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
