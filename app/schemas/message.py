from datetime import datetime
from pydantic import BaseModel

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: str
    patient_id: str
    sender_role: str
    sender_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
