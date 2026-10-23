from typing import Optional
from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    phone: str = Field(..., example="+998901234567")
    full_name: str = Field(..., example="Gulnoza Karimova")
    password: str = Field(..., min_length=4)
    role: str = Field("patient", description="'patient' yoki 'doctor'")
    
    # Agar doctor bo'lsa:
    specialty: Optional[str] = "Akusher-ginekolog"
    clinic_name: Optional[str] = None
    
    # Agar bemor bo'lsa:
    stage: Optional[str] = "pregnant"  # "pregnant" | "postpartum"
    stage_date: Optional[str] = None   # ISO format YYYY-MM-DD
    doctor_phone: Optional[str] = None # Biriktirilgan shifokor raqami

class UserLogin(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str
    profile_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    phone: str
    full_name: str
    role: str

    class Config:
        from_attributes = True
