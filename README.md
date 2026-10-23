# Sog'lom Ona — Backend API

Homilador va tug'ruqdan keyingi ayollar hamda shifokorlar (akusher-ginekolog, psixolog) uchun mobil platforma backend xizmati.

## Texnologiyalar
- **Python 3.10+ / FastAPI**
- **SQLAlchemy 2.0 (ORM)**
- **PostgreSQL** (Railway bulutida) yoki **SQLite** (lokal ishlab chiqish uchun)
- **JWT (JSON Web Token)** autentifikatsiya
- **Bcrypt** xavfsiz parol heshlash

---

## 🚀 Lokal muhitda ishga tushirish

1. Virtual muhit yaratish va faollashtirish:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

2. Kerakli paketlarni o'rnatish:
```bash
pip install -r requirements.txt
```

3. Serverni ishga tushirish:
```bash
uvicorn app.main:app --reload --port 8000
```

4. Brauzerda ochish:
- API Bosh sahifa: `http://localhost:8000/`
- Interaktiv Swagger hujjatlari: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## ☁️ Railway ga Deploy qilish (Tezkor qo'llanma)

1. **GitHub ga yuklash:** `soglom_ona_backend` papkasini yangi Git repozitoriyaga joylang yoki umumiy repozitoriyangizga push qiling.
2. **Railway.app ga kirish:**
   - Yangi loyiha oching (`New Project`).
   - `Deploy from GitHub repo` ni tanlang.
   - `Add a Database` -> `PostgreSQL` ni bosing.
3. **Avtomatik sozlash:**
   - Railway avtomatik ravishda `Procfile` yoki `railway.json` ni taniydi va `Nixpacks` orqali Python muhitini o'rnatadi.
   - Railway yaratilgan PostgreSQL ning `DATABASE_URL` o'zgaruvchisini dasturga avtomatik biriktiradi.
4. **Tayyor!** Serveringiz `https://your-project.up.railway.app` manzilida ishlay boshlaydi va `/docs` orqali barcha API'larni tekshirishingiz mumkin bo'ladi.

---

## 📌 Asosiy API Endpointlar

### 🔐 Autentifikatsiya (`/api/auth`)
- `POST /api/auth/register` — Ro'yxatdan o'tish (bemor yoki shifokor sifatida)
- `POST /api/auth/login` — Tizimga kirish va JWT token olish
- `GET /api/auth/me` — Joriy foydalanuvchi ma'lumotlari

### 📋 So'rovnomalar (`/api/questionnaires`)
- `GET /api/questionnaires` — Barcha faol testlar ro'yxati (EPDS, PHQ-9 va shifokor yaratgan testlar)
- `GET /api/questionnaires/{id}` — Bitta test va uning barcha savollari
- `POST /api/questionnaires` — *(Faqat shifokor)* Yangi so'rovnoma yaratish
- `PUT /api/questionnaires/{id}` — *(Faqat shifokor)* Mavjud test savollarini tahrirlash
- `DELETE /api/questionnaires/{id}` — *(Faqat shifokor)* Testni o'chirish/deaktivatsiya qilish

### 👩‍🦰 Bemor API (`/api/patient`)
- `GET /api/patient/profile` — Shaxsiy profil va biriktirilgan shifokor ma'lumotlari
- `POST /api/patient/screenings` — EPDS yoki PHQ-9 testini topshirish (avtomatik ball & daraja hisoblanadi, og'ir holatda shifokorga alert yuboriladi)
- `GET /api/patient/screenings` — O'z test natijalari tarixi
- `POST /api/patient/danger-checks` — Kunlik 19 ta xavfli alomat va qon bosimini yozish (kritik holatda shifokorga ogohlantirish ketadi)
- `GET /api/patient/danger-checks` — Xavf tekshiruvlari tarixi

### 👨‍⚕️ Shifokor Kabineti (`/api/doctor`)
- `GET /api/doctor/dashboard` — Statistika (jami bemorlar, yuqori xavfdagilar, faol ogohlantirishlar)
- `GET /api/doctor/patients` — Barcha biriktirilgan bemorlar ro'yxati (filtrlar: `stage`, `risk`, `search`)
- `GET /api/doctor/patients/{id}` — Bemorning to'liq kartochkasi (bosim grafigi, testlar dinamikasi, ogohlantirishlar)
- `PUT /api/doctor/patients/{id}` — Bemorni xavf toifasini yangilash va shifokor eslatmalarini yozish
- `GET /api/doctor/alerts` — Barcha kritik xavf signallari
- `POST /api/doctor/alerts/{id}/resolve` — Xavf signalini "ko'rib chiqildi" deb yopish
