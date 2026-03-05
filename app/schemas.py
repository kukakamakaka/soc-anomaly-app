from pydantic import BaseModel
from typing import Optional

class EventBase(BaseModel):
    process_name: str
    command_line: str
    user: str

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    severity: str
    anomaly_score: float
    mitre_technique: Optional[str] = None # НОВОЕ ПОЛЕ

    class Config:
        from_attributes = True