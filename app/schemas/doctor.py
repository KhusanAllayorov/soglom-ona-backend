from typing import Optional
from pydantic import BaseModel

class DoctorProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    clinic_name: Optional[str] = None
    phone: Optional[str] = None

class DoctorPublicItem(BaseModel):
    id: str
    full_name: str
    phone: str
    specialty: Optional[str] = None
    clinic_name: Optional[str] = None
