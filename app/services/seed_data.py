from sqlalchemy.orm import Session
from app.models.questionnaire import Questionnaire, Question

def seed_default_questionnaires(db: Session):
    # 1. EPDS
    epds = db.query(Questionnaire).filter(Questionnaire.id == "epds").first()
    if not epds:
        epds = Questionnaire(
            id="epds",
            title="EPDS",
            subtitle="Tug'ruqdan keyingi depressiya (Edinburg shkalasi)",
            description="So'nggi 7 kun davomidagi ruhiy holat va his-tuyg'ularni baholash shkalasi.",
            category="screening",
            is_active=True,
            bands=[
                {"key": "minimal", "min": 0, "max": 9, "label": "Past ehtimol", "color": "#4CAF50"},
                {"key": "moderate", "min": 10, "max": 12, "label": "Chegaraviy holat", "color": "#FF9800"},
                {"key": "severe", "min": 13, "max": 30, "label": "Yuqori ehtimol", "color": "#E53935"},
            ]
        )
        db.add(epds)
        db.flush()

        epds_questions = [
            ("So'nggi 7 kun ichida men kulishga va narsalarning kulgili tomonini ko'rishga qodir edim:", [
                {"label": "Avvalgidek", "points": 0},
                {"label": "Hozir avvalgichalik emas", "points": 1},
                {"label": "Hozir aniq avvalgichalik emas", "points": 2},
                {"label": "Umuman yo'q", "points": 3},
            ], False),
            ("Men narsalarni zavq bilan kutdim:", [
                {"label": "Avvalgidek", "points": 0},
                {"label": "Avvalgidan biroz kamroq", "points": 1},
                {"label": "Avvalgidan sezilarli darajada kamroq", "points": 2},
                {"label": "Deyarli umuman", "points": 3},
            ], False),
            ("Ishlar yomon ketganda, men o'zimni keraksiz ayblab yurdim:", [
                {"label": "Ha, ko'p vaqt", "points": 3},
                {"label": "Ha, ba'zan", "points": 2},
                {"label": "Kamdan-kam", "points": 1},
                {"label": "Yo'q, hech qachon", "points": 0},
            ], False),
            ("Men hech qanday asosli sababsiz xavotirda yoki tashvishda bo'ldim:", [
                {"label": "Yo'q, umuman", "points": 0},
                {"label": "Deyarli hech qachon", "points": 1},
                {"label": "Ha, ba'zan", "points": 2},
                {"label": "Ha, juda tez-tez", "points": 3},
            ], False),
            ("Ishlar boshimdan oshib ketayotgandek tuyuldi:", [
                {"label": "Ha, ko'p vaqt men umuman uddalay olmadim", "points": 3},
                {"label": "Ha, ba'zan odatdagidek uddalay olmadim", "points": 2},
                {"label": "Yo'q, ko'pincha yaxshi uddaladim", "points": 1},
                {"label": "Yo'q, men har doimgidek yaxshi uddaladim", "points": 0},
            ], False),
            ("Men shu qadar baxtsiz edimki, uxlashga qiynaldim:", [
                {"label": "Ha, ko'p vaqt", "points": 3},
                {"label": "Ha, ba'zan", "points": 2},
                {"label": "Juda kamdan-kam", "points": 1},
                {"label": "Yo'q, umuman", "points": 0},
            ], False),
            ("Men o'zimni g'amgin yoki baxtsiz his qildim:", [
                {"label": "Ha, ko'p vaqt", "points": 3},
                {"label": "Ha, ancha tez-tez", "points": 2},
                {"label": "Faqat ba'zan", "points": 1},
                {"label": "Yo'q, umuman", "points": 0},
            ], False),
            ("Men shu qadar baxtsiz edimki, yig'lab yubordim:", [
                {"label": "Ha, ko'p vaqt", "points": 3},
                {"label": "Ha, ancha tez-tez", "points": 2},
                {"label": "Faqat vaqti-vaqti bilan", "points": 1},
                {"label": "Yo'q, hech qachon", "points": 0},
            ], False),
            ("Men qo'rqib yoki vahimaga tushdim:", [
                {"label": "Ha, juda tez-tez", "points": 3},
                {"label": "Ha, ba'zan", "points": 2},
                {"label": "Yo'q, juda kam", "points": 1},
                {"label": "Yo'q, umuman", "points": 0},
            ], False),
            ("O'zimga zarar yetkazish haqidagi fikr xayolimga keldi:", [
                {"label": "Ha, ancha tez-tez", "points": 3},
                {"label": "Ba'zan", "points": 2},
                {"label": "Deyarli hech qachon", "points": 1},
                {"label": "Hech qachon", "points": 0},
            ], True),
        ]

        for i, (text, opts, is_crit) in enumerate(epds_questions):
            q = Question(
                questionnaire_id="epds",
                order=i,
                text=text,
                options=opts,
                is_safety_critical=is_crit
            )
            db.add(q)

    # 2. PHQ-9
    phq9 = db.query(Questionnaire).filter(Questionnaire.id == "phq9").first()
    if not phq9:
        phq9 = Questionnaire(
            id="phq9",
            title="PHQ-9",
            subtitle="Depressiya so'rovnomasi",
            description="So'nggi 2 hafta davomidagi kayfiyat va depressiya belgilarini aniqlash.",
            category="screening",
            is_active=True,
            bands=[
                {"key": "minimal", "min": 0, "max": 4, "label": "Normal", "color": "#4CAF50"},
                {"key": "mild", "min": 5, "max": 9, "label": "Engil daraja", "color": "#8BC34A"},
                {"key": "moderate", "min": 10, "max": 14, "label": "O'rtacha daraja", "color": "#FF9800"},
                {"key": "modSevere", "min": 15, "max": 19, "label": "O'rtacha-og'ir daraja", "color": "#EF6C00"},
                {"key": "severe", "min": 20, "max": 27, "label": "Og'ir daraja", "color": "#E53935"},
            ]
        )
        db.add(phq9)
        db.flush()

        phq_labels = [
            {"label": "Hech qachon", "points": 0},
            {"label": "Kamdan-kam", "points": 1},
            {"label": "Ba'zan", "points": 2},
            {"label": "Doimiy", "points": 3},
        ]

        phq_questions = [
            ("Qandaydir vaqtda sizning kayfiyatingizni tushganini his qilganmisiz?", False),
            ("Oldin sizni qiziqtirgan narsalarga qiziqish yoki zavqning yo'qolganini his qildingizmi?", False),
            ("Sizning ish yoki kundalik faoliyatlaringizni bajarishda qiyinchilik tug'ildimi?", False),
            ("Uyquga borishda yoki uxlab qolishda qiyinchilik bo'ldimi?", False),
            ("Siz o'zingizni charchagan va to'liq energiya yo'qligini his qilganmisiz?", False),
            ("O'zingizni ishonchsiz, yaxshilanishga umidsiz his qilganmisiz?", False),
            ("O'zingizni bo'sh yoki jismoniy holatni yo'qotgan his qilganmisiz?", False),
            ("O'zingizni o'lim haqida yoki o'z joniga qasd qilishni o'ylaganmisiz?", True),
            ("Agar yuqorida keltirilgan simptomlardan bir nechtasini sezgan bo'lsangiz, ularni qanday darajada his qilganingizni baholang:", False),
        ]

        for i, (text, is_crit) in enumerate(phq_questions):
            q = Question(
                questionnaire_id="phq9",
                order=i,
                text=text,
                options=phq_labels,
                is_safety_critical=is_crit
            )
            db.add(q)

    db.commit()
