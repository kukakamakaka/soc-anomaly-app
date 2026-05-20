class MitreMapper:
    def __init__(self):
        # Расширенный словарь техник MITRE ATT&CK с описаниями
        self.rules = [
            {
                "pattern": "powershell", 
                "technique": "T1059.001", 
                "name": "PowerShell Execution",
                "impact": "Выполнение произвольного кода через PowerShell.",
                "remediation": "Проверить логи PowerShell (Event ID 4104). Ограничить использование PowerShell через Constrained Language Mode."
            },
            {
                "pattern": "whoami", 
                "technique": "T1033", 
                "name": "System Owner/User Discovery",
                "impact": "Разведка: поиск текущего пользователя.",
                "remediation": "Обычно является частью автоматизированных скриптов разведки. Проверить сопутствующие команды."
            },
            {
                "pattern": "net user", 
                "technique": "T1087", 
                "name": "Account Discovery",
                "impact": "Разведка учетных записей пользователей.",
                "remediation": "Проверить, не является ли это попыткой поиска привилегированных пользователей для повышения прав."
            },
            {
                "pattern": "curl", 
                "technique": "T1105", 
                "name": "Ingress Tool Transfer",
                "impact": "Загрузка вредоносных инструментов извне.",
                "remediation": "Проверить URL загрузки. Изолировать хост, если загружен исполняемый файл."
            },
            {
                "pattern": "wget", 
                "technique": "T1105", 
                "name": "Ingress Tool Transfer",
                "impact": "Загрузка вредоносных инструментов извне.",
                "remediation": "Проверить URL загрузки и целостность системы."
            },
            {
                "pattern": "bitsadmin", 
                "technique": "T1197", 
                "name": "BITS Jobs",
                "impact": "Скрытая передача файлов через системную службу BITS.",
                "remediation": "Проверить текущие задачи BITS с помощью 'bitsadmin /list /allusers /verbose'."
            },
            {
                "pattern": "encodedcommand", 
                "technique": "T1564.003", 
                "name": "Obfuscated Files or Information",
                "impact": "Попытка скрыть содержимое команды (обфускация).",
                "remediation": "Декодировать Base64-команду и проанализировать её реальное действие."
            },
            {
                "pattern": "schtasks", 
                "technique": "T1053.005", 
                "name": "Scheduled Task",
                "impact": "Закрепление в системе через планировщик задач.",
                "remediation": "Проверить список запланированных задач на предмет подозрительных записей."
            },
            {
                "pattern": "reg add", 
                "technique": "T1547.001", 
                "name": "Registry Run Keys / Startup Folder",
                "impact": "Закрепление в системе через автозагрузку в реестре.",
                "remediation": "Проверить ключи Run/RunOnce в реестре."
            }
        ]

    def get_attack_info(self, command_line: str):
        if not command_line:
            return []
        command_line = command_line.lower()
        found_techniques = []
        for rule in self.rules:
            if rule["pattern"] in command_line:
                found_techniques.append(rule)

        return found_techniques


    def format_techniques(self, techniques: list):
        if not techniques:
            return "Неизвестная техника"
        return ", ".join([f"{t['name']} ({t['technique']})" for t in techniques])