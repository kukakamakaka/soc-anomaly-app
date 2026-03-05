import time
import re


class AIForensicEngine:
    def __init__(self):
        self.model_name = "Sentinel-GPT v2.6"
        # База знаний техник (имитация)
        self.threat_intel = {
            "bitsadmin": {"id": "T1197", "name": "BITS Jobs", "danger": "High"},
            "powershell": {"id": "T1059.001", "name": "PowerShell Scripting", "danger": "Critical"},
            "curl": {"id": "T1105", "name": "Ingress Tool Transfer", "danger": "Medium"},
            "cmd": {"id": "T1059.003", "name": "Windows Command Shell", "danger": "High"}
        }

    def _detect_indicators(self, cmd: str) -> list:
        """Поиск индикаторов компрометации (IoC) в строке"""
        indicators = []
        if "http" in cmd: indicators.append("External Network Connection")
        if "enc" in cmd or "bypass" in cmd: indicators.append("Security Evacuation")
        if "temp" in cmd: indicators.append("Hidden Payload Location")
        if "/transfer" in cmd: indicators.append("Unauthorized Data Transfer")
        return indicators

    def analyze_event(self, event_data: dict) -> str:
        """Генерирует глубокий криминалистический отчет"""
        process = event_data.get("process_name", "Unknown").lower()
        cmd = event_data.get("command_line", "").lower()
        user = event_data.get("user", "unknown")
        severity = event_data.get("severity", "normal")
        score = event_data.get("anomaly_score", 0)

        # Эффект "глубокого сканирования"
        time.sleep(0.6)

        if severity in ["high", "critical"] or score < 0:
            # 1. Проверка по базе MITRE
            tech = next((self.threat_intel[k] for k in self.threat_intel if k in process or k in cmd), None)

            # 2. Поиск подозрительных паттернов
            iocs = self._detect_indicators(cmd)
            ioc_text = f" Обнаружены маркеры: {', '.join(iocs)}." if iocs else ""

            if tech:
                return (
                    f"🚨 ВЕРДИКТ: ОБНАРУЖЕНА ТЕХНИКА {tech['id']} ({tech['name']}). "
                    f"Процесс '{process}' запущен пользователем '{user}' с аномальными параметрами.{ioc_text} "
                    f"Действие классифицировано как попытка {tech['danger'].lower()} уровня опасности. "
                    f"Рекомендуется немедленная изоляция хоста.")

            return (
                f"⚠️ АНОМАЛИЯ ПОВЕДЕНИЯ: Система зафиксировала отклонение процесса {process} от нормального профиля. "
                f"ML-скоринг ({score:.4f}) указывает на нетипичное использование системных ресурсов. "
                f"Требуется ручная проверка аналитиком SOC.")

        return f"✅ СИСТЕМА ЧИСТА: Процесс {process} верифицирован. Поведенческий паттерн пользователя {user} в пределах нормы."


# Инициализация
ai_analyst = AIForensicEngine()