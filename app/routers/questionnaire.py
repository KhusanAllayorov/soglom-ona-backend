import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.questionnaire import Questionnaire, Question
from app.schemas.questionnaire import QuestionnaireSchema, QuestionnaireCreate, QuestionSchema
from app.services.auth import get_current_user, require_doctor

router = APIRouter(prefix="/api/questionnaires", tags=["So'rovnomalar"])

@router.get("", response_model=List[QuestionnaireSchema])
def list_questionnaires(db: Session = Depends(get_db)):
    """Barcha faol so'rovnomalarni olish (EPDS, PHQ-9 va shifokor yaratgan testlar)."""
    items = db.query(Questionnaire).filter(Questionnaire.is_active == True).all()
    res = []
    for q in items:
        questions = [
            QuestionSchema(
                id=quest.id,
                order=quest.order,
                text=quest.text,
                is_safety_critical=quest.is_safety_critical,
                options=quest.options
            )
            for quest in q.questions
        ]
        res.append(QuestionnaireSchema(
            id=q.id,
            title=q.title,
            subtitle=q.subtitle,
            description=q.description,
            category=q.category,
            is_active=q.is_active,
            bands=q.bands,
            questions=questions
        ))
    return res

@router.get("/{q_id}", response_model=QuestionnaireSchema)
def get_questionnaire(q_id: str, db: Session = Depends(get_db)):
    q = db.query(Questionnaire).filter(Questionnaire.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="So'rovnoma topilmadi")

    questions = [
        QuestionSchema(
            id=quest.id,
            order=quest.order,
            text=quest.text,
            is_safety_critical=quest.is_safety_critical,
            options=quest.options
        )
        for quest in q.questions
    ]
    return QuestionnaireSchema(
        id=q.id,
        title=q.title,
        subtitle=q.subtitle,
        description=q.description,
        category=q.category,
        is_active=q.is_active,
        bands=q.bands,
        questions=questions
    )

@router.post("", response_model=QuestionnaireSchema)
def create_questionnaire(
    req: QuestionnaireCreate,
    db: Session = Depends(get_db),
    doctor_user: User = Depends(require_doctor)
):
    """Shifokor tomonidan yangi so'rovnoma yaratish."""
    existing = db.query(Questionnaire).filter(Questionnaire.id == req.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ushbu ID bilan so'rovnoma allaqachon mavjud")

    q = Questionnaire(
        id=req.id,
        title=req.title,
        subtitle=req.subtitle,
        description=req.description,
        category=req.category or "custom",
        created_by_doctor_id=doctor_user.doctor_profile.id if doctor_user.doctor_profile else None,
        is_active=True,
        bands=req.bands
    )
    db.add(q)
    db.flush()

    for i, quest in enumerate(req.questions):
        question = Question(
            id=str(uuid.uuid4()),
            questionnaire_id=q.id,
            order=quest.order if quest.order is not None else i,
            text=quest.text,
            is_safety_critical=quest.is_safety_critical,
            options=[opt.dict() for opt in quest.options]
        )
        db.add(question)

    db.commit()
    return get_questionnaire(q.id, db)

@router.put("/{q_id}", response_model=QuestionnaireSchema)
def update_questionnaire(
    q_id: str,
    req: QuestionnaireCreate,
    db: Session = Depends(get_db),
    doctor_user: User = Depends(require_doctor)
):
    """Shifokor tomonidan mavjud so'rovnoma va uning savollarini tahrirlash."""
    q = db.query(Questionnaire).filter(Questionnaire.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="So'rovnoma topilmadi")

    q.title = req.title
    q.subtitle = req.subtitle
    q.description = req.description
    if req.category:
        q.category = req.category
    if req.bands:
        q.bands = req.bands

    # Eski savollarni tozalab yangilarini kiritish (cascade delete-orphan)
    q.questions.clear()
    db.flush()
    for i, quest in enumerate(req.questions):
        opts = [opt.model_dump() if hasattr(opt, 'model_dump') else opt.dict() for opt in quest.options]
        question = Question(
            id=str(uuid.uuid4()),
            questionnaire_id=q.id,
            order=quest.order if quest.order is not None else i,
            text=quest.text,
            is_safety_critical=quest.is_safety_critical,
            options=opts
        )
        q.questions.append(question)

    db.commit()
    db.refresh(q)
    return get_questionnaire(q_id, db)

@router.delete("/{q_id}")
def delete_questionnaire(
    q_id: str,
    db: Session = Depends(get_db),
    doctor_user: User = Depends(require_doctor)
):
    """So'rovnomani o'chirish (yoki deaktivatsiya qilish)."""
    q = db.query(Questionnaire).filter(Questionnaire.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="So'rovnoma topilmadi")

    if q.submissions and len(q.submissions) > 0:
        q.is_active = False
    else:
        db.delete(q)
    db.commit()
    return {"message": "So'rovnoma muvaffaqiyatli o'chirildi"}
