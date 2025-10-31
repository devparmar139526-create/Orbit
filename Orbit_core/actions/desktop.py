"""
Desktop application control and system commands
"""

import subprocess
import platform
import re
import os

class DesktopAction:
    def __init__(self, settings=None):
        self.settings = settings
        self.os_type = platform.system()
        self.app_map = {
            'notepad': {'Windows': 'notepad.exe'},
            'calculator': {'Windows': 'calc.exe'},
            'terminal': {'Windows': 'cmd.exe'},
            'chrome': {'Windows': 'chrome.exe'},
            'firefox': {'Windows': 'firefox.exe'},
            'edge': {'Windows': 'msedge.exe'},
            'code': {'Windows': 'code.cmd'},
            'vscode': {'Windows': 'code.cmd'}
        }
        
        # Check if app control is allowed
        if settings:
            self.allow_app_control = settings.ALLOW_APP_CONTROL
            self.allowed_apps = [app.lower() for app in settings.ALLOWED_APPS]
            self.blocked_apps = [app.lower() for app in settings.BLOCKED_APPS]
        else:
            self.allow_app_control = True
            self.allowed_apps = []
            self.blocked_apps = []

    def execute(self, command: str) -> str:
        # Check if app control is allowed
        if not self.allow_app_control:
            return "Application control is disabled in settings."
        
        command_lower = command.lower()
        if 'open' in command_lower or 'launch' in command_lower or 'start' in command_lower:
            return self._open_application(command_lower)
        elif 'close' in command_lower:
            return "Closing applications is not supported for safety reasons."
        else:
            return "I can help open applications. Try 'open Chrome'."

    def _find_executable_windows(self, app_name: str) -> str:
        if app_name in self.app_map:
            return self.app_map[app_name].get(self.os_type)
        
        start_menu_folders = [
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ.get('ALLUSERSPROFILE', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]

        for folder in start_menu_folders:
            if not os.path.isdir(folder): continue
            for root, _, files in os.walk(folder):
                for file in files:
                    if app_name.lower() in file.lower() and file.endswith('.lnk'):
                        return os.path.join(root, file)
        return app_name

    def _open_application(self, command: str) -> str:
        match = re.search(r'(?:open|launch|start)\s+(\w+)', command)
        if not match:
            return "I couldn't identify which application to open."
        
        app_name = match.group(1).lower().strip()
        
        # Check if app is blocked
        if app_name in self.blocked_apps:
            return f"Sorry, {app_name} is blocked by settings."
        
        # Check if app is in allowed list (if list is not empty)
        if self.allowed_apps and app_name not in self.allowed_apps:
            return f"Sorry, {app_name} is not in the allowed applications list."

        cmd = app_name
        if self.os_type == 'Windows':
            cmd = self._find_executable_windows(app_name)

        try:
            subprocess.Popen(f'start "" "{cmd}"', shell=True)
            return f"Opening {app_name}."
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"

    def get_system_info(self) -> str:
        return f"Running on {self.os_type} ({platform.release()})"