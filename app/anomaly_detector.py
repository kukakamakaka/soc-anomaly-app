import pandas as pd
import re
import os
import joblib
import math
import logging
import numpy as np
from collections import Counter
from sklearn.ensemble import IsolationForest

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    MODEL_FILE = "soc_model.joblib"

    def __init__(self):
        # contamination=0.05 означает, что мы ожидаем 5% аномалий
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False
        self.load_model()

    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        counts = Counter(text)
        probs = [c/len(text) for c in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def _extract_features(self, events: list[dict]) -> pd.DataFrame:
        data = []
        for e in events:
            cmd = (e.get("command_line", "") or "").lower()
            proc = (e.get("process_name", "") or "").lower()

            # 1. Базовые метрики длины и структуры
            features = {
                "cmd_length": len(cmd),
                # Добавляем больше спецсимволов, часто используемых в эксплойтах
                "special_chars": len(re.findall(r'[&|;$%^><!`\\]', cmd)),
                "arg_count": len(cmd.split()),
                "pipe_count": cmd.count('|') + cmd.count('>'),
                
                # 2. Подозрительные пути
                "is_suspicious_path": 1 if re.search(r'\b(temp|appdata|recycle\.bin|/tmp|/dev/shm|/var/tmp)\b', cmd) else 0,

                # 3. Признаки обфускации
                "entropy": self._calculate_entropy(cmd),
                "has_base64": 1 if re.search(r'[A-Za-z0-9+/]{40,}', cmd) else 0,
                "obfuscation_markers": len(re.findall(r'(\^|\$|{|}|\+)', cmd)),

                # 4. Сетевые индикаторы (IP адреса)
                "has_ip": 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', cmd) else 0,

                # 5. Категории команд
                "is_recon_cmd": 1 if any(recon in cmd for recon in ['whoami', 'net user', 'ipconfig', 'id', 'uname', 'systeminfo', 'who']) else 0,
                "is_download_tool": 1 if any(tool in cmd for tool in ['curl', 'wget', 'downloadstring', 'bitsadmin', 'certutil']) else 0,
                "is_shell_proc": 1 if any(s in proc for s in ['powershell', 'cmd.exe', 'bash', 'sh', 'zsh']) else 0
            }
            data.append(features)
        return pd.DataFrame(data)

    def train(self, events: list[dict]):
        if len(events) < 5:
            logger.warning(f"Недостаточно данных для обучения: получено {len(events)}, нужно минимум 5")
            return
        
        X = self._extract_features(events)
        # contamination=0.1 для большей чувствительности к аномалиям
        self.model = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
        self.model.fit(X)
        self.is_trained = True
        self.save_model()
        logger.info("Модель успешно обучена и сохранена.")

    def save_model(self):
        try:
            joblib.dump(self.model, self.MODEL_FILE)
        except Exception as e:
            logger.error(f"Ошибка при сохранении модели: {e}")

    def load_model(self):
        if os.path.exists(self.MODEL_FILE):
            try:
                self.model = joblib.load(self.MODEL_FILE)
                self.is_trained = True
                logger.info("Существующая модель загружена с диска.")
            except Exception as e:
                logger.error(f"Ошибка при загрузке модели: {e}")

    def score(self, event: dict) -> float:
        if not self.is_trained:
            return 0.1
        
        features_df = self._extract_features([event])
        raw_score = float(self.model.decision_function(features_df)[0])
        
        # Базовая вероятность из ML модели
        probability = 1.0 / (1.0 + math.exp((raw_score + 0.02) * 18))
        
        # ГИБРИДНЫЙ ПОДХОД: Буст скора при наличии явных признаков атаки
        # Если модель не уверена, но мы видим критические маркеры - повышаем балл
        features = features_df.iloc[0]
        boost = 0.0
        if features["has_base64"]: boost += 0.4
        if features["is_suspicious_path"]: boost += 0.3
        if features["has_ip"] and features["is_download_tool"]: boost += 0.5
        if features["obfuscation_markers"] > 5: boost += 0.3
        
        final_score = min(0.99, probability + boost)
        
        return float(final_score)