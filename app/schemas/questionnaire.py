from typing import List, Optional, Any
from pydantic import BaseModel

class QuestionOptionSchema(BaseModel):
    label: str
    points: int

class QuestionSchema(BaseModel):
    id: Optional[str] = None
    order: int
    text: str
    is_safety_critical: bool = False
    options: List[QuestionOptionSchema]

    class Config:
        from_attributes = True

class QuestionnaireCreate(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category: str = "screening"
    bands: Optional[List[dict]] = None
    questions: List[QuestionSchema]

class QuestionnaireSchema(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category: str
    is_active: bool
    bands: Optional[List[dict]] = None
    questions: List[QuestionSchema] = []

    class Config:
        from_attributes = True
