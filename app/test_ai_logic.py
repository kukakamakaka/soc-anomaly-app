from app.ai_engine import ai_analyst
from app.anomaly_detector import AnomalyDetector
from mitre_mapper import MitreMapper

def test_logic():
    print("--- Testing AI Logic ---\n")
    
    # 1. Test Anomaly Detector
    detector = AnomalyDetector()
    # Mock some data for training if not trained
    if not detector.is_trained:
        print("Training model with mock normal data...")
        normal_events = [
            {"process_name": "explorer.exe", "command_line": "C:\\Windows\\explorer.exe", "user": "admin"},
            {"process_name": "chrome.exe", "command_line": "chrome.exe --new-window", "user": "admin"},
            {"process_name": "svchost.exe", "command_line": "svchost.exe -k netsvcs", "user": "system"},
            {"process_name": "lsass.exe", "command_line": "lsass.exe", "user": "system"},
            {"process_name": "cmd.exe", "command_line": "dir", "user": "admin"}
        ]
        detector.train(normal_events)

    # 2. Test Malicious Command
    malicious_event = {
        "process_name": "powershell.exe",
        "command_line": "powershell.exe -ExecutionPolicy Bypass -EncodedCommand SQBFAFIAAIAA...",
        "user": "victim_user"
    }
    
    score = detector.score(malicious_event)
    print(f"Anomaly Score for PowerShell attack: {score:.4f}")
    
    # 3. Test AI Report Generation
    report = ai_analyst.analyze_event({
        **malicious_event,
        "anomaly_score": score
    })
    
    # 4. Test High Entropy / Suspicious Path (no direct MITRE)
    suspicious_event = {
        "process_name": "unknown_binary",
        "command_line": "/tmp/evil_bin --data-dir /var/tmp/.hidden_config_xyz_123",
        "user": "nobody"
    }
    
    susp_score = detector.score(suspicious_event)
    print(f"\nAnomaly Score for Suspicious Path: {susp_score:.4f}")
    
    susp_report = ai_analyst.analyze_event({
        **suspicious_event,
        "anomaly_score": susp_score
    })
    print("\nSuspicious Path Report:")
    print(susp_report)

    print("\n--- Testing Completed ---")


if __name__ == "__main__":
    test_logic()
