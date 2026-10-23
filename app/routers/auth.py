from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.doctor import DoctorProfile
from app.models.patient import PatientProfile
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autentifikatsiya"])

@router.post("/register", response_model=TokenResponse)
def register(req: UserRegister, db: Session = Depends(get_db)):
    clean_phone = req.phone.strip().replace(" ", "").replace("-", "")
    existing = db.query(User).filter(User.phone == clean_phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu telefon raqami allaqachon ro'yxatdan o'tgan"
        )

    user = User(
        phone=clean_phone,
        full_name=req.full_name.strip(),
        password_hash=hash_password(req.password),
        role=req.role.lower()
    )
    db.add(user)
    db.flush()

    profile_id = None
    if user.role == "doctor":
        doc = DoctorProfile(
            user_id=user.id,
            specialty=req.specialty or "Akusher-ginekolog",
            clinic_name=req.clinic_name
        )
        db.add(doc)
        db.flush()
        profile_id = doc.id
    else:
        # Bemor
        doctor_id = None
        if req.doctor_phone:
            doc_user = db.query(User).filter(User.phone == req.doctor_phone.strip()).first()
            if doc_user and doc_user.doctor_profile:
                doctor_id = doc_user.doctor_profile.id

        stage_date_dt = None
        if req.stage_date:
            try:
                stage_date_dt = datetime.fromisoformat(req.stage_date.replace("Z", ""))
            except Exception:
                pass

        patient = PatientProfile(
            user_id=user.id,
            doctor_id=doctor_id,
            stage=req.stage or "pregnant",
            stage_date=stage_date_dt,
            risk_category="low"
        )
        db.add(patient)
        db.flush()
        profile_id = patient.id

    db.commit()

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
        profile_id=profile_id
    )

@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin, db: Session = Depends(get_db)):
    clean_phone = req.phone.strip().replace(" ", "").replace("-", "")
    user = db.query(User).filter(User.phone == clean_phone).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon raqami yoki parol noto'g'ri"
        )

    profile_id = None
    if user.role == "doctor" and user.doctor_profile:
        profile_id = user.doctor_profile.id
    elif user.role == "patient" and user.patient_profile:
        profile_id = user.patient_profile.id

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
        profile_id=profile_id
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
