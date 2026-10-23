from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.doctor import DoctorProfile
from app.models.questionnaire import Questionnaire
from app.models.screening import ScreeningSubmission
from app.models.danger_check import DangerCheck
from app.models.alert import ClinicalAlert
from app.schemas.screening import ScreeningSubmit, ScreeningResponse
from app.schemas.danger_check import DangerCheckSubmit, DangerCheckResponse
from app.schemas.patient import PatientDetail, PatientProfileUpdate
from app.services.auth import require_patient

router = APIRouter(prefix="/api/patient", tags=["Bemor"])

@router.get("/profile", response_model=PatientDetail)
def get_patient_profile(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    profile = current_user.patient_profile
    if not profile:
        raise HTTPException(status_code=404, detail="Bemor profili topilmadi")

    doctor_name = None
    doctor_phone = None
    if profile.doctor and profile.doctor.user:
        doctor_name = profile.doctor.user.full_name
        doctor_phone = profile.doctor.user.phone

    recent_screenings = (
        db.query(ScreeningSubmission)
        .filter(ScreeningSubmission.patient_id == profile.id)
        .order_by(ScreeningSubmission.submitted_at.desc())
        .limit(10)
        .all()
    )

    recent_danger_checks = (
        db.query(DangerCheck)
        .filter(DangerCheck.patient_id == profile.id)
        .order_by(DangerCheck.logged_at.desc())
        .limit(14)
        .all()
    )

    return PatientDetail(
        id=profile.id,
        user_id=current_user.id,
        full_name=current_user.full_name,
        phone=current_user.phone,
        stage=profile.stage,
        stage_date=profile.stage_date,
        blood_group=profile.blood_group,
        risk_category=profile.risk_category,
        notes=profile.notes,
        doctor_id=profile.doctor_id,
        doctor_name=doctor_name,
        doctor_phone=doctor_phone,
        recent_screenings=recent_screenings,
        recent_danger_checks=recent_danger_checks
    )

@router.put("/profile", response_model=PatientDetail)
def update_patient_profile(
    req: PatientProfileUpdate,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    profile = current_user.patient_profile
    if not profile:
        raise HTTPException(status_code=404, detail="Bemor profili topilmadi")

    if req.full_name is not None and req.full_name.strip():
        current_user.full_name = req.full_name.strip()
    if req.phone is not None and req.phone.strip():
        clean_phone = req.phone.strip().replace(" ", "").replace("-", "")
        existing = db.query(User).filter(User.phone == clean_phone, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ushbu telefon raqami boshqa foydalanuvchida mavjud")
        current_user.phone = clean_phone
    if req.stage is not None and req.stage in ["pregnant", "postpartum"]:
        profile.stage = req.stage
    if req.stage_date is not None:
        profile.stage_date = req.stage_date
    if req.blood_group is not None:
        profile.blood_group = req.blood_group.strip()
    if req.doctor_id is not None:
        if req.doctor_id:
            doc = db.query(DoctorProfile).filter(DoctorProfile.id == req.doctor_id).first()
            if not doc:
                raise HTTPException(status_code=404, detail="Tanlangan shifokor topilmadi")
            profile.doctor_id = req.doctor_id
        else:
            profile.doctor_id = None

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)

    doctor_name = None
    doctor_phone = None
    if profile.doctor and profile.doctor.user:
        doctor_name = profile.doctor.user.full_name
        doctor_phone = profile.doctor.user.phone

    return PatientDetail(
        id=profile.id,
        user_id=current_user.id,
        full_name=current_user.full_name,
        phone=current_user.phone,
        stage=profile.stage,
        stage_date=profile.stage_date,
        blood_group=profile.blood_group,
        risk_category=profile.risk_category,
        notes=profile.notes,
        doctor_id=profile.doctor_id,
        doctor_name=doctor_name,
        doctor_phone=doctor_phone,
        recent_screenings=[],
        recent_danger_checks=[]
    )

@router.post("/screenings", response_model=ScreeningResponse)
def submit_screening(
    req: ScreeningSubmit,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    profile = current_user.patient_profile
    if not profile:
        raise HTTPException(status_code=404, detail="Bemor profili topilmadi")

    q = db.query(Questionnaire).filter(Questionnaire.id == req.questionnaire_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="So'rovnoma topilmadi")

    # Ballni hisoblash
    total_score = 0
    is_urgent = False
    questions = q.questions

    for i, ans_idx in enumerate(req.answers):
        if i < len(questions):
            opts = questions[i].options
            if 0 <= ans_idx < len(opts):
                pts = opts[ans_idx].get("points", 0)
                total_score += pts
                # Agar o'ziga zarar yetkazish savoli bo'lsa va ball > 0 bo'lsa:
                if questions[i].is_safety_critical and pts > 0:
                    is_urgent = True

    # Darajani aniqlash (bands bo'yicha)
    severity_level = "minimal"
    if q.bands:
        for b in q.bands:
            if b.get("min", 0) <= total_score <= b.get("max", 100):
                severity_level = b.get("key", "minimal")
                break

    submission = ScreeningSubmission(
        patient_id=profile.id,
        questionnaire_id=q.id,
        total_score=total_score,
        severity_level=severity_level,
        is_urgent=is_urgent,
        answers=req.answers,
        submitted_at=datetime.utcnow()
    )
    db.add(submission)

    # Agar shoshilinch yordam (o'ziga zarar fikri) yoki og'ir daraja bo'lsa -> shifokorga alert!
    if is_urgent or severity_level in ["severe", "modSevere"]:
        alert = ClinicalAlert(
            patient_id=profile.id,
            doctor_id=profile.doctor_id,
            alert_type="self_harm" if is_urgent else "high_depression",
            title=f"Kritik ruhiy holat: {current_user.full_name}",
            message=(
                f"{q.title} testi bo'yicha {total_score} ball qayd etildi. "
                f"Daraja: {severity_level}. "
                + ("DIQQAT: O'ziga zarar yetkazish xavfi mavjud!" if is_urgent else "")
            )
        )
        db.add(alert)
        profile.risk_category = "high"

    db.commit()
    db.refresh(submission)
    return submission

@router.get("/screenings", response_model=List[ScreeningResponse])
def get_my_screenings(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    profile = current_user.patient_profile
    return (
        db.query(ScreeningSubmission)
        .filter(ScreeningSubmission.patient_id == profile.id)
        .order_by(ScreeningSubmission.submitted_at.desc())
        .all()
    )

@router.post("/danger-checks", response_model=DangerCheckResponse)
def submit_danger_check(
    req: DangerCheckSubmit,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    profile = current_user.patient_profile
    if not profile:
        raise HTTPException(status_code=404, detail="Bemor profili topilmadi")

    yes_set = set(req.yes_signs)

    # Qon bosimi tekshiruvi: 140/90 va undan yuqori bo'lsa 'high_bp' avtomatik qo'shiladi
    has_high_bp = False
    if req.systolic_bp and req.diastolic_bp:
        if req.systolic_bp >= 140 or req.diastolic_bp >= 90:
            yes_set.add("high_bp")
            has_high_bp = True

    # Darajani aniqlash:
    # Kritik alomatlar: tutqanoq (seizure), kuchli qon ketishi (heavy_bleeding), homila suvi ketishi (fluid_rupture)
    critical_signs = {"seizure", "heavy_bleeding", "fluid_rupture"}
    has_critical = bool(yes_set.intersection(critical_signs))

    if has_critical:
        level = "emergency"
    elif len(yes_set) > 0:
        level = "doctor_call"
    else:
        level = "stable"

    check = DangerCheck(
        patient_id=profile.id,
        systolic_bp=req.systolic_bp,
        diastolic_bp=req.diastolic_bp,
        yes_signs=list(yes_set),
        level=level,
        pregnancy_week=req.pregnancy_week,
        logged_at=datetime.utcnow()
    )
    db.add(check)

    # Agar tez yordam darajasi yoki yuqori qon bosimi bo'lsa -> shifokorga alert!
    if level == "emergency" or has_high_bp:
        alert_title = "Kritik xavf signali!" if level == "emergency" else "Qon bosimi ko'tarilgan!"
        alert_msg = (
            f"Bemor: {current_user.full_name}. "
            f"Bosim: {req.systolic_bp}/{req.diastolic_bp} mm sim. ust. "
            f"Alomatlar: {', '.join(yes_set)}"
        )
        alert = ClinicalAlert(
            patient_id=profile.id,
            doctor_id=profile.doctor_id,
            alert_type="emergency_sign" if level == "emergency" else "high_bp",
            title=alert_title,
            message=alert_msg
        )
        db.add(alert)
        profile.risk_category = "high"

    db.commit()
    db.refresh(check)
    return check

@router.get("/danger-checks", response_model=List[DangerCheckResponse])
def get_my_danger_checks(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    profile = current_user.patient_profile
    return (
        db.query(DangerCheck)
        .filter(DangerCheck.patient_id == profile.id)
        .order_by(DangerCheck.logged_at.desc())
        .all()
    )
