from sqlalchemy.orm import Session
from app.models import Event
from app.schemas import EventCreate
from app.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()


def classify_severity(score: float) -> str:
    if score < -0.05:
        return "critical"
    elif score < 0.05:
        return "warning"
    return "normal"


def create_event(db: Session, event: EventCreate):
    history = db.query(Event).all()

    history_data = [
        {
            "process_name": e.process_name,
            "command_line": e.command_line,
            "user": e.user
        }
        for e in history
    ]

    detector.train(history_data)

    score = detector.score(event.model_dump())
    severity = classify_severity(score)

    db_event = Event(
        process_name=event.process_name,
        command_line=event.command_line,
        user=event.user,
        anomaly_score=score,
        severity=severity
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
