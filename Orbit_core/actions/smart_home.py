data:
            return "No sensors configured"
        
        result = "Sensor Readings:\n"
        for name, data in self.sensor_data.items():
            value = data['last_reading']
            timestamp = data['timestamp']
            result += f"- {name}: {value} (updated: {timestamp})\n"
        
        return result
    
    # ==================== AUTOMATION RULES ====================
    
    def create_automation_rule(self, name: str, condition: Dict, action: Dict) -> str:
        """
        Create automation rule
        
        Example:
        create_automation_rule(
            'night_light',
            condition={'sensor': 'motion_sensor', 'value': True, 'time_range': ('22:00', '06:00')},
            action={'device': 'hallway_light', 'action': 'on', 'duration': 300}
        )
        """
        rule = {
            'name': name,
            'condition': condition,
            'action': action,
            'enabled': True
        }
        
        self.automation_rules.append(rule)
        return f"Automation rule '{name}' created"
    
    def check_automation_rules(self) -> List[str]:
        """Check and execute automation rules"""
        triggered_actions = []
        current_time = datetime.now().time()
        
        for rule in self.automation_rules:
            if not rule['enabled']:
                continue
            
            condition = rule['condition']
            
            # Check sensor condition
            if 'sensor' in condition:
                sensor_name = condition['sensor']
                if sensor_name in self.sensor_data:
                    sensor_value = self.sensor_data[sensor_name]['last_reading']
                    
                    # Check if condition met
                    condition_met = False
                    
                    if 'value' in condition:
                        if sensor_value == condition['value']:
                            condition_met = True
                    elif 'threshold' in condition:
                        if sensor_value > condition['threshold']:
                            condition_met = True
                    
                    # Check time range
                    if condition_met and 'time_range' in condition:
                        start, end = condition['time_range']
                        start_time = datetime.strptime(start, '%H:%M').time()
                        end_time = datetime.strptime(end, '%H:%M').time()
                        
                        if not (start_time <= current_time <= end_time):
                            condition_met = False
                    
                    # Execute action if condition met
                    if condition_met:
                        action = rule['action']
                        result = self.iot.control_device(action['device'], action['action'])
                        triggered_actions.append(f"{rule['name']}: {result}")
        
        return triggered_actions
    
    def disable_automation_rule(self, name: str) -> str:
        """Disable an automation rule"""
        for rule in self.automation_rules:
            if rule['name'] == name:
                rule['enabled'] = False
                return f"Rule '{name}' disabled"
        
        return f"Rule '{name}' not found"
    
    # ==================== SCENE MANAGEMENT ====================
    
    def create_scene(self, name: str, device_states: Dict) -> str:
        """
        Create a scene (snapshot of device states)
        
        Example:
        create_scene('movie_time', {
            'living_room_light': {'brightness': 20},
            'tv': {'power': 'on'},
            'blinds': {'position': 'closed'}
        })
        """
        self.routines[f"scene_{name}"] = [
            {'device': device, 'action': 'on', 'params': params}
            for device, params in device_states.items()
        ]
        
        return f"Scene '{name}' created"
    
    def activate_scene(self, name: str) -> str:
        """Activate a scene"""
        return self.execute_routine(f"scene_{name}")
    
    # ==================== ENERGY MANAGEMENT ====================
    
    def energy_saving_mode(self) -> str:
        """Enable energy saving mode"""
        actions = [
            {'device': 'ac', 'action': 'off'},
            {'device': 'heater', 'action': 'off'},
            {'device': 'living_room_light', 'action': 'off'},
            {'device': 'kitchen_light', 'action': 'off'}
        ]
        
        return self._execute_action_list(actions, "Energy Saving")
    
    def get_energy_usage(self) -> str:
        """Get energy usage from smart plugs"""
        # This would query smart plugs with energy monitoring
        energy_devices = ['smart_plug_1', 'smart_plug_2']
        
        total_power = 0
        result = "Energy Usage:\n"
        
        for device in energy_devices:
            if device in self.sensor_data:
                power = self.sensor_data[device].get('power', 0)
                total_power += power
                result += f"- {device}: {power}W\n"
        
        result += f"\nTotal: {total_power}W"
        return result
    
    # ==================== CLIMATE CONTROL ====================
    
    def set_temperature(self, target_temp: float, room: str = 'living_room') -> str:
        """Set target temperature"""
        device = f"{room}_thermostat"
        
        # This would send temperature setpoint to smart thermostat
        return f"Setting {room} temperature to {target_temp}°C"
    
    def auto_climate_control(self) -> str:
        """Automatic climate control based on sensors"""
        if 'temperature_sensor' not in self.sensor_data:
            return "Temperature sensor not available"
        
        current_temp = self.sensor_data['temperature_sensor']['last_reading']
        
        if current_temp > 26:
            return self.iot.control_device('ac', 'on')
        elif current_temp < 18:
            return self.iot.control_device('heater', 'on')
        else:
            return "Temperature is comfortable, no action needed"
    
    # ==================== SECURITY FEATURES ====================
    
    def arm_security_system(self) -> str:
        """Arm security system"""
        actions = [
            {'device': 'security_system', 'action': 'on'},
            {'device': 'motion_sensors', 'action': 'on'},
            {'device': 'door_sensors', 'action': 'on'}
        ]
        
        return self._execute_action_list(actions, "Security System Armed")
    
    def disarm_security_system(self) -> str:
        """Disarm security system"""
        return self.iot.control_device('security_system', 'off')
    
    def check_security_status(self) -> str:
        """Check status of all security devices"""
        security_devices = ['door_lock', 'window_sensors', 'motion_sensors', 'cameras']
        
        status = "Security Status:\n"
        for device in security_devices:
            # This would query device status
            status += f"- {device}: [Status would be queried]\n"
        
        return status
    
    # ==================== ALERTS ====================
    
    def setup_alert(self, sensor: str, condition: str, threshold: float, notification_method: str) -> str:
        """Setup alert for sensor threshold"""
        alert = {
            'sensor': sensor,
            'condition': condition,  # 'above', 'below', 'equals'
            'threshold': threshold,
            'notification': notification_method
        }
        
        return f"Alert configured for {sensor} {condition} {threshold}"
    
    def check_alerts(self) -> List[str]:
        """Check if any alerts should be triggered"""
        alerts = []
        
        # Example: Temperature too high
        if 'temperature_sensor' in self.sensor_data:
            temp = self.sensor_data['temperature_sensor']['last_reading']
            if temp > 30:
                alerts.append(f"⚠️ High temperature alert: {temp}°C")
        
        # Example: Motion detected when armed
        if 'motion_sensor' in self.sensor_data:
            motion = self.sensor_data['motion_sensor']['last_reading']
            if motion:
                alerts.append("⚠️ Motion detected!")
        
        return alerts
    
    # ==================== DEVICE GROUPS ====================
    
    def create_device_group(self, group_name: str, devices: List[str]) -> str:
        """Create a group of devices for batch control"""
        self.iot.devices[group_name] = {
            'type': 'group',
            'devices': devices
        }
        
        return f"Device group '{group_name}' created with {len(devices)} devices"
    
    def control_group(self, group_name: str, action: str) -> str:
        """Control all devices in a group"""
        if group_name not in self.iot.devices:
            return f"Group '{group_name}' not found"
        
        group = self.iot.devices[group_name]
        
        if group.get('type') != 'group':
            return f"{group_name} is not a group"
        
        results = []
        for device in group['devices']:
            result = self.iot.control_device(device, action)
            results.append(f"{device}: {result}")
        
     """
Smart Home Advanced - Routines, Sensors, Automation
Step 3: Smart Home / IoT Features
"""

