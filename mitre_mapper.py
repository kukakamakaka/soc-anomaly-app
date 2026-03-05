class MitreMapper:
    def __init__(self):
        # Словарь техник MITRE ATT&CK
        self.rules = [
            {"pattern": "powershell", "technique": "T1059.001", "name": "PowerShell Execution"},
            {"pattern": "whoami", "technique": "T1033", "name": "System Owner/User Discovery"},
            {"pattern": "net user", "technique": "T1087", "name": "Account Discovery"},
            {"pattern": "curl", "technique": "T1105", "name": "Ingress Tool Transfer"},
            {"pattern": "bitsadmin", "technique": "T1197", "name": "BITS Jobs"},
            {"pattern": "encodedcommand", "technique": "T1564.003", "name": "Obfuscated Files or Information"}
        ]

    def get_attack_info(self, command_line: str):
        command_line = command_line.lower()
        found_techniques = []
        for rule in self.rules:
            if rule["pattern"] in command_line:
                found_techniques.append(f"{rule['name']} ({rule['technique']})")

        return ", ".join(found_techniques) if found_techniques else "Unknown Technique"