"""
Configuration settings for orbit - fully configurable, no hardcoding
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class Settings:
    def __init__(self, config_file: Optional[str] = None):
        # Base paths
        self.BASE_DIR = Path(__file__).parent.parent.parent
        
        # Load environment variables from .env file
        env_path = self.BASE_DIR / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        self.DATA_DIR = Path(os.getenv("ORBIT_DATA_DIR", str(self.BASE_DIR / "data")))
        self.DATA_DIR.mkdir(exist_ok=True)
        
        # Load from config file if provided, or default to my_config.json
        self.config_data = {}
        if config_file is None:
            # Try to load default config
            default_config = self.BASE_DIR / "configs" / "my_config.json"
            if default_config.exists():
                config_file = str(default_config)
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                self.config_data = json.load(f)
        
        # Database Settings
        db_name = self._get_config("db_name", "orbit_memory.db")
        self.DB_PATH = self.DATA_DIR / db_name
        
        # LLM Settings - OpenAI/GitHub Models API
        self.OPENAI_API_KEY = self._get_config("openai_api_key", "")
        self.OPENAI_MODEL = self._get_config("openai_model", "gpt-4o")
        self.OPENAI_BASE_URL = self._get_config("openai_base_url", None)  # For GitHub Models or other providers
        
        # Weather API Settings
        self.WEATHER_API_URL = self._get_config("weather_api_url", "https://api.open-meteo.com/v1/forecast")
        self.WEATHER_GEOCODING_URL = self._get_config("weather_geocoding_url", "https://geocoding-api.open-meteo.com/v1/search")
        self.DEFAULT_LOCATION = self._get_config("default_location", "India")
        
        # Wikipedia API Settings
        self.WIKIPEDIA_API_URL = self._get_config("wikipedia_api_url", "https://en.wikipedia.org/w/api.php")
        self.WIKIPEDIA_LANGUAGE = self._get_config("wikipedia_language", "en")
        self.WIKIPEDIA_SUMMARY_SENTENCES = int(self._get_config("wikipedia_summary_sentences", "3"))
        
        # Speech Recognition Settings (STT)
        self.STT_ENGINE = self._get_config("stt_engine", "google")  # google, sphinx, whisper
        self.STT_TIMEOUT = int(self._get_config("stt_timeout", "10"))
        self.STT_PHRASE_LIMIT = int(self._get_config("stt_phrase_limit", "15"))
        self.STT_ENERGY_THRESHOLD = int(self._get_config("stt_energy_threshold", "0"))  # 0 = auto-adjust
        self.STT_LANGUAGE = self._get_config("stt_language", "en-US")
        
        # Whisper STT Settings (Optimized for RTX 3050 4GB)
        self.WHISPER_MODEL_SIZE = self._get_config("whisper_model_size", "base")  # tiny, base, small, medium
        # For RTX 3050 4GB: Use 'base' (1GB VRAM + 2GB for Qwen 2.5 3B = 3GB total)
        # 'tiny': 500MB (fastest, less accurate)
        # 'base': 1GB (RECOMMENDED - balanced speed/quality)
        # 'small': 2GB (better quality, may conflict with LLM)
        # 'medium': 4GB (WARNING: will conflict with Qwen 2.5 3B)
        
        # Text-to-Speech Settings (TTS)
        self.TTS_ENGINE = self._get_config("tts_engine", "higgs")  # pyttsx3, higgs (Edge TTS) - Changed to higgs for better reliability
        self.TTS_RATE = int(self._get_config("tts_rate", "175"))
        self.TTS_VOLUME = float(self._get_config("tts_volume", "0.9"))
        self.TTS_VOICE = self._get_config("tts_voice", None)  # None = use default voice
        self.TTS_VOICE_GENDER = self._get_config("tts_voice_gender", "neutral")  # male, female, neutral
        
        # HiggsAudio TTS Settings (Microsoft Edge TTS)
        self.HIGGS_TTS_VOICE = self._get_config("higgs_tts_voice", "en-US-AriaNeural")
        self.HIGGS_TTS_LANGUAGE = self._get_config("higgs_tts_language", "en-US")
        self.HIGGS_TTS_RATE = self._get_config("higgs_tts_rate", "+0%")  # -50% to +100%
        self.HIGGS_TTS_VOLUME = self._get_config("higgs_tts_volume", "+0%")  # -50% to +50%
        self.HIGGS_TTS_PITCH = self._get_config("higgs_tts_pitch", "+0Hz")  # -50Hz to +50Hz
        
        # Wake Word Settings
        self.WAKE_WORD = self._get_config("wake_word", "orbit").lower()
        self.WAKE_WORD_ENABLED = self._get_config("wake_word_enabled", "true").lower() == "true"
        self.WAKE_WORD_SENSITIVITY = float(self._get_config("wake_word_sensitivity", "0.5"))
        
        # System Settings
        self.TIMEOUT_SECONDS = int(self._get_config("timeout_seconds", "60"))
        self.MAX_CONTEXT_MESSAGES = int(self._get_config("max_context_messages", "4"))
        self.LOG_LEVEL = self._get_config("log_level", "INFO")
        self.ENABLE_AUDIO_FEEDBACK = self._get_config("enable_audio_feedback", "true").lower() == "true"
        
        # Desktop Control Settings
        self.ALLOW_APP_CONTROL = self._get_config("allow_app_control", "true").lower() == "true"
        self.ALLOWED_APPS = self._get_config_list("allowed_apps", [])  # Empty = allow all
        self.BLOCKED_APPS = self._get_config_list("blocked_apps", [])
        
        # Task Scheduling Settings
        self.ENABLE_SCHEDULER = self._get_config("enable_scheduler", "true").lower() == "true"
        self.SCHEDULER_CHECK_INTERVAL = int(self._get_config("scheduler_check_interval", "60"))
        
        # ==================== PHASE 2: ADVANCED DEVICE CONTROL ====================
        
        # Screenshot Settings
        self.ENABLE_SCREENSHOTS = self._get_config("enable_screenshots", "true").lower() == "true"
        self.SCREENSHOT_DIR = self._get_config("screenshot_dir", str(Path.home() / "Pictures" / "Orbit_Screenshots"))
        
        # Screen Recording Settings
        self.ENABLE_SCREEN_RECORDING = self._get_config("enable_screen_recording", "true").lower() == "true"
        self.RECORDING_DIR = self._get_config("recording_dir", str(Path.home() / "Pictures" / "Orbit_Screenshots"))
        self.DEFAULT_RECORDING_DURATION = int(self._get_config("default_recording_duration", "10"))
        self.RECORDING_FPS = int(self._get_config("recording_fps", "20"))
        self.RECORDING_CODEC = self._get_config("recording_codec", "XVID")
        
        # File Management Settings
        self.ENABLE_FILE_OPERATIONS = self._get_config("enable_file_operations", "true").lower() == "true"
        self.ALLOWED_DIRECTORIES = self._get_config_list("allowed_directories", [
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Pictures")
        ])
        
        # File Organization Categories
        self.FILE_CATEGORIES = self._get_config_dict("file_categories", {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.odt'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.xml']
        })
        
        # Automation & Macro Settings
        self.ENABLE_AUTOMATION = self._get_config("enable_automation", "true").lower() == "true"
        self.MACROS = self._get_config_dict("macros", {})  # Load custom macros from config
        
        # Window Management Settings
        self.ENABLE_WINDOW_MANAGEMENT = self._get_config("enable_window_management", "true").lower() == "true"
        
        # ==================== PHASE 3: AI & PRODUCTIVITY ====================
        
        # Translation Settings
        self.ENABLE_TRANSLATION = self._get_config("enable_translation", "true").lower() == "true"
        self.DEFAULT_SOURCE_LANGUAGE = self._get_config("default_source_language", "auto")
        self.DEFAULT_TARGET_LANGUAGE = self._get_config("default_target_language", "en")
        self.SUPPORTED_LANGUAGES = self._get_config_list("supported_languages", [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh-cn", "zh-tw",
            "ar", "hi", "bn", "pa", "te", "mr", "ta", "ur", "gu", "kn"
        ])
        
        # Task Prediction & Smart Reminders Settings
        self.ENABLE_TASK_PREDICTION = self._get_config("enable_task_prediction", "true").lower() == "true"
        self.ENABLE_SMART_REMINDERS = self._get_config("enable_smart_reminders", "true").lower() == "true"
        self.TASK_HISTORY_FILE = self._get_config("task_history_file", "data/task_history.json")
        self.MIN_TASKS_FOR_PREDICTION = int(self._get_config("min_tasks_for_prediction", "5"))
        self.SMART_REMINDER_LEAD_TIME = int(self._get_config("smart_reminder_lead_time", "15"))  # minutes
        
        # Schedule Optimization Settings
        self.ENABLE_SCHEDULE_OPTIMIZATION = self._get_config("enable_schedule_optimization", "true").lower() == "true"
        self.SCHEDULE_FILE = self._get_config("schedule_file", "data/schedule.json")
        self.WORK_START_HOUR = int(self._get_config("work_start_hour", "9"))
        self.WORK_END_HOUR = int(self._get_config("work_end_hour", "17"))
        self.BREAK_DURATION = int(self._get_config("break_duration", "15"))  # minutes
        
        # Document Organization Settings
        self.ENABLE_DOC_ORGANIZATION = self._get_config("enable_doc_organization", "true").lower() == "true"
        self.DOCUMENTS_DIR = self._get_config("documents_dir", str(Path.home() / "Documents"))
        self.ORGANIZE_BY_DATE_FORMAT = self._get_config("organize_by_date_format", "%Y-%m")  # YYYY-MM
        self.ENABLE_AUTO_ORGANIZE = self._get_config("enable_auto_organize", "false").lower() == "true"
        self.AUTO_ORGANIZE_INTERVAL = int(self._get_config("auto_organize_interval", "3600"))  # seconds
        
        # Document Summarization Settings
        self.ENABLE_DOC_SUMMARIZATION = self._get_config("enable_doc_summarization", "true").lower() == "true"
        self.SUMMARY_MAX_LENGTH = int(self._get_config("summary_max_length", "500"))
        self.SUMMARY_MODEL = self._get_config("summary_model", "phi3:mini")  # Ollama model
        
        # CSV/Excel Processing Settings
        self.ENABLE_CSV_PROCESSING = self._get_config("enable_csv_processing", "true").lower() == "true"
        self.CSV_DELIMITER = self._get_config("csv_delimiter", ",")
        self.CSV_ENCODING = self._get_config("csv_encoding", "utf-8")
        
        # Report Generation Settings
        self.ENABLE_REPORT_GENERATION = self._get_config("enable_report_generation", "true").lower() == "true"
        self.REPORTS_DIR = self._get_config("reports_dir", str(Path.home() / "Documents" / "Orbit_Reports"))
        self.REPORT_FORMAT = self._get_config("report_format", "txt")  # txt, csv, json
        
        # Screen Time Tracking Settings
        self.ENABLE_SCREEN_TIME_TRACKING = self._get_config("enable_screen_time_tracking", "true").lower() == "true"
        self.SCREEN_TIME_LOG_FILE = self._get_config("screen_time_log_file", "data/screen_time.json")
        self.TRACK_INTERVAL = int(self._get_config("track_interval", "60"))  # seconds
        self.WORK_DURATION = int(self._get_config("work_duration", "50"))  # minutes (Pomodoro-style)
        self.BREAK_REMINDER_DURATION = int(self._get_config("break_reminder_duration", "10"))  # minutes
        self.DAILY_WORK_LIMIT = int(self._get_config("daily_work_limit", "480"))  # minutes (8 hours)
        
        # ==================== PHASE 4: YOUTUBE MUSIC (14 FEATURES) ====================
        
        # YouTube Music Core Settings
        self.ENABLE_YOUTUBE_MUSIC = self._get_config("enable_youtube_music", "true").lower() == "true"
        self.YOUTUBE_MUSIC_AUTH_FILE = self._get_config("youtube_music_auth_file", "headers_auth.json")
        self.YOUTUBE_MUSIC_DEFAULT_VOLUME = int(self._get_config("youtube_music_default_volume", "50"))
        self.YOUTUBE_MUSIC_MAX_QUEUE_SIZE = int(self._get_config("youtube_music_max_queue_size", "100"))
        self.YOUTUBE_MUSIC_SEARCH_LIMIT = int(self._get_config("youtube_music_search_limit", "10"))
        self.YOUTUBE_MUSIC_AUTO_PLAY_NEXT = self._get_config("youtube_music_auto_play_next", "true").lower() == "true"
        
        # YouTube Music Mood Keywords (configurable)
        self.YOUTUBE_MUSIC_MOOD_KEYWORDS = self._get_config_dict("youtube_music_mood_keywords", {
            'happy': ['upbeat', 'cheerful', 'party', 'joyful'],
            'sad': ['melancholic', 'emotional', 'tearjerker'],
            'energetic': ['workout', 'gym', 'pump up', 'motivation'],
            'relaxed': ['chill', 'ambient', 'peaceful', 'calm'],
            'focus': ['study', 'concentration', 'lofi', 'instrumental']
        })
        
        # ==================== PHASE 2: COMMUNICATION (12 FEATURES) ====================
        
        # Email Settings (IMAP/SMTP)
        self.EMAIL_ADDRESS = self._get_config("EMAIL_ADDRESS", None)
        self.EMAIL_PASSWORD = self._get_config("EMAIL_PASSWORD", None)
        self.IMAP_SERVER = self._get_config("IMAP_SERVER", "imap.gmail.com")
        self.IMAP_PORT = int(self._get_config("IMAP_PORT", "993"))
        self.SMTP_SERVER = self._get_config("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(self._get_config("SMTP_PORT", "587"))
        
        # Telegram Settings
        self.TELEGRAM_BOT_TOKEN = self._get_config("TELEGRAM_BOT_TOKEN", None)
        self.TELEGRAM_CHAT_ID = self._get_config("TELEGRAM_CHAT_ID", None)
        
        # Twilio SMS Settings
        self.TWILIO_ACCOUNT_SID = self._get_config("TWILIO_ACCOUNT_SID", None)
        self.TWILIO_AUTH_TOKEN = self._get_config("TWILIO_AUTH_TOKEN", None)
        self.TWILIO_PHONE_NUMBER = self._get_config("TWILIO_PHONE_NUMBER", None)
        
        # Priority Email Settings
        self.PRIORITY_KEYWORDS = self._get_config_list("PRIORITY_KEYWORDS", [
            'urgent', 'important', 'asap', 'critical', 'emergency', 'deadline'
        ])
        self.PRIORITY_SENDERS = self._get_config_list("PRIORITY_SENDERS", [])
        
        # Assistant Personality
        default_prompt = """You are Orbit, an intelligent AI assistant inspired by Jarvis.
