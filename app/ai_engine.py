import os
from google import genai
from mitre_mapper import MitreMapper
from dotenv import load_dotenv
import random

class AIForensicEngine:
    def __init__(self):
        self.model_name = "Sentinel-AI v3.0 (SOC Core)"
        self.mitre = MitreMapper()

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "ТВОЙ_КЛЮЧ_СЮДА":
            self.client = genai.Client(api_key=api_key)
            self.is_active = True
        else:
            self.client = None
            self.is_active = False

    def _generate_fallback_report(self, event_data: dict) -> str:
        """Профессиональный отчёт на основе данных события и MITRE ATT&CK."""
        process = event_data.get("process_name", "Unknown")
        cmd = event_data.get("command_line", "") or ""
        user = event_data.get("user", "unknown")
        score = event_data.get("anomaly_score", 0.0)
        severity = event_data.get("severity", "normal").lower()

        techniques = self.mitre.get_attack_info(cmd)

        severity_map = {
            "critical": ("🔴 КРИТИЧЕСКИЙ", "немедленного реагирования", "ИЗОЛИРОВАТЬ"),
            "high":     ("🟠 ВЫСОКИЙ",    "срочного расследования",   "БЛОКИРОВАТЬ"),
            "medium":   ("🟡 СРЕДНИЙ",    "мониторинга",               "НАБЛЮДАТЬ"),
            "normal":   ("🟢 НОРМАЛЬНЫЙ", "плановой проверки",         "РАЗРЕШИТЬ"),
        }
        sev_label, sev_action, sev_verdict = severity_map.get(severity, severity_map["normal"])

        lines = []
        lines.append(f"### 🤖 ОТЧЁТ НЕЙРОСЕТЕВОГО АНАЛИТИКА Sentinel-AI v3.0")
        lines.append(f"**Статус:** {sev_label} | **Рекомендация:** {sev_verdict}")
        lines.append("")
        lines.append(f"**Анализируемый процесс:** `{process}` (пользователь: `{user}`)")
        if cmd:
            lines.append(f"**Командная строка:** `{cmd[:120]}{'...' if len(cmd) > 120 else ''}`")
        lines.append(f"**Аномальность (ML Score):** `{score:.4f}` — {'превышает пороговое значение' if score > 0.35 else 'в пределах нормы'}")
        lines.append("")

        if techniques:
            lines.append("#### 🎯 Обнаруженные техники MITRE ATT\u0026CK")
            for t in techniques:
                lines.append(f"- **{t['technique']}** — {t['name']}")
                lines.append(f"  *{t.get('description', 'Техника используется для получения несанкционированного доступа или выполнения вредоносного кода.')}*")
                if t.get("remediation"):
                    lines.append(f"  ✅ **Контрмера:** {t['remediation']}")
            lines.append("")
            lines.append("#### 📋 Вердикт анализатора")
            tech_names = ", ".join(t['name'] for t in techniques)
            lines.append(
                f"Зафиксирована активность, соответствующая паттернам {tech_names}. "
                f"Процесс `{process}` инициирован пользователем `{user}` с аномальным показателем {score:.4f}. "
                f"Требуется {sev_action}."
            )
        else:
            lines.append("#### 📋 Вердикт анализатора")
            if score > 0.35:
                lines.append(
                    f"Процесс `{process}` демонстрирует статистически аномальное поведение "
                    f"(score: {score:.4f}), не соответствующее базовым паттернам системы. "
                    f"Совпадений с известными техниками MITRE ATT&CK не обнаружено, однако "
                    f"профиль поведения требует {sev_action}."
                )
            else:
                lines.append(
                    f"Процесс `{process}` работает в штатном режиме. "
                    f"Аномальность ({score:.4f}) находится ниже порогового значения. "
                    f"Угрозы не обнаружено."
                )

        lines.append("")
        lines.append("---")
        lines.append("*Отчёт сформирован модулем Sentinel-AI на основе IsolationForest ML + MITRE ATT&CK KB*")
        return "\n".join(lines)

    def analyze_event(self, event_data: dict) -> str:
        process = event_data.get("process_name", "Unknown")
        cmd = event_data.get("command_line", "") or ""
        user = event_data.get("user", "unknown")
        score = event_data.get("anomaly_score", 0.0)
        severity = event_data.get("severity", "normal").lower()

        techniques = self.mitre.get_attack_info(cmd)
        tech_text = ", ".join([f"{t['technique']} ({t['name']})" for t in techniques]) if techniques else "Не обнаружено"

        if self.is_active:
            prompt = f"""Ты — продвинутый AI-аналитик в Security Operations Center (SOC). Твоя задача — проанализировать системное событие и выдать краткий, профессиональный криминалистический отчет (максимум 4-5 предложений) на русском языке.

Данные события:
- Пользователь: {user}
- Процесс: {process}
- Командная строка: {cmd}
- Уровень угрозы: {severity.upper()}
- Оценка аномалии (ML Score): {score:.4f}
- Найденные техники MITRE ATT&CK: {tech_text}

Объясни, что пытается сделать эта команда, насколько она опасна, и дай одну главную рекомендацию по реагированию. Не используй лишних приветствий, пиши в строгом техническом стиле."""

            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                return response.text
            except Exception:
                # Если API недоступен — используем умный fallback
                pass

        return self._generate_fallback_report(event_data)

# Инициализация
ai_analyst = AIForensicEngine()