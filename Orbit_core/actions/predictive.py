"""
Predictive Assistance - Proactive task detection and suggestions
Detects likely user needs and surfaces contextual suggestions
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

class PredictiveAssistant:
    def __init__(self, llm_client=None, smart_home=None):
        self.llm = llm_client
        self.smart_home = smart_home
        
        # Data sources
        self.device_logs = {}
        self.task_history = []
        self.user_preferences = {
            'enabled': True,
            'sensitivity': 'medium',  # low, medium, high
            'auto_execute': False,
            'opt_in_sources': {
                'calendar': True,
                'emails': True,
                'devices': True,
                'location': True
            }
        }
        
        # Suggestion cache
        self.suggestions = []
        self.suggestion_history = []
    
    # ==================== PREDICTION GENERATION ====================
    
    def generate_predictions(self) -> List[Dict]:
        """Generate predictions from all data sources"""
        if not self.user_preferences['enabled']:
            return []
        
        candidates = []
        
        # Rule-based predictions (quick wins)
        candidates.extend(self._rule_based_predictions())
        
        # ML-based predictions (optional)
        if self.llm:
            candidates.extend(self._ml_predictions())
        
        # Rank and phrase suggestions
        ranked = self._rank_suggestions(candidates)
        
        # Store for history
        self.suggestions = ranked
        
        return ranked
    
    def _rule_based_predictions(self) -> List[Dict]:
        """Generate predictions using simple rules"""
        predictions = []
        now = datetime.now()
        
        # Laundry prediction
        laundry_pred = self._predict_laundry(now)
        if laundry_pred:
            predictions.append(laundry_pred)
        
        # Grocery prediction
        grocery_pred = self._predict_grocery(now)
        if grocery_pred:
            predictions.append(grocery_pred)
        
        # Morning routine prediction
        morning_pred = self._predict_morning_routine(now)
        if morning_pred:
            predictions.append(morning_pred)
        
        # Device maintenance prediction
        device_pred = self._predict_device_maintenance(now)
        if device_pred:
            predictions.append(device_pred)
        
        # Schedule conflict prediction
        conflict_pred = self._predict_schedule_conflicts(now)
        if conflict_pred:
            predictions.append(conflict_pred)
        
        return predictions
    
    def _predict_laundry(self, now: datetime) -> Optional[Dict]:
        """Predict when laundry should be done"""
        # Check last laundry run
        last_run = self._get_last_task_run('laundry')
        
        if not last_run:
            return None
        
        days_since = (now - last_run).days
        
        # Rule: suggest laundry after 4+ days
        if days_since >= 4:
            # Check if washer is available
            washer_available = self._check_device_available('washer_01')
            
            if washer_available:
                return {
                    'suggestion_id': f"sug_{now.strftime('%Y%m%d_%H%M%S')}_laundry",
                    'type': 'laundry',
                    'confidence': min(0.85, 0.6 + (days_since * 0.05)),
                    'reason': f"Last laundry run: {days_since} days ago. Washer is available.",
                    'action': {
                        'label': 'Start washing machine',
                        'command': {
                            'device_id': 'washer_01',
                            'api': 'start_cycle',
                            'params': {'mode': 'auto'}
                        }
                    },
                    'timestamp': now.isoformat()
                }
        
        return None
    
    def _predict_grocery(self, now: datetime) -> Optional[Dict]:
        """Predict when grocery shopping is needed"""
        # Check grocery inventory (if tracked)
        low_items = self._check_inventory_low()
        
        if low_items:
            return {
                'suggestion_id': f"sug_{now.strftime('%Y%m%d_%H%M%S')}_grocery",
                'type': 'grocery',
                'confidence': 0.75,
                'reason': f"Low on: {', '.join(low_items[:3])}",
                'action': {
                    'label': 'Create shopping list',
                    'command': {
                        'type': 'task',
                        'action': 'create_shopping_list',
                        'items': low_items
                    }
                },
                'timestamp': now.isoformat()
            }
        
        return None
    
    def _predict_morning_routine(self, now: datetime) -> Optional[Dict]:
        """Predict morning routine trigger"""
        hour = now.hour
        weekday = now.weekday()
        
        # Weekday morning (7-9 AM)
        if weekday < 5 and 7 <= hour < 9:
            # Check if routine already executed today
            if not self._routine_executed_today('morning'):
                return {
                    'suggestion_id': f"sug_{now.strftime('%Y%m%d_%H%M%S')}_morning",
                    'type': 'routine',
                    'confidence': 0.90,
                    'reason': f"It's {now.strftime('%I:%M %p')} on a weekday. Time for your morning routine?",
                    'action': {
                        'label': 'Start morning routine',
                        'command': {
                            'type': 'routine',
                            'routine': 'good_morning'
                        }
                    },
                    'timestamp': now.isoformat()
                }
        
        return None
    
    def _predict_device_maintenance(self, now: datetime) -> Optional[Dict]:
        """Predict device maintenance needs"""
        # Check device usage patterns
        for device_id, logs in self.device_logs.items():
            if not logs:
                continue
            
            # Check if device hasn't been used in a while
            last_use = logs[-1].get('timestamp')
            if last_use:
                last_use_dt = datetime.fromisoformat(last_use)
                days_unused = (now - last_use_dt).days
                
                if days_unused > 30:
                    return {
                        'suggestion_id': f"sug_{now.strftime('%Y%m%d_%H%M%S')}_maint",
                        'type': 'maintenance',
                        'confidence': 0.70,
                        'reason': f"{device_id} hasn't been used in {days_unused} days. Check if it needs maintenance?",
                        'action': {
                            'label': 'Add to maintenance checklist',
                            'command': {
                                'type': 'task',
                                'action': 'add_maintenance',
                                'device': device_id
                            }
                        },
                        'timestamp': now.isoformat()
                    }
        
        return None
    
    def _predict_schedule_conflicts(self, now: datetime) -> Optional[Dict]:
        """Predict upcoming schedule conflicts"""
        # This would integrate with calendar API
        # For now, return None (requires calendar integration)
        return None
    
    def _ml_predictions(self) -> List[Dict]:
        """Generate ML-based predictions using LLM"""
        if not self.llm:
            return []
        
        # Prepare context for LLM
        context = {
            'current_time': datetime.now().isoformat(),
            'recent_tasks': self.task_history[-10:],
            'device_status': self._get_device_summary(),
            'day_of_week': datetime.now().strftime('%A')
        }
        
        # LLM prompt
        prompt = f"""Given this context, suggest up to 3 proactive tasks the user might need:

