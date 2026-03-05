from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    process_name = Column(String)
    command_line = Column(String)
    user = Column(String)
    severity = Column(String)
    anomaly_score = Column(Float)
    mitre_technique = Column(String, nullable=True) # НОВАЯ КОЛОНКА