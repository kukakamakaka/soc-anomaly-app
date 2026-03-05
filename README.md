# 🛡️ Sentinel.AI: Hybrid SOC Anomaly Detection System

**Sentinel.AI** — это полнофункциональная система мониторинга безопасности (SOC), которая использует гибридный подход для обнаружения угроз: Машинное обучение (Isolation Forest) и экспертные правила (MITRE ATT&CK Mapping).

![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-4169E1?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker)

## 🚀 Основные возможности
* **Real-time Ingestion:** Прием и обработка системных логов через FastAPI.
* **ML Anomaly Detection:** Использование алгоритма *Isolation Forest* для выявления нестандартного поведения процессов.
* **MITRE ATT&CK Integration:** Автоматическое сопоставление подозрительных команд с техниками MITRE (T1059, T1105 и др.).
* **AI Forensic Reports:** Генерация подробных отчетов по инцидентам (Simulation/LLM-ready).
* **Modern Dashboard:** Интерактивный интерфейс на Next.js 15 с графиками аномалий (Recharts) и Glassmorphism дизайном.

## 🛠 Стек технологий
* **Backend:** Python 3.10, FastAPI, SQLAlchemy, Scikit-learn (ML).
* **Frontend:** React 19, Next.js 15 (App Router), TypeScript, Tailwind CSS, Recharts, Lucide Icons.
* **Database:** PostgreSQL.
* **Infrastructure:** Docker, Docker Compose.

## 📦 Как запустить проект

### 1. Клонирование репозитория
```bash
git clone [https://github.com/kukakamakaka/soc-anomaly-app.git](https://github.com/kukakamakaka/soc-anomaly-app.git)
cd soc-anomaly-app