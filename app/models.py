from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True, nullable=False)
    username      = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role          = Column(String, default="analyst", nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    # password reset
    reset_token   = Column(String, nullable=True)
    reset_expires = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    process_name = Column(String)
    command_line = Column(String)
    user = Column(String)
    severity = Column(String)
    anomaly_score = Column(Float)
    mitre_technique = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
