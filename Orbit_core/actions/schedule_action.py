"""
Task scheduling and reminders
"""

from datetime import datetime, timedelta
import re

class ScheduleAction:
    def __init__(self, settings):
        self.settings = settings
        self.pending_task = None  # Store task waiting for time
    
    def schedule(self, command: str):
        """Parse and schedule a task, supports two-step scheduling"""
        command_lower = command.lower()
        
        # Check if this is a time response to a pending task
        if self.pending_task:
            scheduled_time = self._extract_time(command_lower)
            if scheduled_time:
                # Complete the scheduling
                result = {
                    'task': self.pending_task,
                    'scheduled_time': scheduled_time
                }
                self.pending_task = None  # Clear pending task
                return result
            else:
                return "I didn't understand that time. Please say something like '5 PM' or 'in 30 minutes'."
        
        # Check for "remind me to" without time (step 1)
        if command_lower.startswith('remind me to'):
            task = command_lower.replace('remind me to', '').strip()
            if task and not self._extract_time(command_lower):
                self.pending_task = task
                return f"Sure! I'll remind you to {task}. When would you like me to remind you?"
        
        # Regular scheduling with complete command
        task = self._extract_task(command_lower)
        scheduled_time = self._extract_time(command_lower)
        
        if not task:
            return "I couldn't understand what you want me to remind you about."
        
        if not scheduled_time:
            return f"I understood you want to: '{task}', but I couldn't determine when. Please specify a time."
        
        # SUCCESS: Return structured data for the caller
        return {
            'task': task,
            'scheduled_time': scheduled_time
        }
    
    # MODIFIED: Added pattern to extract desktop commands correctly
    def _extract_task(self, command: str) -> str:
        """Extract task description from command"""
        
        # Pattern 1: Catch specific app commands like "open notepad" before the time phrase
        # Captures everything between 'open/launch/start' and the time marker (at/in/tomorrow/$)
        app_command_patterns = [
             r'((?:open|launch|start)\s+.+?)(?:\s+at|\s+in|\s+tomorrow|$)',
        ]
        
        for pattern in app_command_patterns:
            match = re.search(pattern, command)
            if match:
                # This returns the full command, e.g., "open notepad"
                return match.group(1).strip()

        # Pattern 2: Original, formal scheduling phrases
        patterns_original = [
            r'remind me to\s+(.+?)(?:\s+at|\s+in|\s+tomorrow|$)',
            r'schedule\s+(.+?)(?:\s+at|\s+in|\s+tomorrow|$)',
            r'set (?:a )?reminder (?:to )?\s*(.+?)(?:\s+at|\s+in|\s+tomorrow|$)'
        ]
        
        for pattern in patterns_original:
            match = re.search(pattern, command)
            if match:
                return match.group(1).strip()
        
        return ""
    
    # NOTE: _extract_time is assumed to be the correct, updated version
    def _extract_time(self, command: str) -> datetime:
        """Extract time from command"""
        now = datetime.now()
        
        # ... (rest of the time extraction logic from your previous successful iteration)
        # Check for specific time (e.g., "at 5 PM", "at 17:00")
        time_patterns = [
            r'at\s+(\d{1,2})\s*(?::(\d{2}))?\s*(am|pm)',
            r'at\s+(\d{1,2}):(\d{2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, command)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                
                # Handle AM/PM
                if len(match.groups()) >= 3 and match.group(3):
                    meridiem = match.group(3).lower()
                    if meridiem == 'pm' and hour != 12:
                        hour += 12
                    elif meridiem == 'am' and hour == 12:
                        hour = 0
                
                scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time has passed today, schedule for tomorrow
                if scheduled < now:
                    scheduled += timedelta(days=1)
                
                return scheduled
        
        # Check for relative time (e.g., "in 30 minutes", "in 2 hours")
        relative_pattern = r'in\s+(\d+)\s+(minute|hour|second)s?'
        match = re.search(relative_pattern, command)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'minute':
                return now + timedelta(minutes=amount)
            elif unit == 'hour':
                return now + timedelta(hours=amount)
            elif unit == 'second':
                return now + timedelta(seconds=amount)
        
        # Check for "tomorrow"
        if 'tomorrow' in command:
            tomorrow = now + timedelta(days=1)
            # Default to 9 AM tomorrow
            return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return None
    
    def execute_scheduled_task(self, task: str) -> str:
        """Execute a scheduled task - supports desktop commands and reminders"""
        task_lower = task.lower()
        
        # Check if this is a desktop command
        if any(cmd in task_lower for cmd in ['open', 'launch', 'start']):
            # Import desktop action to execute the command
            from .desktop import DesktopAction
            desktop = DesktopAction(self.settings)
            return desktop.execute(task)
        
        # For other tasks, just return as a reminder
        return f"Reminder: {task}"