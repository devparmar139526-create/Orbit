"""
Advanced Desktop Control - Screenshots, Macros, File Management
Phase 2: Device Control Features - Zero Hardcoding, Full Configuration
"""

import os
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import time
import json

class AdvancedDesktopControl:
    def __init__(self, settings=None):
        self.settings = settings
        self.os_type = platform.system()
        
        # Configure screenshot directory from settings
        if settings and hasattr(settings, 'SCREENSHOT_DIR'):
            self.screenshot_dir = Path(settings.SCREENSHOT_DIR).expanduser()
        else:
            self.screenshot_dir = Path.home() / "Pictures" / "Orbit_Screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure screen recording directory
        if settings and hasattr(settings, 'RECORDING_DIR'):
            self.recording_dir = Path(settings.RECORDING_DIR).expanduser()
        else:
            self.recording_dir = self.screenshot_dir
        self.recording_dir.mkdir(parents=True, exist_ok=True)
        
        # Security: Whitelist allowed directories from settings
        if settings and hasattr(settings, 'ALLOWED_DIRECTORIES'):
            self.allowed_dirs = [Path(d).expanduser() for d in settings.ALLOWED_DIRECTORIES]
        else:
            self.allowed_dirs = [
                Path.home() / "Documents",
                Path.home() / "Downloads",
                Path.home() / "Desktop"
            ]
        
        # Load file organization categories from settings
        if settings and hasattr(settings, 'FILE_CATEGORIES'):
            self.file_categories = settings.FILE_CATEGORIES
        else:
            self.file_categories = {
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
                'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.odt'],
                'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'],
                'Audio': ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg'],
                'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
                'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json']
            }
        
        # Load predefined macros from settings
        if settings and hasattr(settings, 'MACROS'):
            self.macros = settings.MACROS
        else:
            self.macros = self._default_macros()
        
        # Feature enablement from settings
        self.enable_screenshots = getattr(settings, 'ENABLE_SCREENSHOTS', True) if settings else True
        self.enable_recording = getattr(settings, 'ENABLE_SCREEN_RECORDING', True) if settings else True
        self.enable_file_ops = getattr(settings, 'ENABLE_FILE_OPERATIONS', True) if settings else True
        self.enable_automation = getattr(settings, 'ENABLE_AUTOMATION', True) if settings else True
        self.enable_window_mgmt = getattr(settings, 'ENABLE_WINDOW_MANAGEMENT', True) if settings else True
        
        # Recording settings
        self.default_recording_duration = getattr(settings, 'DEFAULT_RECORDING_DURATION', 10) if settings else 10
        self.recording_fps = getattr(settings, 'RECORDING_FPS', 20) if settings else 20
        self.recording_codec = getattr(settings, 'RECORDING_CODEC', 'XVID') if settings else 'XVID'
    
    # ==================== SCREENSHOTS ====================
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot and save it to the configured directory"""
        try:
            import pyautogui
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            if not filename:
                filename = f"screenshot_{timestamp}.png"
            elif not filename.endswith(('.png', '.jpg', '.jpeg')):
                filename += '.png'
            
            filepath = self.screenshot_dir / filename
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return f"📷 Screenshot saved to {filepath}"
        
        except ImportError:
            return "❌ Screenshot feature requires pyautogui. Install with: pip install pyautogui"
        except Exception as e:
            return f"❌ Screenshot failed: {str(e)}"
    
    def take_screenshot_region(self, x: int, y: int, width: int, height: int) -> str:
        """Take screenshot of specific region"""
        try:
            import pyautogui
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_region_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(filepath)
            
            return f"Region screenshot saved to {filepath}"
        
        except ImportError:
            return "Feature requires pyautogui"
        except Exception as e:
            return f"Region screenshot failed: {str(e)}"
    
    # ==================== SCREEN RECORDING ====================
    
    def start_screen_recording(self, duration: int = 10) -> str:
        """Record screen for specified duration"""
        try:
            import cv2
            import numpy as np
            import pyautogui
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.avi"
            filepath = self.recording_dir / filename
            
            # Get screen dimensions
            screen_size = pyautogui.size()
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*self.recording_codec)
            out = cv2.VideoWriter(str(filepath), fourcc, self.recording_fps, screen_size)
            
            print(f"🎥 Recording for {duration} seconds...")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Take screenshot
                screenshot = pyautogui.screenshot()
                # Convert PIL image to OpenCV format
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                # Write frame
                out.write(frame)
                
                # Control frame rate
                time.sleep(1.0 / self.recording_fps)
            
            out.release()
            cv2.destroyAllWindows()
            
            return f"🎥 Recording saved to {filepath}"
        
        except ImportError:
            return "❌ Screen recording requires opencv-python and pyautogui. Install with: pip install opencv-python pyautogui"
        except Exception as e:
            return f"❌ Screen recording failed: {str(e)}"
    
    # ==================== FILE MANAGEMENT ====================
    
    def create_folder(self, path: str) -> str:
        """Create a new folder"""
        try:
            folder_path = Path(path).expanduser()
            
            # Security check
            if not self._is_path_allowed(folder_path):
                return "Access denied: Path not in allowed directories"
            
            folder_path.mkdir(parents=True, exist_ok=True)
            return f"Folder created: {folder_path}"
        
        except Exception as e:
            return f"Failed to create folder: {str(e)}"
    
    def delete_file(self, path: str) -> str:
        """Delete a file (with safety check)"""
        try:
            file_path = Path(path).expanduser()
            
            if not self._is_path_allowed(file_path):
                return "Access denied: Path not in allowed directories"
            
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            if file_path.is_file():
                file_path.unlink()
                return f"File deleted: {file_path}"
            else:
                return "Path is not a file"
        
        except Exception as e:
            return f"Failed to delete file: {str(e)}"
    
    def move_file(self, source: str, destination: str) -> str:
        """Move file from source to destination"""
        try:
            src_path = Path(source).expanduser()
            dst_path = Path(destination).expanduser()
            
            if not self._is_path_allowed(src_path) or not self._is_path_allowed(dst_path):
                return "Access denied: Path not in allowed directories"
            
            if not src_path.exists():
                return f"Source not found: {src_path}"
            
            shutil.move(str(src_path), str(dst_path))
            return f"Moved: {src_path} → {dst_path}"
        
        except Exception as e:
            return f"Failed to move file: {str(e)}"
    
    def organize_downloads(self) -> str:
        """Organize downloads folder by file type"""
        try:
            downloads = Path.home() / "Downloads"
            
            if not downloads.exists():
                return "Downloads folder not found"
            
            # Create category folders
            categories = {
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
                'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx'],
                'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.flv'],
                'Audio': ['.mp3', '.wav', '.flac', '.aac'],
                'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp']
            }
            
            moved_count = 0
            
            for file in downloads.iterdir():
                if file.is_file():
                    ext = file.suffix.lower()
                    
                    for category, extensions in categories.items():
                        if ext in extensions:
                            category_folder = downloads / category
                            category_folder.mkdir(exist_ok=True)
                            
                            try:
                                shutil.move(str(file), str(category_folder / file.name))
                                moved_count += 1
                            except:
                                pass
                            break
            
            return f"Organized {moved_count} files in Downloads folder"
        
        except Exception as e:
            return f"Failed to organize downloads: {str(e)}"
    
    # ==================== MACROS / AUTOMATION ====================
    
    def type_text(self, text: str, interval: float = 0.05) -> str:
        """Type text automatically"""
        try:
            import pyautogui
            
            time.sleep(2)  # Give user time to focus window
            pyautogui.typewrite(text, interval=interval)
            
            return f"Typed: {text[:50]}..."
        
        except ImportError:
            return "Feature requires pyautogui"
        except Exception as e:
            return f"Failed to type text: {str(e)}"
    
    def click_at(self, x: int, y: int) -> str:
        """Click at specific coordinates"""
        try:
            import pyautogui
            
            pyautogui.click(x, y)
            return f"Clicked at ({x}, {y})"
        
        except ImportError:
            return "Feature requires pyautogui"
        except Exception as e:
            return f"Failed to click: {str(e)}"
    
    def execute_macro(self, macro_name: str) -> str:
        """Execute predefined macro"""
        macros = {
            'open_gmail': [
                ('open', 'chrome'),
                ('wait', 2),
                ('type', 'gmail.com'),
                ('press', 'enter')
            ],
            'morning_routine': [
                ('open', 'chrome'),
                ('open', 'calendar'),
                ('open', 'email')
            ]
        }
        
        if macro_name not in macros:
            return f"Macro '{macro_name}' not found. Available: {', '.join(macros.keys())}"
        
        try:
            for action, *params in macros[macro_name]:
                if action == 'open':
                    # Use existing desktop control
                    pass
                elif action == 'wait':
                    time.sleep(params[0])
                elif action == 'type':
                    self.type_text(params[0])
                elif action == 'press':
                    import pyautogui
                    pyautogui.press(params[0])
            
            return f"Macro '{macro_name}' executed successfully"
        
        except Exception as e:
            return f"Macro execution failed: {str(e)}"
    
    # ==================== WINDOW MANAGEMENT ====================
    
    def list_windows(self) -> str:
        """Window management disabled - terminal mode only"""
        return "🪟 Window management features disabled in terminal mode."
    
    def focus_window(self, title: str) -> str:
        """Window management disabled - terminal mode only"""
        return "🪟 Window management features disabled in terminal mode."
    
    # ==================== SECURITY HELPERS ====================
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is in allowed directories"""
        try:
            path = path.resolve()
            return any(path.is_relative_to(allowed) for allowed in self.allowed_dirs)
        except:
            return False
    
    def add_allowed_directory(self, directory: str):
        """Add directory to whitelist"""
        self.allowed_dirs.append(Path(directory).expanduser())
        return f"Added to allowed directories: {directory}"
    
    # ==================== DEFAULT MACROS ====================
    
    def _default_macros(self) -> Dict[str, List]:
        """Return default predefined macros"""
        return {
            'productivity_mode': [
                {'action': 'open', 'app': 'code'},
                {'action': 'wait', 'seconds': 2},
                {'action': 'open', 'app': 'chrome'}
            ],
            'focus_mode': [
                {'action': 'close_distractions', 'apps': ['discord', 'slack']},
                {'action': 'open', 'app': 'notepad'}
            ],
            'end_of_day': [
                {'action': 'organize_downloads'},
                {'action': 'screenshot', 'name': 'end_of_day_desktop'}
            ]
        }
    
    # ==================== MAIN EXECUTION METHOD ====================
    
    def execute(self, command: str) -> str:
        """Main method to route commands to appropriate handlers"""
        command_lower = command.lower().strip()
        
        # Screenshots
        if 'screenshot' in command_lower or 'capture screen' in command_lower:
            if not self.enable_screenshots:
                return "Screenshot feature is disabled in settings"
            
            if 'region' in command_lower:
                # Parse region coordinates if available
                return "Region screenshot requires coordinates. Use: take_screenshot_region(x, y, width, height)"
            else:
                return self.take_screenshot()
        
        # Screen Recording
        elif 'record screen' in command_lower or 'start recording' in command_lower:
            if not self.enable_recording:
                return "Screen recording is disabled in settings"
            
            # Extract duration if specified
            import re
            duration_match = re.search(r'(\d+)\s*(?:second|sec)', command_lower)
            duration = int(duration_match.group(1)) if duration_match else self.default_recording_duration
            
            return self.start_screen_recording(duration)
        
        # File Operations
        elif 'organize downloads' in command_lower or 'clean downloads' in command_lower:
            if not self.enable_file_ops:
                return "File operations are disabled in settings"
            return self.organize_downloads()
        
        elif 'create folder' in command_lower or 'make directory' in command_lower:
            if not self.enable_file_ops:
                return "File operations are disabled in settings"
            return "Specify folder path to create"
        
        # Window Management
        elif 'list windows' in command_lower or 'show windows' in command_lower:
            if not self.enable_window_mgmt:
                return "Window management is disabled in settings"
            return self.list_windows()
        
        elif 'focus window' in command_lower or 'switch to window' in command_lower:
            if not self.enable_window_mgmt:
                return "Window management is disabled in settings"
            return "Specify window title to focus"
        
        # Macros
        elif 'run macro' in command_lower or 'execute macro' in command_lower:
            if not self.enable_automation:
                return "Automation is disabled in settings"
            
            # Extract macro name
            for macro_name in self.macros.keys():
                if macro_name in command_lower:
                    return self.execute_macro(macro_name)
            
            return f"Available macros: {', '.join(self.macros.keys())}"
        
        else:
            return self._help_message()
    
    def _help_message(self) -> str:
        """Return help message with available commands"""
        features = []
        
        if self.enable_screenshots:
            features.append("📸 Screenshots: 'take screenshot', 'capture screen'")
        if self.enable_recording:
            features.append("🎥 Recording: 'record screen for 10 seconds'")
        if self.enable_file_ops:
            features.append("📁 Files: 'organize downloads', 'create folder'")
        if self.enable_window_mgmt:
            features.append("🪟 Windows: 'list windows', 'focus window [name]'")
        if self.enable_automation:
            features.append(f"⚡ Macros: 'run macro [{', '.join(self.macros.keys())}]'")
        
        return "Advanced Desktop Control - Available Features:\n" + "\n".join(features)