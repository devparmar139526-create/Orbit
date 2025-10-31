"""
Event Bus for pub-sub communication between modules
"""

from typing import Callable, Dict, List
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data=None):
        """Publish an event to all subscribers"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
    
    def clear(self, event_type: str = None):
        """Clear subscribers for an event type or all"""
        if event_type:
            self.subscribers[event_type].clear()
        else:
            self.subscribers.clear()

# Example usage:
# bus = EventBus()
# 
# def on_task_complete(data):
#     print(f"Task completed: {data}")
# 
# bus.subscribe("task.complete", on_task_complete)
# bus.publish("task.complete", {"task_id": 1, "status": "done"})