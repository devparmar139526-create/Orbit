"""
IoT device control via MQTT or HTTP
Supports smart lights, relays, sensors, etc.
"""

import requests
from typing import Optional, Dict

class IoTAction:
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize IoT controller
        
        config example:
        {
            'mqtt_broker': 'localhost',
            'mqtt_port': 1883,
            'devices': {
                'living_room_light': {
                    'type': 'http',
                    'on_url': 'http://192.168.1.100/on',
                    'off_url': 'http://192.168.1.100/off'
                }
            }
        }
        """
        self.config = config or {}
        self.devices = self.config.get('devices', {})
        self.mqtt_client = None
        
        # Initialize MQTT if configured
        if 'mqtt_broker' in self.config:
            self._init_mqtt()
    
    def _init_mqtt(self):
        """Initialize MQTT client (optional)"""
        try:
            import paho.mqtt.client as mqtt
            
            broker = self.config.get('mqtt_broker', 'localhost')
            port = self.config.get('mqtt_port', 1883)
            
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
            
            print(f"✅ Connected to MQTT broker at {broker}:{port}")
        except ImportError:
            print("⚠️  paho-mqtt not installed. MQTT features disabled.")
            print("   Install with: pip install paho-mqtt")
        except Exception as e:
            print(f"⚠️  MQTT connection failed: {e}")
    
    def control_device(self, device_name: str, action: str) -> str:
        """Control a device"""
        device_name = device_name.lower().replace(' ', '_')
        
        if device_name not in self.devices:
            available = ', '.join(self.devices.keys()) if self.devices else 'None'
            return f"Device '{device_name}' not found. Available devices: {available}"
        
        device = self.devices[device_name]
        device_type = device.get('type', 'http')
        
        if device_type == 'http':
            return self._http_control(device, action)
        elif device_type == 'mqtt':
            return self._mqtt_control(device, action)
        else:
            return f"Unsupported device type: {device_type}"
    
    def _http_control(self, device: Dict, action: str) -> str:
        """Control device via HTTP"""
        action = action.lower()
        
        if action in ['on', 'turn on', 'enable']:
            url = device.get('on_url')
        elif action in ['off', 'turn off', 'disable']:
            url = device.get('off_url')
        else:
            return f"Unknown action: {action}"
        
        if not url:
            return f"Action '{action}' not configured for this device"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"Device turned {action} successfully"
            else:
                return f"Device responded with status {response.status_code}"
        except requests.exceptions.Timeout:
            return "Device did not respond (timeout)"
        except requests.exceptions.ConnectionError:
            return "Cannot connect to device"
        except Exception as e:
            return f"Error controlling device: {str(e)}"
    
    def _mqtt_control(self, device: Dict, action: str) -> str:
        """Control device via MQTT"""
        if not self.mqtt_client:
            return "MQTT not configured"
        
        topic = device.get('topic')
        if not topic:
            return "MQTT topic not configured for device"
        
        action = action.lower()
        
        if action in ['on', 'turn on', 'enable']:
            payload = device.get('on_payload', 'ON')
        elif action in ['off', 'turn off', 'disable']:
            payload = device.get('off_payload', 'OFF')
        else:
            return f"Unknown action: {action}"
        
        try:
            self.mqtt_client.publish(topic, payload)
            return f"Command sent to device via MQTT"
        except Exception as e:
            return f"MQTT error: {str(e)}"
    
    def add_device(self, name: str, config: Dict):
        """Add a new device configuration"""
        self.devices[name] = config
        return f"Device '{name}' added successfully"
    
    def list_devices(self) -> str:
        """List all configured devices"""
        if not self.devices:
            return "No devices configured"
        
        device_list = []
        for name, config in self.devices.items():
            device_type = config.get('type', 'http')
            device_list.append(f"- {name} ({device_type})")
        
        return "Configured devices:\n" + "\n".join(device_list)
    
    def disconnect(self):
        """Disconnect MQTT client"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()