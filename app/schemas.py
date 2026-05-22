from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
    mitre_technique: Optional[str] = None
    created_at: Optional[datetime] = None
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

    class Config:
        from_attributes = True
