from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.doctor import DoctorProfile
from app.models.patient import PatientProfile
from app.models.screening import ScreeningSubmission
from app.models.danger_check import DangerCheck
from app.models.alert import ClinicalAlert
from app.schemas.patient import PatientListItem, PatientDetail, PatientUpdate
from app.schemas.danger_check import ClinicalAlertResponse
from app.schemas.doctor import DoctorProfileUpdate
from app.services.auth import require_doctor

router = APIRouter(prefix="/api/doctor", tags=["Shifokor"])

@router.get("/dashboard")
def doctor_dashboard(
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    doc = current_user.doctor_profile
    if not doc:
        raise HTTPException(status_code=404, detail="Shifokor profili topilmadi")

    total_patients = db.query(PatientProfile).filter(PatientProfile.doctor_id == doc.id).count()
    high_risk_count = (
        db.query(PatientProfile)
        .filter(PatientProfile.doctor_id == doc.id, PatientProfile.risk_category == "high")
        .count()
    )
    active_alerts_count = (
        db.query(ClinicalAlert)
        .filter(ClinicalAlert.doctor_id == doc.id, ClinicalAlert.is_resolved == False)
        .count()
    )

    return {
        "doctor_name": current_user.full_name,
        "specialty": doc.specialty,
        "clinic_name": doc.clinic_name,
        "total_patients": total_patients,
        "high_risk_patients": high_risk_count,
        "active_alerts": active_alerts_count
    }

@router.get("/profile")
def get_doctor_profile(
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    doc = current_user.doctor_profile
    if not doc:
        raise HTTPException(status_code=404, detail="Shifokor profili topilmadi")

    total_patients = db.query(PatientProfile).filter(PatientProfile.doctor_id == doc.id).count()
    high_risk_count = (
        db.query(PatientProfile)
        .filter(PatientProfile.doctor_id == doc.id, PatientProfile.risk_category == "high")
        .count()
    )
    active_alerts_count = (
        db.query(ClinicalAlert)
        .filter(ClinicalAlert.doctor_id == doc.id, ClinicalAlert.is_resolved == False)
        .count()
    )

    return {
        "id": doc.id,
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "specialty": doc.specialty or "Akusher-ginekolog",
        "clinic_name": doc.clinic_name or "Tibbiyot muassasasi",
        "total_patients": total_patients,
        "high_risk_patients": high_risk_count,
        "active_alerts": active_alerts_count
    }

@router.put("/profile")
def update_doctor_profile(
    req: DoctorProfileUpdate,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    doc = current_user.doctor_profile
    if not doc:
        raise HTTPException(status_code=404, detail="Shifokor profili topilmadi")

    if req.full_name:
        current_user.full_name = req.full_name.strip()
    if req.phone:
        clean_phone = req.phone.strip().replace(" ", "").replace("-", "")
        # Check if phone is taken by another user
        existing = db.query(User).filter(User.phone == clean_phone, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ushbu telefon raqami boshqa foydalanuvchida mavjud")
        current_user.phone = clean_phone
    if req.specialty is not None:
        doc.specialty = req.specialty.strip()
    if req.clinic_name is not None:
        doc.clinic_name = req.clinic_name.strip()

    db.commit()
    return {
        "message": "Shifokor profili muvaffaqiyatli yangilandi",
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "specialty": doc.specialty,
        "clinic_name": doc.clinic_name
    }

@router.get("/patients", response_model=List[PatientListItem])
def list_patients(
    stage: Optional[str] = Query(None, description="'pregnant' yoki 'postpartum'"),
    risk: Optional[str] = Query(None, description="'low', 'medium' yoki 'high'"),
    search: Optional[str] = Query(None, description="Ism yoki telefon bo'yicha qidiruv"),
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    doc = current_user.doctor_profile
    if not doc:
        raise HTTPException(status_code=404, detail="Shifokor profili topilmadi")

    query = db.query(PatientProfile).join(User, PatientProfile.user_id == User.id)
    # Shifokorga biriktirilgan bemorlar (agar admin bo'lsa barchasini ko'rishi mumkin)
    if current_user.role != "admin":
        query = query.filter(PatientProfile.doctor_id == doc.id)

    if stage:
        query = query.filter(PatientProfile.stage == stage)
    if risk:
        query = query.filter(PatientProfile.risk_category == risk)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter((User.full_name.ilike(s)) | (User.phone.ilike(s)))

    patients = query.all()
    res = []

    for p in patients:
        # Oxirgi qon bosimi
        last_check = (
            db.query(DangerCheck)
            .filter(DangerCheck.patient_id == p.id)
            .order_by(DangerCheck.logged_at.desc())
            .first()
        )
        last_bp = f"{last_check.systolic_bp}/{last_check.diastolic_bp}" if last_check and last_check.systolic_bp else None

        # Oxirgi test bali
        last_screening = (
            db.query(ScreeningSubmission)
            .filter(ScreeningSubmission.patient_id == p.id)
            .order_by(ScreeningSubmission.submitted_at.desc())
            .first()
        )

        has_alert = (
            db.query(ClinicalAlert)
            .filter(ClinicalAlert.patient_id == p.id, ClinicalAlert.is_resolved == False)
            .count() > 0
        )

        res.append(PatientListItem(
            id=p.id,
            user_id=p.user.id,
            full_name=p.user.full_name,
            phone=p.user.phone,
            stage=p.stage,
            stage_date=p.stage_date,
            risk_category=p.risk_category,
            last_bp=last_bp,
            latest_screening_score=last_screening.total_score if last_screening else None,
            latest_danger_level=last_check.level if last_check else None,
            has_active_alert=has_alert
        ))

    return res

@router.get("/patients/{patient_id}", response_model=PatientDetail)
def get_patient_detail(
    patient_id: str,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    recent_screenings = (
        db.query(ScreeningSubmission)
        .filter(ScreeningSubmission.patient_id == patient.id)
        .order_by(ScreeningSubmission.submitted_at.desc())
        .limit(20)
        .all()
    )

    recent_danger_checks = (
        db.query(DangerCheck)
        .filter(DangerCheck.patient_id == patient.id)
        .order_by(DangerCheck.logged_at.desc())
        .limit(30)
        .all()
    )

    return PatientDetail(
        id=patient.id,
        user_id=patient.user.id,
        full_name=patient.user.full_name,
        phone=patient.user.phone,
        stage=patient.stage,
        stage_date=patient.stage_date,
        blood_group=patient.blood_group,
        risk_category=patient.risk_category,
        notes=patient.notes,
        doctor_name=current_user.full_name,
        doctor_phone=current_user.phone,
        recent_screenings=recent_screenings,
        recent_danger_checks=recent_danger_checks
    )

@router.put("/patients/{patient_id}")
def update_patient_info(
    patient_id: str,
    req: PatientUpdate,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi")

    if req.risk_category:
        patient.risk_category = req.risk_category
    if req.notes is not None:
        patient.notes = req.notes
    if req.doctor_id:
        patient.doctor_id = req.doctor_id

    db.commit()
    return {"message": "Bemor ma'lumotlari muvaffaqiyatli yangilandi"}

@router.get("/alerts", response_model=List[ClinicalAlertResponse])
def get_active_alerts(
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    doc = current_user.doctor_profile
    if not doc:
        raise HTTPException(status_code=404, detail="Shifokor profili topilmadi")

    alerts = (
        db.query(ClinicalAlert)
        .filter(ClinicalAlert.doctor_id == doc.id, ClinicalAlert.is_resolved == False)
        .order_by(ClinicalAlert.created_at.desc())
        .all()
    )

    res = []
    for a in alerts:
        p_name = a.patient.user.full_name if a.patient and a.patient.user else None
        p_phone = a.patient.user.phone if a.patient and a.patient.user else None
        res.append(ClinicalAlertResponse(
            id=a.id,
            patient_id=a.patient_id,
            patient_name=p_name,
            patient_phone=p_phone,
            alert_type=a.alert_type,
            title=a.title,
            message=a.message,
            is_resolved=a.is_resolved,
            created_at=a.created_at
        ))
    return res

@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    alert = db.query(ClinicalAlert).filter(ClinicalAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Ogohlantirish topilmadi")

    alert.is_resolved = True
    db.commit()
    return {"message": "Ogohlantirish ko'rib chiqilgan deb belgilandi"}
