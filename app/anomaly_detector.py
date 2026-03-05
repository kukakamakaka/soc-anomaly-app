import pandas as pd
import re
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    def __init__(self):
        # contamination=0.05 означает, что мы ожидаем 5% аномалий
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False

    def _extract_features(self, events: list[dict]) -> pd.DataFrame:
        data = []
        for e in events:
            cmd = e.get("command_line", "").lower()
            proc = e.get("process_name", "").lower()

            features = {
                # 1. Длина команды (аномально длинные команды часто признак эксплойта)
                "cmd_length": len(cmd),

                # 2. Количество спецсимволов (признак обфускации или инъекции)
                "special_chars": len(re.findall(r'[&|;$%^]', cmd)),

                # 3. Запуск из подозрительных путей (Temp, AppData, /tmp)
                "is_suspicious_path": 1 if any(
                    path in cmd for path in ['temp', 'appdata', 'recycle.bin', '/tmp']) else 0,

                # 4. Использование системных утилит для разведки (whoami, net user, ipconfig)
                "is_recon_cmd": 1 if any(
                    recon in cmd for recon in ['whoami', 'net user', 'ipconfig', 'id', 'uname']) else 0,

                # 5. Использование инструментов скачивания (curl, wget, powershell download)
                "is_download_tool": 1 if any(
                    tool in cmd for tool in ['curl', 'wget', 'downloadstring', 'bitsadmin']) else 0
            }
            data.append(features)
        return pd.DataFrame(data)

    def train(self, events: list[dict]):
        if len(events) < 5:  # Для тестов снизим порог до 5
            return
        X = self._extract_features(events)
        self.model.fit(X)
        self.is_trained = True

    def score(self, event: dict) -> float:
        if not self.is_trained:
            return 0.0
        X = self._extract_features([event])
        # Чем ниже число (уходит в минус), тем больше это похоже на аномалию
        return float(self.model.decision_function(X)[0])