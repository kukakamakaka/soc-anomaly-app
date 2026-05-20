from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.ai_engine import ai_analyst
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas
from app.anomaly_detector import AnomalyDetector
from mitre_mapper import MitreMapper
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = "soc_diploma_secret_2026"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key. Access Denied.")
    return api_key

# Создаем таблицы в PostgreSQL (в Докере)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SOC Anomaly Detection")

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        train_model_on_existing_data(db)
    finally:
        db.close()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники для локальной разработки
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем компоненты
detector = AnomalyDetector()
mitre_mapper = MitreMapper()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def train_model_on_existing_data(db: Session):
    all_events = db.query(models.Event).all()
    if len(all_events) >= 5:
        events_list = [
            {"process_name": e.process_name, "command_line": e.command_line, "user": e.user}
            for e in all_events
        ]
        detector.train(events_list)

@app.post("/train")
def trigger_training(api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    train_model_on_existing_data(db)
    return {"status": "success", "message": "Модель IsolationForest успешно переобучена"}

@app.post("/ingest", response_model=schemas.EventOut)
def ingest_event(event: schemas.EventCreate, api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    # 1. ML Scoring
    score = detector.score(event.dict())

    # 2. MITRE Mapping
    techniques = mitre_mapper.get_attack_info(event.command_line)
    mitre_text = mitre_mapper.format_techniques(techniques) if techniques else None

    # 3. Hybrid Severity Logic
    severity = "normal"
    if score >= 0.5: severity = "low"
    if score >= 0.75 or techniques: severity = "high"
    if score >= 0.9 and techniques: severity = "critical"

    db_event = models.Event(
        **event.dict(),
        anomaly_score=score,
        severity=severity,
        mitre_technique=mitre_text
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events", response_model=list[schemas.EventOut])
def get_events(limit: int = 100, api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    return db.query(models.Event).order_by(models.Event.id.desc()).limit(limit).all()


@app.get("/events/{event_id}/report")
def get_event_report(event_id: int, api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Передаем данные в ИИ-движок
    report_text = ai_analyst.analyze_event({
        "process_name": event.process_name,
        "command_line": event.command_line,
        "user": event.user,
        "severity": event.severity,
        "anomaly_score": event.anomaly_score
    })

    return {"id": event_id, "report": report_text}

@app.post("/simulate")
async def run_simulation(api_key: str = Depends(verify_api_key)):
    try:
        script_path = os.path.join(os.path.dirname(__file__), "..", "generate_data.py")
        subprocess.Popen(["python3", script_path])
        return {"status": "success", "message": "Симуляция атак запущена!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска: {str(e)}")