from typing import Dict, List, Optional
from datetime import datetime, time
import json

class SmartHomeManager:
    def __init__(self, iot_action, scheduler=None):
        """
        Initialize smart home manager
        
        Args:
            iot_action: Instance of IoTAction for device control
            scheduler: Optional scheduler for timed routines
        """
        self.iot = iot_action
        self.scheduler = scheduler
        self.routines = {}
        self.sensor_data = {}
        self.automation_rules = []
    
    # ==================== ROUTINES ====================
    
    def create_routine(self, name: str, actions: List[Dict]) -> str:
        """
        Create a routine (sequence of actions)
        
        Example:
        create_routine('morning', [
            {'device': 'bedroom_light', 'action': 'on'},
            {'device': 'coffee_maker', 'action': 'on'},
            {'wait': 5},
            {'device': 'blinds', 'action': 'open'}
        ])
        """
        self.routines[name] = actions
        return f"Routine '{name}' created with {len(actions)} actions"
    
    def execute_routine(self, name: str) -> str:
        """Execute a predefined routine"""
        if name not in self.routines:
            return f"Routine '{name}' not found. Available: {', '.join(self.routines.keys())}"
        
        import time
        results = []
        
        for action in self.routines[name]:
            if 'wait' in action:
                time.sleep(action['wait'])
                results.append(f"Waited {action['wait']}s")
            elif 'device' in action:
                result = self.iot.control_device(action['device'], action['action'])
                results.append(result)
        
        return f"Routine '{name}' executed:\n" + "\n".join(results)
    
    def schedule_routine(self, name: str, time_str: str) -> str:
        """Schedule a routine to run at specific time"""
        if not self.scheduler:
            return "Scheduler not available"
        
        # This would integrate with the scheduler service
        return f"Routine '{name}' scheduled for {time_str}"
    
    # ==================== PRE-DEFINED ROUTINES ====================
    
    def good_morning_routine(self) -> str:
        """Execute morning routine"""
        routine = [
            {'device': 'bedroom_light', 'action': 'on'},
            {'device': 'blinds', 'action': 'open'},
            {'wait': 2},
            {'device': 'coffee_maker', 'action': 'on'},
            {'device': 'thermostat', 'action': 'on'}  # Set to comfortable temp
        ]
        
        return self._execute_action_list(routine, "Good Morning")
    
    def good_night_routine(self) -> str:
        """Execute night routine"""
        routine = [
            {'device': 'living_room_light', 'action': 'off'},
            {'device': 'kitchen_light', 'action': 'off'},
            {'device': 'bedroom_light', 'action': 'on'},  # Dim light
            {'device': 'door_lock', 'action': 'on'},  # Lock
            {'device': 'thermostat', 'action': 'off'},  # Lower temp
            {'device': 'security_system', 'action': 'on'}
        ]
        
        return self._execute_action_list(routine, "Good Night")
    
    def leaving_home_routine(self) -> str:
        """Execute leaving home routine"""
        routine = [
            {'device': 'all_lights', 'action': 'off'},
            {'device': 'ac', 'action': 'off'},
            {'device': 'door_lock', 'action': 'on'},
            {'device': 'security_system', 'action': 'on'}
        ]
        
        return self._execute_action_list(routine, "Leaving Home")
    
    def arriving_home_routine(self) -> str:
        """Execute arriving home routine"""
        routine = [
            {'device': 'door_lock', 'action': 'off'},
            {'device': 'entry_light', 'action': 'on'},
            {'device': 'ac', 'action': 'on'},
            {'device': 'security_system', 'action': 'off'}
        ]
        
        return self._execute_action_list(routine, "Arriving Home")
    
    def _execute_action_list(self, actions: List[Dict], routine_name: str) -> str:
        """Helper to execute action list"""
        import time
        results = []
        
        for action in actions:
            if 'wait' in action:
                time.sleep(action['wait'])
            elif 'device' in action:
                try:
                    result = self.iot.control_device(action['device'], action['action'])
                    results.append(f"✓ {action['device']}: {action['action']}")
                except Exception as e:
                    results.append(f"✗ {action['device']}: {str(e)}")
        
        return f"{routine_name} routine completed:\n" + "\n".join(results)
    
    # ==================== SENSOR MONITORING ====================
    
    def monitor_sensor(self, sensor_name: str, mqtt_topic: str = None) -> str:
        """Start monitoring a sensor"""
        # This would subscribe to MQTT topics or poll HTTP endpoints
        self.sensor_data[sensor_name] = {
            'topic': mqtt_topic,
            'last_reading': None,
            'timestamp': None
        }
        
        return f"Monitoring sensor: {sensor_name}"
    
    def get_sensor_reading(self, sensor_name: str) -> str:
        """Get latest sensor reading"""
        if sensor_name not in self.sensor_data:
            return f"Sensor '{sensor_name}' not monitored"
        
        data = self.sensor_data[sensor_name]
        
        if data['last_reading'] is None:
            return f"No data available for {sensor_name}"
        
        return f"{sensor_name}: {data['last_reading']} (at {data['timestamp']})"
    
    def update_sensor_reading(self, sensor_name: str, value: float):
        """Update sensor reading (called by MQTT callback)"""
        if sensor_name in self.sensor_data:
            self.sensor_data[sensor_name]['last_reading'] = value
            self.sensor_data[sensor_name]['timestamp'] = datetime.now()
    
    def get_all_sensors(self) -> str:
        """Get all sensor readings"""
        if not self.sensor_