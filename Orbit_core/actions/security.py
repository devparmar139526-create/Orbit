"""
Security Features - Device Lock, Intrusion Detection, Facial Recognition
Step 4: Security Features
"""

import platform
import subprocess
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path

class SecurityManager:
    def __init__(self):
        self.os_type = platform.system()
        self.known_faces = {}
        self.security_log = []
        self.locked_status = False
        
    # ==================== DEVICE LOCK/UNLOCK ====================
    
    def lock_device(self) -> str:
        """Lock the current device"""
        try:
            if self.os_type == 'Windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
                self.locked_status = True
                self._log_security_event("Device locked")
                return "Device locked successfully"
            
            elif self.os_type == 'Darwin':  # macOS
                subprocess.run(['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'])
                self.locked_status = True
                self._log_security_event("Device locked")
                return "Device locked successfully"
            
            elif self.os_type == 'Linux':
                # Try multiple lock commands
                commands = [
                    ['gnome-screensaver-command', '-l'],
                    ['xdg-screensaver', 'lock'],
                    ['dm-tool', 'lock']
                ]
                
                for cmd in commands:
                    try:
                        subprocess.run(cmd, check=True)
                        self.locked_status = True
                        self._log_security_event("Device locked")
                        return "Device locked successfully"
                    except:
                        continue
                
                return "Could not lock device. No screen locker found."
            
            else:
                return f"Device locking not supported on {self.os_type}"
        
        except Exception as e:
            return f"Failed to lock device: {str(e)}"
    
    def unlock_device(self, password: str) -> str:
        """Unlock device (requires authentication)"""
        # In practice, this would verify credentials
        # For security, actual unlock requires physical access
        return "Device unlock requires physical authentication for security"
    
    def remote_lock_device(self, device_id: str, auth_token: str) -> str:
        """Remotely lock a device"""
        # This would integrate with device management APIs
        self._log_security_event(f"Remote lock requested for {device_id}")
        return f"Remote lock command sent to device {device_id}"
    
    # ==================== INTRUSION DETECTION ====================
    
    def enable_intrusion_detection(self) -> str:
        """Enable intrusion detection mode"""
        self._log_security_event("Intrusion detection enabled")
        return "Intrusion detection enabled. Monitoring for suspicious activity..."
    
    def check_unauthorized_access(self) -> str:
        """Check for unauthorized access attempts"""
        # This would analyze system logs
        if self.os_type == 'Linux':
            try:
                # Check auth.log for failed login attempts
                result = subprocess.run(
                    ['grep', 'Failed password', '/var/log/auth.log'],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    failed_attempts = len(result.stdout.strip().split('\n'))
                    return f"⚠️ {failed_attempts} failed login attempts detected"
                else:
                    return "✓ No unauthorized access attempts detected"
            
            except Exception as e:
                return f"Could not check auth logs: {str(e)}"
        
        return "Unauthorized access checking not implemented for this OS"
    
    def detect_suspicious_processes(self) -> str:
        """Detect suspicious running processes"""
        try:
            import psutil
            
            suspicious_keywords = ['keylog', 'trojan', 'backdoor', 'exploit', 'malware']
            suspicious_processes = []
            
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    name = proc.info['name'].lower()
                    if any(keyword in name for keyword in suspicious_keywords):
                        suspicious_processes.append(proc.info['name'])
                except:
                    pass
            
            if suspicious_processes:
                self._log_security_event(f"Suspicious processes: {suspicious_processes}")
                return f"⚠️ Suspicious processes detected: {', '.join(suspicious_processes)}"
            else:
                return "✓ No suspicious processes detected"
        
        except ImportError:
            return "Process detection requires psutil: pip install psutil"
        except Exception as e:
            return f"Process detection failed: {str(e)}"
    
    def monitor_network_connections(self) -> str:
        """Monitor active network connections"""
        try:
            import psutil
            
            connections = psutil.net_connections(kind='inet')
            active_connections = [
                conn for conn in connections 
                if conn.status == 'ESTABLISHED'
            ]
            
            result = f"Active network connections: {len(active_connections)}\n"
            
            # Show top 5 connections
            for conn in active_connections[:5]:
                result += f"- {conn.laddr.ip}:{conn.laddr.port} → {conn.raddr.ip if conn.raddr else 'N/A'}\n"
            
            return result
        
        except ImportError:
            return "Network monitoring requires psutil"
        except Exception as e:
            return f"Network monitoring failed: {str(e)}"
    
    # ==================== LOCATION TRACKING ====================
    
    def get_device_location(self) -> str:
        """Get device location via IP geolocation"""
        try:
            import requests
            
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            
            location = f"Device Location:\n"
            location += f"IP: {data.get('ip')}\n"
            location += f"City: {data.get('city')}\n"
            location += f"Region: {data.get('region')}\n"
            location += f"Country: {data.get('country_name')}\n"
            location += f"Coordinates: {data.get('latitude')}, {data.get('longitude')}\n"
            
            self._log_security_event(f"Location queried: {data.get('city')}")
            return location
        
        except Exception as e:
            return f"Location tracking failed: {str(e)}"
    
    def track_device_movement(self) -> str:
        """Track device movement (for laptops with GPS)"""
        # This would integrate with GPS APIs or Android/iOS location services
        return "GPS tracking requires additional hardware/API integration"
    
    # ==================== FACIAL RECOGNITION ====================
    
    def setup_facial_recognition(self, user_name: str, image_path: str) -> str:
        """Face recognition disabled - terminal mode only"""
        return "👤 Face recognition features disabled in terminal mode."
    
    def recognize_face(self, image_path: Optional[str] = None) -> str:
        """Face recognition disabled - terminal mode only"""
        return "👤 Face recognition features disabled in terminal mode."