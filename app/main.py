from fastapi import FastAPI, Depends, HTTPException
from app.ai_engine import ai_analyst
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas
from app.anomaly_detector import AnomalyDetector
import subprocess
import os

# Создаем таблицы в PostgreSQL (в Докере)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SOC Anomaly Detection")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Адрес твоего фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем детектор при старте
detector = AnomalyDetector()


# 1. Функция подключения к БД (теперь она определена!)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. Функция обучения (чтобы модель знала, что такое "норма")
def train_model_on_existing_data(db: Session):
    all_events = db.query(models.Event).all()
    if len(all_events) >= 5:  # Обучаем, если есть хотя бы 5 записей
        events_list = [
            {"process_name": e.process_name, "command_line": e.command_line, "user": e.user}
            for e in all_events
        ]
        detector.train(events_list)


@app.post("/ingest", response_model=schemas.EventOut)
def ingest_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    train_model_on_existing_data(db)
    score = detector.score(event.dict())

    # ПРОВЕРКА MITRE (Твоя логика!)
    mitre_info = analyze_with_mitre(event.command_line)

    # Гибридная логика определения серьезности
    severity = "normal"
    if score < -0.05: severity = "low"
    if score < -0.15 or mitre_info: severity = "high" # Если есть техника MITRE - сразу HIGH
    if score < -0.25 and mitre_info: severity = "critical"

    db_event = models.Event(
        **event.dict(),
        anomaly_score=score,
        severity=severity,
        mitre_technique=mitre_info # Сохраняем результат анализа
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events", response_model=list[schemas.EventOut])
def get_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()

# Если severity "high" или "critical", вызываем этот метод
def generate_ai_report(event_details: str):
    # Здесь будет вызов OpenAI API или LangChain
    # "Проанализируй событие {event_details} и напиши краткий отчет для аналитика SOC"
    pass

# База знаний MITRE (для твоего резюме и диплома)
MITRE_TECHNIQUES = {
    "powershell": "T1059.001 (Command and Scripting Interpreter)",
    "whoami": "T1033 (System Owner/User Discovery)",
    "bitsadmin": "T1197 (BITS Jobs)",
    "curl": "T1105 (Ingress Tool Transfer)",
    "net user": "T1087 (Account Discovery)"
}

def analyze_with_mitre(command: str):
    command = command.lower()
    for trigger, technique in MITRE_TECHNIQUES.items():
        if trigger in command:
            return technique
    return None


@app.get("/events/{event_id}/report")
def get_ai_report(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        return {"error": "Event not found"}

    # Логика "ИИ-аналитика"
    # В реальном проекте здесь был бы вызов OpenAI API
    prompt = f"Проанализируй команду: {event.command_line}. Процесс: {event.process_name}."

    if "powershell" in event.command_line.lower():
        report = (
            "⚠️ **Анализ ИИ:** Обнаружена попытка запуска скрытого скрипта PowerShell. "
            "Использование `-EncodedCommand` часто указывает на попытку обхода антивируса (EDR). "
            "**Рекомендация:** Немедленно изолировать хост и проверить сетевые соединения."
        )
    elif "curl" in event.command_line.lower() or "wget" in event.command_line.lower():
        report = (
            "🌐 **Анализ ИИ:** Подозрительная загрузка внешнего файла. "
            "Утилита пытается скачать объект с удаленного сервера. Это может быть загрузка бэкдора. "
            "**Рекомендация:** Проверить репутацию IP-адреса источника."
        )
    else:
        report = "✅ **Анализ ИИ:** Поведение соответствует стандартным операциям системы. Аномалий не выявлено."

    return {"report": report}

@app.get("/events/{event_id}/report")
def get_event_report(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.SOCEvent).filter(models.SOCEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Передаем данные в ИИ-движок
    report_text = ai_analyst.analyze_event({
        "process_name": event.process_name,
        "command_line": event.command_line,
        "user": event.user,
        "severity": event.severity
    })

    return {"id": event_id, "report": report_text}


@app.post("/simulate")
async def run_simulation():
    try:
        # Указываем путь к скрипту (убедись, что путь верный относительно main.py)
        script_path = os.path.join(os.path.dirname(__file__), "..", "generate_data.py")

        # Запускаем скрипт в фоновом режиме
        subprocess.Popen(["python3", script_path])

        return {"status": "success", "message": "Симуляция атак запущена!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска: {str(e)}")