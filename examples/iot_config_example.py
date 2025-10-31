"""
IoT Device Configuration Example for orbit

This file shows how to configure smart devices for home automation.
Copy and modify this file to match your setup.
"""

# Example 1: HTTP-based devices (ESP8266/ESP32 with simple web server)
iot_config_http = {
    'devices': {
        # Living room smart light
        'living_room_light': {
            'type': 'http',
            'on_url': 'http://192.168.1.100/on',
            'off_url': 'http://192.168.1.100/off',
            'status_url': 'http://192.168.1.100/status'  # Optional
        },
        
        # Bedroom fan
        'bedroom_fan': {
            'type': 'http',
            'on_url': 'http://192.168.1.101/relay?state=1',
            'off_url': 'http://192.168.1.101/relay?state=0'
        },
        
        # Garage door
        'garage_door': {
            'type': 'http',
            'on_url': 'http://192.168.1.102/open',
            'off_url': 'http://192.168.1.102/close'
        }
    }
}

# Example 2: MQTT-based devices (more advanced IoT setup)
iot_config_mqtt = {
    'mqtt_broker': 'localhost',  # or your MQTT broker IP
    'mqtt_port': 1883,
    'mqtt_username': 'orbit',  # Optional
    'mqtt_password': 'password',  # Optional
    
    'devices': {
        # Smart bulb via MQTT
        'bedroom_light': {
            'type': 'mqtt',
            'topic': 'home/bedroom/light',
            'on_payload': 'ON',
            'off_payload': 'OFF'
        },
        
        # Temperature sensor (read-only)
        'living_room_sensor': {
            'type': 'mqtt',
            'topic': 'home/livingroom/sensor',
            'sensor': True  # Indicates read-only device
        },
        
        # RGB LED strip
        'rgb_strip': {
            'type': 'mqtt',
            'topic': 'home/rgb/command',
            'on_payload': '{"state":"ON"}',
            'off_payload': '{"state":"OFF"}',
            'color_topic': 'home/rgb/color'  # For color control
        }
    }
}

# Example 3: Mixed setup (both HTTP and MQTT)
iot_config_mixed = {
    'mqtt_broker': '192.168.1.50',
    'mqtt_port': 1883,
    
    'devices': {
        # HTTP devices
        'kitchen_light': {
            'type': 'http',
            'on_url': 'http://192.168.1.110/on',
            'off_url': 'http://192.168.1.110/off'
        },
        
        # MQTT devices
        'thermostat': {
            'type': 'mqtt',
            'topic': 'home/thermostat/set',
            'on_payload': '22',  # Set to 22°C
            'off_payload': '18'  # Set to 18°C
        }
    }
}

# ============================================================================
# HOW TO USE THIS CONFIGURATION
# ============================================================================

"""
1. Choose your configuration (http, mqtt, or mixed)

2. Update IP addresses and topics to match your devices

3. In your orbit code, import and use:

   from examples.iot_config_example import iot_config_http
   from Orbit_core.actions.iot import IoTAction
   
   iot = IoTAction(iot_config_http)
   iot.control_device('living_room_light', 'on')

4. Voice commands will work automatically:
   - "Turn on living room light"
   - "Turn off bedroom fan"
   - "Open garage door"

5. To integrate into main orbit, modify source_selector.py to include IoT:
   
   self.iot = IoTAction(iot_config_http)
   
   # In process() method, add IoT intent handling:
   elif intent == 'iot':
       return self._handle_iot(query)
   
   def _handle_iot(self, query):
       # Parse device name and action from query
       # Call self.iot.control_device(device_name, action)
       pass
"""

# ============================================================================
# ARDUINO/ESP8266/ESP32 EXAMPLE CODE
# ============================================================================

"""
Simple ESP8266/ESP32 web server for HTTP control:

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "YourWiFi";
const char* password = "YourPassword";

ESP8266WebServer server(80);
const int relayPin = D1;  // GPIO pin for relay

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  
  server.on("/on", []() {
    digitalWrite(relayPin, HIGH);
    server.send(200, "text/plain", "ON");
  });
  
  server.on("/off", []() {
    digitalWrite(relayPin, LOW);
    server.send(200, "text/plain", "OFF");
  });
  
  server.on("/status", []() {
    String status = digitalRead(relayPin) ? "ON" : "OFF";
    server.send(200, "text/plain", status);
  });
  
  server.begin();
}

void loop() {
  server.handleClient();
}

Find the ESP's IP address in your router and use it in the config!
"""

# ============================================================================
# MQTT SETUP GUIDE
# ============================================================================

"""
Installing Mosquitto MQTT Broker:

Ubuntu/Debian:
  sudo apt-get install mosquitto mosquitto-clients
  sudo systemctl start mosquitto
  sudo systemctl enable mosquitto

macOS:
  brew install mosquitto
  brew services start mosquitto

Windows:
  Download from: https://mosquitto.org/download/

Test MQTT:
  # Subscribe to topic
  mosquitto_sub -h localhost -t "home/test"
  
  # Publish message
  mosquitto_pub -h localhost -t "home/test" -m "Hello"

ESP8266/ESP32 MQTT Client:
  Use PubSubClient library in Arduino IDE
  Connect to your broker and subscribe/publish to topics
  orbit will send commands to the appropriate topics
"""

# ============================================================================
# DEVICE NAMING CONVENTIONS
# ============================================================================

"""
Good device names:
  - living_room_light
  - bedroom_fan
  - kitchen_outlet
  - garage_door

Avoid:
  - light1, light2 (not descriptive)
  - lr_lt (too abbreviated)
  - "living room light" (use underscores, not spaces)

Voice commands work best with descriptive, location-based names!
"""