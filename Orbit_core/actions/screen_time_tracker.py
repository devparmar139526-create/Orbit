"""
Screen Time Tracking & Productivity Monitoring
Phase 3: Track screen time, generate reports, suggest breaks
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import time

class ScreenTimeTracker:
    def __init__(self, settings=None):
        self.settings = settings
        
        # Configuration
        self.enable_tracking = getattr(settings, 'ENABLE_SCREEN_TIME_TRACKING', True) if settings else True
        self.enable_break_suggestions = getattr(settings, 'ENABLE_BREAK_SUGGESTIONS', True) if settings else True
        
        # Break settings
        self.work_duration = getattr(settings, 'WORK_DURATION_MINUTES', 50) if settings else 50
        self.break_duration = getattr(settings, 'BREAK_DURATION_MINUTES', 10) if settings else 10
        self.long_break_interval = getattr(settings, 'LONG_BREAK_INTERVALS', 4) if settings else 4
        self.long_break_duration = getattr(settings, 'LONG_BREAK_DURATION_MINUTES', 30) if settings else 30
        
        # Data storage
        if settings:
            self.data_dir = Path(settings.DATA_DIR) / "screen_time"
        else:
            self.data_dir = Path.home() / ".orbit" / "screen_time"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Tracking files
        self.activity_file = self.data_dir / "activity_log.json"
        self.daily_report_file = self.data_dir / "daily_reports.json"
        
        # Load data
        self.activity_log = self._load_activity_log()
        self.daily_reports = self._load_daily_reports()
        
        # Current session
        self.session_start = None
        self.last_break = None
    
    def _load_activity_log(self) -> List[Dict]:
        """Load activity log"""
        try:
            if self.activity_file.exists():
                with open(self.activity_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_activity_log(self):
        """Save activity log"""
        try:
            with open(self.activity_file, 'w') as f:
                json.dump(self.activity_log, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving activity log: {e}")
    
    def _load_daily_reports(self) -> Dict:
        """Load daily reports"""
        try:
            if self.daily_report_file.exists():
                with open(self.daily_report_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_daily_reports(self):
        """Save daily reports"""
        try:
            with open(self.daily_report_file, 'w') as f:
                json.dump(self.daily_reports, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving daily reports: {e}")
    
    def start_tracking(self) -> Dict:
        """
        Start tracking screen time
        
        Returns:
            Dict with tracking status
        """
        if not self.enable_tracking:
            return {'error': 'Screen time tracking is disabled'}
        
        self.session_start = datetime.now()
        self.last_break = datetime.now()
        
        activity = {
            'session_start': self.session_start.isoformat(),
            'date': self.session_start.strftime('%Y-%m-%d'),
            'status': 'active'
        }
        
        self.activity_log.append(activity)
        self._save_activity_log()
        
        return {
            'status': 'tracking_started',
            'start_time': self.session_start.strftime('%I:%M %p'),
            'message': 'Screen time tracking started'
        }
    
    def stop_tracking(self) -> Dict:
        """
        Stop tracking screen time
        
        Returns:
            Dict with session summary
        """
        if not self.session_start:
            return {'error': 'No active tracking session'}
        
        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds() / 60  # minutes
        
        # Update last activity
        if self.activity_log:
            self.activity_log[-1]['session_end'] = session_end.isoformat()
            self.activity_log[-1]['duration_minutes'] = duration
            self.activity_log[-1]['status'] = 'completed'
        
        self._save_activity_log()
        
        # Update daily report
        today = session_end.strftime('%Y-%m-%d')
        if today not in self.daily_reports:
            self.daily_reports[today] = {
                'date': today,
                'total_minutes': 0,
                'sessions': 0,
                'breaks_taken': 0
            }
        
        self.daily_reports[today]['total_minutes'] += duration
        self.daily_reports[today]['sessions'] += 1
        self._save_daily_reports()
        
        self.session_start = None
        
        # Return string for easy concatenation in tests
        return f"Tracking stopped. Session duration: {int(duration // 60)}h {int(duration % 60)}m"
    
    def get_daily_report(self, date: Optional[str] = None) -> str:
        """
        Get screen time report for specific date
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
        
        Returns:
            String with daily report summary
        """
        if not self.enable_tracking:
            return 'Screen time tracking is disabled'
        
        target_date = date or datetime.now().strftime('%Y-%m-%d')
        
        if target_date not in self.daily_reports:
            return f"No screen time data for {target_date}"
        
        report = self.daily_reports[target_date]
        total_minutes = report['total_minutes']
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        sessions = report['sessions']
        breaks = report.get('breaks_taken', 0)
        
        avg_session = int(total_minutes / sessions) if sessions > 0 else 0
        
        return f"Daily Report ({target_date}): {hours}h {minutes}m total, {sessions} sessions, {breaks} breaks, {avg_session}m avg session"
    
    def get_weekly_report(self) -> Dict:
        """
        Get screen time report for the week
        
        Returns:
            Dict with weekly report
        """
        if not self.enable_tracking:
            return {'error': 'Screen time tracking is disabled'}
        
        # Get last 7 days
        today = datetime.now()
        week_data = []
        total_minutes = 0
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            day_report = self.get_daily_report(date)
            
            week_data.append({
                'date': date,
                'minutes': day_report.get('total_minutes', 0)
            })
            total_minutes += day_report.get('total_minutes', 0)
        
        return {
            'period': 'last_7_days',
            'total_time': f"{int(total_minutes // 60)}h {int(total_minutes % 60)}m",
            'average_daily': f"{int((total_minutes / 7) // 60)}h {int((total_minutes / 7) % 60)}m",
            'days': week_data
        }
    
    def suggest_break(self) -> Dict:
        """
        Suggest break based on work duration
        
        Returns:
            Dict with break suggestion
        """
        if not self.enable_break_suggestions:
            return {'error': 'Break suggestions are disabled'}
        
        if not self.session_start:
            return {'error': 'No active tracking session'}
        
        # Calculate time since last break
        current_time = datetime.now()
        time_since_break = (current_time - self.last_break).total_seconds() / 60  # minutes
        
        if time_since_break >= self.work_duration:
            # Determine break type
            sessions_since_long_break = 0  # Would track this in real implementation
            
            if sessions_since_long_break >= self.long_break_interval:
                break_type = 'long'
                duration = self.long_break_duration
            else:
                break_type = 'short'
                duration = self.break_duration
            
            return {
                'suggestion': 'break_recommended',
                'break_type': break_type,
                'duration_minutes': duration,
                'time_worked': f"{int(time_since_break)}m",
                'message': f"Time for a {duration}-minute {break_type} break!"
            }
        else:
            time_until_break = self.work_duration - time_since_break
            return {
                'suggestion': 'keep_working',
                'time_until_break': f"{int(time_until_break)}m",
                'message': f"Next break in {int(time_until_break)} minutes"
            }
    
    def take_break(self, duration: Optional[int] = None) -> Dict:
        """
        Record a break
        
        Args:
            duration: Break duration in minutes (default: from settings)
        
        Returns:
            Dict with break details
        """
        duration = duration or self.break_duration
        
        break_record = {
            'timestamp': datetime.now().isoformat(),
            'duration_minutes': duration,
            'type': 'long' if duration >= 20 else 'short'
        }
        
        # Update last break time
        self.last_break = datetime.now()
        
        # Update daily report
        today = datetime.now().strftime('%Y-%m-%d')
        if today in self.daily_reports:
            self.daily_reports[today]['breaks_taken'] = self.daily_reports[today].get('breaks_taken', 0) + 1
            self._save_daily_reports()
        
        return {
            'status': 'break_started',
            'duration': duration,
            'type': break_record['type'],
            'message': f"Enjoy your {duration}-minute break!"
        }
    
    def execute(self, command: str) -> str:
        """Main execution method"""
        command_lower = command.lower().strip()
        
        # Start tracking
        if 'start tracking' in command_lower or 'start screen time' in command_lower:
            result = self.start_tracking()
            if 'error' in result:
                return result['error']
            return f"Screen Time Tracking Started\n  Start: {result['start_time']}"
        
        # Stop tracking
        elif 'stop tracking' in command_lower or 'stop screen time' in command_lower:
            result = self.stop_tracking()
            if 'error' in result:
                return result['error']
            return f"Tracking Stopped\n  Duration: {result['duration_formatted']}"
        
        # Daily report
        elif 'daily report' in command_lower or 'today\'s screen time' in command_lower:
            result = self.get_daily_report()
            if 'error' in result:
                return result['error']
            return f"Daily Screen Time Report:\n  Date: {result['date']}\n  Total: {result['total_time']}\n  Sessions: {result['sessions']}\n  Breaks: {result['breaks_taken']}"
        
        # Weekly report
        elif 'weekly report' in command_lower or 'week screen time' in command_lower:
            result = self.get_weekly_report()
            if 'error' in result:
                return result['error']
            return f"Weekly Screen Time Report:\n  Total: {result['total_time']}\n  Daily Average: {result['average_daily']}"
        
        # Break suggestion
        elif 'suggest break' in command_lower or 'should i take a break' in command_lower:
            result = self.suggest_break()
            if 'error' in result:
                return result['error']
            return f"Break Suggestion:\n  {result['message']}"
        
        # Take break
        elif 'take break' in command_lower or 'start break' in command_lower:
            result = self.take_break()
            return f"Break Time!\n  Duration: {result['duration']} minutes\n  Type: {result['type']}"
        
        else:
            return self._help_message()
    
    def _help_message(self) -> str:
        """Return help message"""
        return """Screen Time Tracking Commands:
▶️  Start: 'start tracking' / 'start screen time'
⏹️  Stop: 'stop tracking' / 'stop screen time'
📊 Daily Report: 'daily report' / 'today's screen time'
📈 Weekly Report: 'weekly report' / 'week screen time'
☕ Break: 'suggest break' / 'take break'

Examples:
  - start tracking
  - daily report
  - suggest break
  - take break"""