Context: {json.dumps(context, indent=2)}

Generate suggestions in JSON format:
[{{
    "type": "task_type",
    "reason": "brief explanation",
    "action_label": "what to do",
    "confidence": 0.0-1.0
}}]

Focus on: household tasks, device management, routines, and productivity."""
        
        try:
            response = self.llm.generate(prompt)
            # Parse JSON from response
            suggestions = self._parse_llm_suggestions(response)
            return suggestions
        except Exception as e:
            print(f"ML prediction error: {e}")
            return []
    
    def _rank_suggestions(self, candidates: List[Dict]) -> List[Dict]:
        """Rank suggestions by confidence and relevance"""
        # Apply sensitivity filter
        sensitivity_thresholds = {
            'low': 0.9,
            'medium': 0.7,
            'high': 0.5
        }
        
        threshold = sensitivity_thresholds.get(
            self.user_preferences['sensitivity'],
            0.7
        )
        
        # Filter by threshold
        filtered = [c for c in candidates if c.get('confidence', 0) >= threshold]
        
        # Sort by confidence
        ranked = sorted(filtered, key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Limit to top 3
        return ranked[:3]
    
    # ==================== SUGGESTION EXECUTION ====================
    
    def confirm_suggestion(self, suggestion_id: str, user_response: str) -> str:
        """Handle user confirmation of suggestion"""
        # Find suggestion
        suggestion = next(
            (s for s in self.suggestions if s['suggestion_id'] == suggestion_id),
            None
        )
        
        if not suggestion:
            return "Suggestion not found"
        
        # Record in history
        self.suggestion_history.append({
            'suggestion': suggestion,
            'response': user_response,
            'timestamp': datetime.now().isoformat()
        })
        
        if user_response.lower() in ['yes', 'accept', 'confirm', 'do it']:
            return self._execute_suggestion(suggestion)
        
        elif user_response.lower() in ['snooze', 'later', 'postpone']:
            return self._snooze_suggestion(suggestion)
        
        elif user_response.lower() in ['no', 'decline', 'dismiss', 'cancel']:
            return "Suggestion dismissed"
        
        else:
            return "I didn't understand. Please say 'yes', 'snooze', or 'no'"
    
    def _execute_suggestion(self, suggestion: Dict) -> str:
        """Execute the suggested action"""
        action = suggestion.get('action', {})
        command = action.get('command', {})
        
        if command.get('type') == 'routine':
            # Execute routine
            routine_name = command.get('routine')
            if self.smart_home:
                return self.smart_home.execute_routine(routine_name)
            return f"Routine '{routine_name}' would be executed"
        
        elif command.get('device_id'):
            # Control device
            if self.smart_home and self.smart_home.iot:
                device_id = command['device_id']
                return self.smart_home.iot.control_device(device_id, command.get('api', 'on'))
            return f"Device command would be executed"
        
        elif command.get('type') == 'task':
            # Create task
            return f"Task created: {action.get('label')}"
        
        return "Action executed successfully"
    
    def _snooze_suggestion(self, suggestion: Dict, minutes: int = 60) -> str:
        """Snooze suggestion for later"""
        # Would integrate with scheduler
        return f"Suggestion snoozed for {minutes} minutes"
    
    # ==================== USER PREFERENCES ====================
    
    def update_preferences(self, preferences: Dict) -> str:
        """Update user preferences"""
        self.user_preferences.update(preferences)
        return "Preferences updated"
    
    def get_preferences(self) -> Dict:
        """Get current preferences"""
        return self.user_preferences
    
    def toggle_source(self, source: str, enabled: bool) -> str:
        """Enable/disable a data source"""
        if source in self.user_preferences['opt_in_sources']:
            self.user_preferences['opt_in_sources'][source] = enabled
            return f"{source} {'enabled' if enabled else 'disabled'}"
        return f"Unknown source: {source}"
    
    # ==================== DATA LOGGING ====================
    
    def log_device_event(self, device_id: str, event: Dict):
        """Log device event for prediction"""
        if device_id not in self.device_logs:
            self.device_logs[device_id] = []
        
        event['timestamp'] = datetime.now().isoformat()
        self.device_logs[device_id].append(event)
        
        # Keep only last 100 events per device
        self.device_logs[device_id] = self.device_logs[device_id][-100:]
    
    def log_task_completion(self, task_type: str, details: Dict = None):
        """Log task completion for learning"""
        self.task_history.append({
            'type': task_type,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        })
        
        # Keep only last 1000 tasks
        self.task_history = self.task_history[-1000:]
    
    # ==================== HISTORY & ANALYTICS ====================
    
    def get_suggestion_history(self, limit: int = 20) -> List[Dict]:
        """Get suggestion history"""
        return self.suggestion_history[-limit:]
    
    def get_acceptance_rate(self) -> Dict:
        """Get suggestion acceptance statistics"""
        if not self.suggestion_history:
            return {'acceptance_rate': 0, 'total_suggestions': 0}
        
        accepted = sum(
            1 for h in self.suggestion_history
            if h['response'].lower() in ['yes', 'accept', 'confirm', 'do it']
        )
        
        total = len(self.suggestion_history)
        
        return {
            'acceptance_rate': (accepted / total) * 100,
            'accepted': accepted,
            'total_suggestions': total,
            'snoozed': sum(1 for h in self.suggestion_history if 'snooze' in h['response'].lower()),
            'declined': sum(1 for h in self.suggestion_history if h['response'].lower() in ['no', 'decline', 'dismiss'])
        }
    
    def export_analytics(self, filepath: str) -> str:
        """Export analytics to file"""
        analytics = {
            'acceptance_rate': self.get_acceptance_rate(),
            'history': self.get_suggestion_history(100),
            'preferences': self.user_preferences
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analytics, f, indent=2)
            return f"Analytics exported to {filepath}"
        except Exception as e:
            return f"Export failed: {str(e)}"
    
    # ==================== HELPER METHODS ====================
    
    def _get_last_task_run(self, task_type: str) -> Optional[datetime]:
        """Get last time a task was run"""
        for task in reversed(self.task_history):
            if task['type'] == task_type:
                return datetime.fromisoformat(task['timestamp'])
        return None
    
    def _check_device_available(self, device_id: str) -> bool:
        """Check if device is available"""
        # Would check device status via IoT
        return True
    
    def _check_inventory_low(self) -> List[str]:
        """Check for low inventory items"""
        # Would integrate with inventory system
        # For now, return empty list
        return []
    
    def _routine_executed_today(self, routine_name: str) -> bool:
        """Check if routine was executed today"""
        today = datetime.now().date()
        
        for task in reversed(self.task_history):
            if task['type'] == 'routine' and task.get('details', {}).get('name') == routine_name:
                task_date = datetime.fromisoformat(task['timestamp']).date()
                if task_date == today:
                    return True
        
        return False
    
    def _get_device_summary(self) -> Dict:
        """Get summary of device status"""
        summary = {}
        for device_id, logs in self.device_logs.items():
            if logs:
                summary[device_id] = {
                    'last_used': logs[-1].get('timestamp'),
                    'usage_count': len(logs)
                }
        return summary
    
    def _parse_llm_suggestions(self, response: str) -> List[Dict]:
        """Parse LLM response into suggestions"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                
                # Convert to full suggestion format
                full_suggestions = []
                for i, sug in enumerate(suggestions):
                    full_suggestions.append({
                        'suggestion_id': f"sug_llm_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                        'type': sug.get('type', 'general'),
                        'confidence': sug.get('confidence', 0.7),
                        'reason': sug.get('reason', ''),
                        'action': {
                            'label': sug.get('action_label', ''),
                            'command': {}
                        },
                        'timestamp': datetime.now().isoformat()
                    })
                
                return full_suggestions
        except Exception as e:
            print(f"Failed to parse LLM suggestions: {e}")
        
        return []