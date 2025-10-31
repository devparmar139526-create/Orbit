"""
AI-Powered Productivity Features
Phase 3: Task Prediction, Smart Reminders, Schedule Optimization
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

class ProductivityAI:
    def __init__(self, settings=None):
        self.settings = settings
        
        # Configuration
        self.enable_task_prediction = getattr(settings, 'ENABLE_TASK_PREDICTION', True) if settings else True
        self.enable_smart_reminders = getattr(settings, 'ENABLE_SMART_REMINDERS', True) if settings else True
        self.enable_schedule_optimization = getattr(settings, 'ENABLE_SCHEDULE_OPTIMIZATION', True) if settings else True
        
        # Data storage
        if settings:
            self.data_dir = Path(settings.DATA_DIR) / "productivity"
        else:
            self.data_dir = Path.home() / ".orbit" / "productivity"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Task history file
        self.task_history_file = self.data_dir / "task_history.json"
        self.task_history = self._load_task_history()
        
        # Schedule file
        self.schedule_file = self.data_dir / "schedule.json"
        self.schedule = self._load_schedule()
    
    def _load_task_history(self) -> List[Dict]:
        """Load task history from file"""
        try:
            if self.task_history_file.exists():
                with open(self.task_history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_task_history(self):
        """Save task history to file"""
        try:
            with open(self.task_history_file, 'w') as f:
                json.dump(self.task_history, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving task history: {e}")
    
    def _load_schedule(self) -> Dict:
        """Load schedule from file"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'tasks': [], 'events': []}
    
    def _save_schedule(self):
        """Save schedule to file"""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedule, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving schedule: {e}")
    
    def predict_next_task(self) -> Dict:
        """
        Predict the next task based on historical patterns
        
        Returns:
            Dict with prediction details
        """
        if not self.enable_task_prediction:
            return {'error': 'Task prediction is disabled'}
        
        if not self.task_history:
            return {
                'prediction': 'No task history available',
                'confidence': 0.0,
                'suggestion': 'Start logging tasks to enable predictions'
            }
        
        try:
            # Analyze patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().strftime('%A')
            
            # Find tasks done at similar times
            similar_tasks = []
            for task in self.task_history[-50:]:  # Last 50 tasks
                task_time = datetime.fromisoformat(task.get('timestamp', ''))
                if abs(task_time.hour - current_hour) <= 1:
                    similar_tasks.append(task)
            
            if similar_tasks:
                # Find most common task
                task_counts = {}
                for task in similar_tasks:
                    task_name = task.get('task_name', 'Unknown')
                    task_counts[task_name] = task_counts.get(task_name, 0) + 1
                
                most_common = max(task_counts.items(), key=lambda x: x[1])
                confidence = most_common[1] / len(similar_tasks)
                
                return {
                    'prediction': most_common[0],
                    'confidence': confidence,
                    'time': f'{current_hour}:00',
                    'day': current_day,
                    'based_on': f'{most_common[1]} similar occurrences'
                }
            else:
                return {
                    'prediction': 'No pattern found for current time',
                    'confidence': 0.0,
                    'suggestion': 'Continue logging tasks to improve predictions'
                }
        
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def create_smart_reminder(self, task: str, priority: str = 'medium', deadline: Optional[str] = None, context: Optional[Dict] = None) -> Dict:
        """
        Create an AI-powered smart reminder with optimal timing
        
        Args:
            task: Task description
            priority: Priority level (high, medium, low)
            deadline: Optional deadline in ISO format
            context: Additional context
        
        Returns:
            Dict with reminder details
        """
        if not self.enable_smart_reminders:
            return {'error': 'Smart reminders are disabled'}
        
        try:
            context = context or {}
            priority = priority or context.get('priority', 'medium')
            deadline = deadline or context.get('deadline')
            
            # Analyze task history for optimal reminder time
            current_hour = datetime.now().hour
            
            # Determine optimal reminder time based on priority
            if priority == 'high':
                reminder_advance = timedelta(hours=2)
            elif priority == 'low':
                reminder_advance = timedelta(hours=6)
            else:
                reminder_advance = timedelta(hours=4)
            
            # Calculate reminder time
            if deadline:
                try:
                    deadline_dt = datetime.fromisoformat(deadline)
                    reminder_time = deadline_dt - reminder_advance
                except:
                    reminder_time = datetime.now() + timedelta(hours=1)
            else:
                # Default to next productive hour
                reminder_time = datetime.now() + timedelta(hours=1)
            
            reminder = {
                'task': task,
                'priority': priority,
                'reminder_time': reminder_time.isoformat(),
                'deadline': deadline,
                'created_at': datetime.now().isoformat(),
                'smart': True
            }
            
            # Add to schedule
            self.schedule['tasks'].append(reminder)
            self._save_schedule()
            
            return {
                'status': 'created',
                'task': task,
                'reminder_time': reminder_time.strftime('%I:%M %p on %B %d'),
                'priority': priority,
                'message': f"Smart reminder set for {reminder_time.strftime('%I:%M %p')}"
            }
        
        except Exception as e:
            return {'error': f'Smart reminder creation failed: {str(e)}'}
    
    def optimize_schedule(self) -> Dict:
        """
        Optimize schedule based on task priorities, deadlines, and patterns
        
        Returns:
            Dict with optimized schedule
        """
        if not self.enable_schedule_optimization:
            return {'error': 'Schedule optimization is disabled'}
        
        try:
            tasks = self.schedule.get('tasks', [])
            
            if not tasks:
                return {
                    'status': 'no_tasks',
                    'message': 'No tasks to optimize'
                }
            
            # Sort tasks by priority and deadline
            def task_priority_score(task):
                score = 0
                
                # Priority scoring
                priority = task.get('priority', 'medium')
                if priority == 'high':
                    score += 100
                elif priority == 'medium':
                    score += 50
                
                # Deadline scoring (sooner = higher score)
                deadline = task.get('deadline')
                if deadline:
                    try:
                        deadline_dt = datetime.fromisoformat(deadline)
                        hours_until = (deadline_dt - datetime.now()).total_seconds() / 3600
                        score += max(0, 100 - hours_until)
                    except:
                        pass
                
                return score
            
            # Sort tasks
            optimized_tasks = sorted(tasks, key=task_priority_score, reverse=True)
            
            # Assign time slots
            current_time = datetime.now()
            scheduled_tasks = []
            
            for i, task in enumerate(optimized_tasks):
                # Allocate time slot (default: 1 hour per task)
                start_time = current_time + timedelta(hours=i)
                end_time = start_time + timedelta(hours=1)
                
                scheduled_tasks.append({
                    'task': task.get('task', 'Unknown'),
                    'priority': task.get('priority', 'medium'),
                    'start_time': start_time.strftime('%I:%M %p'),
                    'end_time': end_time.strftime('%I:%M %p'),
                    'duration': '1 hour'
                })
            
            # Save optimized schedule
            self.schedule['optimized'] = scheduled_tasks
            self.schedule['last_optimized'] = datetime.now().isoformat()
            self._save_schedule()
            
            return {
                'status': 'optimized',
                'tasks_count': len(scheduled_tasks),
                'schedule': scheduled_tasks,
                'message': f'Optimized {len(scheduled_tasks)} tasks'
            }
        
        except Exception as e:
            return {'error': f'Schedule optimization failed: {str(e)}'}
    
    def log_task(self, task_name: str, duration: Optional[int] = None, category: Optional[str] = None):
        """
        Log a completed task for pattern analysis
        
        Args:
            task_name: Name of the task
            duration: Duration in minutes
            category: Task category
        """
        task_entry = {
            'task_name': task_name,
            'timestamp': datetime.now().isoformat(),
            'duration_minutes': duration,
            'category': category,
            'hour': datetime.now().hour,
            'day': datetime.now().strftime('%A')
        }
        
        self.task_history.append(task_entry)
        self._save_task_history()
    
    def execute(self, command: str) -> str:
        """Main execution method"""
        command_lower = command.lower().strip()
        
        # Task prediction
        if 'predict' in command_lower and 'task' in command_lower:
            result = self.predict_next_task()
            if 'error' in result:
                return result['error']
            return f"Task Prediction:\n  Next task: {result.get('prediction')}\n  Confidence: {result.get('confidence', 0):.1%}\n  {result.get('suggestion', '')}"
        
        # Smart reminder
        elif 'smart reminder' in command_lower or 'intelligent reminder' in command_lower:
            # Extract task from command
            task = command
            for prefix in ['smart reminder', 'intelligent reminder', 'create smart reminder']:
                if prefix in command_lower:
                    task = command[command_lower.index(prefix) + len(prefix):].strip()
                    break
            
            if task and task != command:
                result = self.create_smart_reminder(task)
                if 'error' in result:
                    return result['error']
                return f"Smart Reminder Created:\n  Task: {result['task']}\n  Time: {result['reminder_time']}\n  Priority: {result['priority']}"
            else:
                return "Please specify a task for the smart reminder"
        
        # Schedule optimization
        elif 'optimize schedule' in command_lower or 'optimize my schedule' in command_lower:
            result = self.optimize_schedule()
            if 'error' in result:
                return result['error']
            if result['status'] == 'no_tasks':
                return result['message']
            
            schedule_text = f"Optimized Schedule ({result['tasks_count']} tasks):\n"
            for task in result['schedule'][:5]:  # Show first 5
                schedule_text += f"  {task['start_time']}-{task['end_time']}: {task['task']} [{task['priority']}]\n"
            
            return schedule_text
        
        else:
            return self._help_message()
    
    def _help_message(self) -> str:
        """Return help message"""
        return """AI Productivity Commands:
🔮 Predict: 'predict next task'
🧠 Smart Reminder: 'smart reminder [task]'
📅 Optimize: 'optimize schedule'

Examples:
  - predict next task
  - smart reminder finish report
  - optimize my schedule"""