You are helpful, efficient, and personable. You provide clear, concise answers.
You can control smart home devices, manage tasks, and assist with information."""
        self.SYSTEM_PROMPT = self._get_config("system_prompt", default_prompt)
        self.ASSISTANT_NAME = self._get_config("assistant_name", "Orbit")
        
    def _get_config(self, key: str, default: Any) -> Any:
        """Get configuration value from env var, config file, or default"""
        # Priority: 1. Environment variable, 2. Config file, 3. Default
        env_key = f"ORBIT_{key.upper()}"
        value = os.getenv(env_key, self.config_data.get(key, default))
        
        # Convert boolean values properly
        if isinstance(value, bool):
            return "true" if value else "false"
        
        return value
    
    def _get_config_list(self, key: str, default: list) -> list:
        """Get list configuration from env var (comma-separated) or config file"""
        env_key = f"ORBIT_{key.upper()}"
        env_value = os.getenv(env_key)
        
        if env_value:
            return [item.strip() for item in env_value.split(',') if item.strip()]
        
        config_value = self.config_data.get(key, default)
        if isinstance(config_value, list):
            return config_value
        
        return default
    
    def _get_config_dict(self, key: str, default: dict) -> dict:
        """Get dictionary configuration from config file"""
        config_value = self.config_data.get(key, default)
        if isinstance(config_value, dict):
            return config_value
        return default

    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return self.SYSTEM_PROMPT
    
    def to_dict(self) -> Dict[str, Any]:
        """Export settings as dictionary (excluding sensitive data)"""
        return {
            'assistant_name': self.ASSISTANT_NAME,
            'wake_word': self.WAKE_WORD,
            'ollama_model': self.OLLAMA_MODEL,
            'stt_engine': self.STT_ENGINE,
            'tts_engine': self.TTS_ENGINE,
            'default_location': self.DEFAULT_LOCATION
        }
    
    def save_to_file(self, filepath: str):
        """Save non-sensitive settings to JSON file"""
        config = {
            'assistant_name': self.ASSISTANT_NAME,
            'wake_word': self.WAKE_WORD,
            'ollama_model': self.OLLAMA_MODEL,
            'stt_engine': self.STT_ENGINE,
            'tts_engine': self.TTS_ENGINE,
            'tts_rate': self.TTS_RATE,
            'tts_volume': self.TTS_VOLUME,
            'default_location': self.DEFAULT_LOCATION,
            'max_context_messages': self.MAX_CONTEXT_MESSAGES
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Settings saved to {filepath}")