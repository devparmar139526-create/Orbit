"""
Selects appropriate information source based on query type
"""
from Orbit_core.actions.advanced_desktop import AdvancedDesktopControl
from Orbit_core.actions.wikipedia import WikipediaAction
from Orbit_core.actions.weather import WeatherAction
from Orbit_core.actions.desktop import DesktopAction
from Orbit_core.actions.schedule_action import ScheduleAction
from Orbit_core.actions.translation import TranslationService
from Orbit_core.actions.productivity_ai import ProductivityAI
from Orbit_core.actions.document_processor import DocumentProcessor
from Orbit_core.actions.screen_time_tracker import ScreenTimeTracker
from Orbit_core.actions.youtube_music import YouTubeMusicService
from Orbit_core.actions.communication import CommunicationService
from Orbit_core.actions.email_voice_assistant import EmailVoiceAssistant
from typing import List, Dict, Generator
from pathlib import Path
import re
from datetime import datetime
import time

class SourceSelector:
    def __init__(self, llm_router, settings):
        self.llm = llm_router
        self.settings = settings
        
        # Initialize action handlers with settings
        self.wikipedia = WikipediaAction(settings)
        self.weather = WeatherAction(settings)
        self.desktop = DesktopAction(settings)
        self.scheduler = ScheduleAction(settings)
        self.advanced_desktop = AdvancedDesktopControl(settings)
        
        # Phase 2: Communication handler
        self.communication = CommunicationService(settings)
        
        # Email Voice Assistant (voice-controlled email operations)
        self.email_assistant = EmailVoiceAssistant(self.communication, llm_router, settings)
        
        # Phase 3: AI & Productivity handlers
        self.translation = TranslationService(settings)
        self.productivity_ai = ProductivityAI(settings)
        self.document_processor = DocumentProcessor(settings)
        self.screen_time_tracker = ScreenTimeTracker(settings)
        
        # Phase 4: YouTube Music handler
        self.youtube_music = YouTubeMusicService(settings)
        
        # Fast response cache for common queries
        self.fast_responses = {
            'hi': "Hello! I'm Orbit.",
            'hello': "Hi there!",
            'how are you': "I'm working perfectly!",
            'what can you do': "I can search Wikipedia, check weather, open apps, and more!",
            'thanks': "You're welcome!",
            'thank you': "Happy to help!",
            'bye': "Goodbye!",
            'what is ai': "AI is artificial intelligence - computer systems that can learn.",
            'what is artificial intelligence': "Computer systems that can perform tasks requiring human intelligence."
        }

    def classify_intent(self, query: str) -> str:
        query_lower = query.lower().strip()
        
        # PRIORITY 1: Check for SCHEDULED desktop commands FIRST (before immediate desktop)
        # Timed desktop actions (open X in Y seconds/minutes/hours) 
        if (' in ' in query_lower and ('second' in query_lower or 'minute' in query_lower or 'hour' in query_lower)):
            if any(cmd in query_lower for cmd in ['open', 'launch', 'start']):
                return 'schedule'
        
        # Timed actions with "at" (open X at Y PM/AM)
        if (' at ' in query_lower and (' pm' in query_lower or ' am' in query_lower)):
            if any(cmd in query_lower for cmd in ['open', 'launch', 'start']):
                return 'schedule'
        
        # PRIORITY 2: Phase 4 - YouTube Music (check before Phase 3 to avoid conflicts)
        youtube_music_keywords = [
            'play music', 'play song', 'play track', 'play artist',
            'search music', 'search song', 'find song', 'find music',
            'pause music', 'pause song', 'resume music', 'continue music',
            'next song', 'previous song', 'skip song', 'skip track',
            'volume up', 'volume down', 'set volume', 'increase volume', 'decrease volume',
            'add to queue', 'clear queue', 'shuffle queue', 'show queue', 'view queue',
            'create playlist', 'show playlists', 'my playlists', 'list playlists',
            'recommend music', 'music suggestions', 'suggest songs',
            'happy music', 'sad music', 'workout music', 'chill music', 'focus music',
            'energetic music', 'relaxed music', 'party music',
            'what\'s playing', 'current song', 'music status', 'now playing'
        ]
        
        # Check for specific patterns first
        if query_lower.startswith('play ') and not any(word in query_lower for word in ['video', 'movie', 'game']):
            return 'youtube_music'
        
        if any(keyword in query_lower for keyword in youtube_music_keywords):
            return 'youtube_music'
        
        # PRIORITY 2.5: Phase 2 - Communication Features
        # Check Email Voice Assistant first (handles voice-controlled email workflow)
        email_voice_keywords = [
            'check email', 'read email', 'new email', 'unread email', 'any email',
            'reply', 'reply to', 'send reply', 'answer email', 'respond to',
            'compose email', 'send email to', 'write email', 'how many email'
        ]
        if any(keyword in query_lower for keyword in email_voice_keywords):
            # Check if we're in an active email conversation
            if self.email_assistant.state['mode'] != 'idle' or self.email_assistant.state['pending_send']:
                return 'email_voice'
            # New email command
            return 'email_voice'
        
        # Other communication features (Telegram, SMS, notifications, etc.)
        communication_keywords = [
            'priority email', 'urgent email', 'important email',
            'summarize email', 'email summary',
            'action item', 'extract action',
            'send telegram', 'telegram message',
            'send sms', 'text message',
            'notification', 'notify me', 'send notification',
            'mark as read', 'mark email',
            'auto reply', 'automatic reply'
        ]
        if any(keyword in query_lower for keyword in communication_keywords):
            return 'communication'
        
        # PRIORITY 3: Phase 3 - AI & Productivity Features
        # Translation patterns
        translation_keywords = [
            'translate', 'translation', 'what language is', 'detect language',
            'say in', 'how do you say', 'spanish for', 'french for', 'german for'
        ]
        if any(keyword in query_lower for keyword in translation_keywords):
            return 'translation'
        
        # Task prediction & smart reminders
        task_prediction_keywords = [
            'predict next task', 'what should i do next', 'suggest task',
            'optimize schedule', 'optimize my schedule', 'improve schedule'
        ]
        if any(keyword in query_lower for keyword in task_prediction_keywords):
            return 'productivity_ai'
        
        # Document organization patterns
        doc_organization_keywords = [
            'organize documents', 'organize files by date', 'organize files by type',
            'process csv', 'analyze csv', 'analyse csv',
            'generate report', 'create report'
        ]
        
        # Summarization patterns (separate check to catch any "summarize/summarise")
        if 'summarize' in query_lower or 'summarise' in query_lower:
            return 'document_processor'
        
        if any(keyword in query_lower for keyword in doc_organization_keywords):
            return 'document_processor'
        
        # Screen time tracking patterns
        screen_time_keywords = [
            'screen time', 'track screen time', 'how long have i worked',
            'daily report', 'weekly report', 'take a break', 'break suggestion'
        ]
        if any(keyword in query_lower for keyword in screen_time_keywords):
            return 'screen_time_tracker'
        
        # PRIORITY 3: Advanced Desktop Control (Phase 2 Features)
        advanced_desktop_keywords = [
            'screenshot', 'capture screen', 'record screen', 'start recording',
            'organize downloads', 'clean downloads', 'list windows', 'show windows',
            'focus window', 'switch to window', 'run macro', 'execute macro',
            'create folder', 'make directory', 'delete file', 'move file'
        ]
        if any(keyword in query_lower for keyword in advanced_desktop_keywords):
            return 'advanced_desktop'
        
        # PRIORITY 3: Immediate desktop control (no time specified)
        desktop_patterns = ['open ', 'launch ', 'start ', 'close ', 'run ']
        if any(query_lower.startswith(pattern) for pattern in desktop_patterns):
            return 'desktop'
        
        # Weather detection
        weather_words = ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'climate', 'hot', 'cold']
        if any(word in query_lower for word in weather_words):
            return 'weather'
        
        # Math/Calculator detection - BEFORE Wikipedia to avoid "what is 5+5" going to Wiki
        math_indicators = ['+', '-', '*', '/', 'x', '×', '÷', 'calculate', 'compute', 'math']
        # Check for math operators or explicit calculation requests
        has_math = any(indicator in query_lower for indicator in math_indicators)
        # Also check for number patterns like "what is 5 plus 5"
        number_words = ['plus', 'minus', 'times', 'divided', 'multiply', 'add', 'subtract']
        has_number_words = any(word in query_lower for word in number_words)
        
        if has_math or has_number_words:
            # This is a math question, send to LLM not Wikipedia
            return 'llm'
        
        # Wikipedia detection - only for specific question patterns (AFTER math check)
        # Exclude queries that are likely factual questions answerable by LLM
        wiki_patterns = ['who is ', 'tell me about ', 'information about ']
        
        # Only send to Wikipedia if it's clearly about a person, place, or specific topic
        # NOT for generic "what is" questions that might be math or definitions
        if any(query_lower.startswith(pattern) for pattern in wiki_patterns):
            # Additional check: avoid Wikipedia for short queries that might be commands
            if len(query_lower.split()) >= 3:  # At least 3 words to be a real Wiki query
                return 'wikipedia'
        
        # Let LLM handle most "what is" questions instead of Wikipedia
        # Wikipedia is now only for explicit biographical/informational queries
        
        # Priority 3: Regular reminders
        schedule_patterns = [
            # Complete scheduling commands with time
            'remind me to' in query_lower and (' at ' in query_lower or ' pm' in query_lower or ' am' in query_lower or ' tomorrow' in query_lower or ' in ' in query_lower),
            # Step 1: "remind me to" without time
            query_lower.startswith('remind me to') and not (' at ' in query_lower or ' pm' in query_lower or ' am' in query_lower or ' tomorrow' in query_lower or ' in ' in query_lower),
            # Other explicit scheduling
            'schedule' in query_lower and (' at ' in query_lower or ' pm' in query_lower or ' am' in query_lower),
            'set alarm' in query_lower,
            'set reminder' in query_lower and (' at ' in query_lower or ' pm' in query_lower or ' am' in query_lower)
        ]
        
        if any(schedule_patterns):
            return 'schedule'
        
        # Desktop - immediate actions without time
        desktop_indicators = ['open', 'launch', 'start', 'close']
        if any(indicator in query_lower for indicator in desktop_indicators):
            return 'desktop'
        
        # Advanced desktop - very specific
        advanced_desktop_indicators = ['take screenshot', 'organize downloads', 'lock computer', 'lock device']
        if any(indicator in query_lower for indicator in advanced_desktop_indicators):
            return 'advanced_desktop'
        
        # DEFAULT: Everything else goes to LLM for natural conversation
        return 'llm'
    
    def process(self, query: str, context: List[Dict] = None) -> Generator[str, None, None]:
        """Process query and yield response chunks."""
        query_lower = query.lower().strip()
        
        # Check for pending schedule task FIRST (highest priority)
        if self.scheduler.pending_task:
            yield self._handle_schedule(query)
            return
        
        # Check fast cache
        if query_lower in self.fast_responses:
            yield self.fast_responses[query_lower]
            return
        
        intent = self.classify_intent(query)
        
        try:
            if intent == 'weather':
                yield self._handle_weather(query)
            
            elif intent == 'wikipedia':
                yield self._handle_wikipedia(query)
            
            elif intent == 'email_voice':
                yield self._handle_email_voice(query)
            
            elif intent == 'communication':
                yield self._handle_communication(query)
            
            elif intent == 'translation':
                yield self._handle_translation(query)
            
            elif intent == 'productivity_ai':
                yield self._handle_productivity_ai(query)
            
            elif intent == 'document_processor':
                yield self._handle_document_processor(query)
            
            elif intent == 'screen_time_tracker':
                yield self._handle_screen_time_tracker(query)
            
            elif intent == 'youtube_music':
                yield self._handle_youtube_music(query)
            
            elif intent == 'advanced_desktop':
                yield self._handle_advanced_desktop(query)
            
            elif intent == 'desktop':
                yield self._handle_desktop(query)
            
            elif intent == 'schedule':
                yield self._handle_schedule(query)
            
            else:  # llm
                yield from self.llm.generate(query, context)
        
        except Exception as e:
            yield f"Error: {str(e)}"

    def _handle_weather(self, query: str) -> str:
        location = None
        query_lower = query.lower()
        if ' in ' in query_lower:
            location = query_lower.split(' in ')[-1].strip('?.,')
        elif ' for ' in query_lower:
            location = query_lower.split(' for ')[-1].strip('?.,')
        return self.weather.get_weather(location)

    def _handle_wikipedia(self, query: str) -> str:
        search_term = query
        query_lower = query.lower()
        for prefix in ['who is ', 'what is ', 'tell me about ', 'information about ', 'define ', 'explain ']:
            if query_lower.startswith(prefix):
                search_term = query[len(prefix):].strip('?.,')
                break
        return self.wikipedia.search(search_term)

    def _handle_desktop(self, query: str) -> str:
        return self.desktop.execute(query)
    
    def _handle_advanced_desktop(self, query: str) -> str:
        return self.advanced_desktop.execute(query)

    def _handle_schedule(self, query: str) -> str:
        task_data = self.scheduler.schedule(query)
        if isinstance(task_data, str):
            return task_data
        
        scheduled_time = task_data['scheduled_time']
        task = task_data['task']
        time_until = scheduled_time - datetime.now()
        
        # Schedule the task using threading for any future time
        if time_until.total_seconds() > 0:
            import threading
            
            def execute_later():
                import time
                time.sleep(time_until.total_seconds())
                
                if re.search(r'(?:open|launch|start)\s+.+', task.lower()):
                    desktop_response = self.desktop.execute(task)
                    print(f"\n🤖 orbit: Scheduled task executed! {desktop_response}\n")
                else:
                    print(f"\n🤖 orbit: Reminder - {task}\n")
            
            # Start the timer thread
            timer_thread = threading.Thread(target=execute_later, daemon=True)
            timer_thread.start()
            
            time_str = scheduled_time.strftime("%I:%M %p on %B %d")
            return f"Got it! I'll execute '{task}' at {time_str}."
        else:
            return "That time has already passed. Please specify a future time."
    
    # ==================== PHASE 2: COMMUNICATION HANDLERS ====================
    
    def _handle_email_voice(self, query: str) -> str:
        """Handle voice-controlled email operations with conversation state"""
        return self.email_assistant.process_voice_command(query)
    
    def _handle_communication(self, query: str) -> str:
        """Handle communication requests (emails, messaging, notifications)"""
        return self.communication.execute(query)
    
    # ==================== PHASE 3: AI & PRODUCTIVITY HANDLERS ====================
    
    def _handle_translation(self, query: str) -> str:
        """Handle translation requests"""
        query_lower = query.lower()
        
        # Detect language pattern
        if 'what language' in query_lower or 'detect language' in query_lower:
            # Extract text after "is" or last quote
            text = query.split('is')[-1].strip(' "\'?.,')
            result = self.translation.detect_language(text)
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                lang_name = result.get('language_name', result.get('language_code', 'unknown'))
                return f"Detected language: {lang_name}"
            return str(result)
        
        # Translation pattern: "translate X to Y"
        if 'translate' in query_lower:
            if ' to ' in query_lower:
                parts = query_lower.split(' to ')
                target_lang = parts[-1].strip(' ?.,')
                text_part = parts[0].replace('translate', '').strip(' "\'')
                result = self.translation.translate_text(text_part, target_lang=target_lang)
            else:
                text = query.replace('translate', '', 1).strip(' "\'?.,')
                result = self.translation.translate_text(text)
            
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                return result.get('translated_text', str(result))
            return str(result)
        
        # "Say X in Y" or "how do you say X in Y"
        if ' in ' in query_lower:
            parts = query_lower.split(' in ')
            target_lang = parts[-1].strip(' ?.,')
            text = parts[0].replace('how do you say', '').replace('say', '').strip(' "\'')
            result = self.translation.translate_text(text, target_lang=target_lang)
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                return result.get('translated_text', str(result))
            return str(result)
        
        return "I can translate text between languages. Try: 'translate hello to spanish'"
    
    def _handle_productivity_ai(self, query: str) -> str:
        """Handle productivity AI requests"""
        query_lower = query.lower()
        
        # Task prediction
        if 'predict' in query_lower or 'what should i do' in query_lower or 'suggest task' in query_lower:
            result = self.productivity_ai.predict_next_task()
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                if 'prediction' in result:
                    conf = result.get('confidence', 0)
                    return f"Task prediction: {result['prediction']} (confidence: {int(conf*100)}%)"
                return str(result)
            return str(result)
        
        # Schedule optimization
        if 'optimize schedule' in query_lower or 'improve schedule' in query_lower:
            result = self.productivity_ai.optimize_schedule()
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                if 'message' in result:
                    return result['message']
                return str(result)
            return str(result)
        
        return "I can predict your next task or optimize your schedule. Try: 'predict next task'"
    
    def _handle_document_processor(self, query: str) -> str:
        """Handle document processing requests"""
        query_lower = query.lower()
        
        # Document organization
        if 'organize' in query_lower:
            if 'by date' in query_lower:
                path = self.settings.DOCUMENTS_DIR
                return self.document_processor.organize_documents_by_date(path)
            elif 'by type' in query_lower:
                path = self.settings.DOCUMENTS_DIR
                return self.document_processor.organize_documents_by_type(path)
            else:
                # Default to type organization
                path = self.settings.DOCUMENTS_DIR
                return self.document_processor.organize_documents_by_type(path)
        
        # Document summarization
        if 'summarize' in query_lower or 'summarise' in query_lower:
            import re
            
            # Voice-friendly commands
            if 'latest' in query_lower or 'most recent' in query_lower or 'newest' in query_lower:
                # "summarize latest pdf" or "summarize most recent document"
                file_type = None
                if 'pdf' in query_lower:
                    file_type = 'pdf'
                elif 'text' in query_lower or 'txt' in query_lower:
                    file_type = 'txt'
                elif 'csv' in query_lower:
                    file_type = 'csv'
                
                result = self.document_processor.summarize_document(filename=None, file_type=file_type)
            
            # Check for quoted path (text mode)
            elif re.search(r'["\'](.+?)["\']', query):
                quoted_match = re.search(r'["\'](.+?)["\']', query)
                file_path = quoted_match.group(1)
                result = self.document_processor.summarize_document(file_path=file_path)
            
            # Check for full path (contains : or \ or /)
            elif any(char in query for char in [':', '\\', '/']):
                words = query.split()
                file_path = None
                for i, word in enumerate(words):
                    if ':' in word or '\\' in word or '/' in word:
                        file_path = ' '.join(words[i:]).strip(' "\'?.,')
                        break
                if file_path:
                    result = self.document_processor.summarize_document(file_path=file_path)
                else:
                    return "Could not extract file path from command"
            
            # Voice-friendly: extract filename from natural speech
            else:
                # Remove command words to get filename
                filename_words = query_lower
                for remove_word in ['summarize', 'summarise', 'document', 'file', 'pdf', 'the', 'this', 'called', 'named']:
                    filename_words = filename_words.replace(remove_word, ' ')
                
                filename = filename_words.strip()
                
                # Detect file type from query
                file_type = None
                if 'pdf' in query_lower:
                    file_type = 'pdf'
                elif 'text' in query_lower or 'txt' in query_lower:
                    file_type = 'txt'
                elif 'csv' in query_lower:
                    file_type = 'csv'
                
                if filename:
                    result = self.document_processor.summarize_document(filename=filename, file_type=file_type)
                else:
                    # No filename - get most recent
                    result = self.document_processor.summarize_document(file_type=file_type)
            
            # Format response
            if isinstance(result, dict):
                if 'error' in result:
                    error_msg = result['error']
                    if 'suggestion' in result:
                        error_msg += f"\n{result['suggestion']}"
                    return error_msg
                # Format the response
                return f"Document Summary:\n  File: {Path(result.get('file', 'Unknown')).name}\n  Type: {result.get('type', 'Unknown')}\n  Size: {result.get('size', 'Unknown')}\n\nSummary:\n{result.get('summary', 'No summary available')}"
            return str(result)
        
        # CSV processing
        if 'process csv' in query_lower or 'analyze csv' in query_lower or 'analyse csv' in query_lower:
            import re
            
            # Try to find quoted path first
            quoted_match = re.search(r'["\'](.+?)["\']', query)
            if quoted_match:
                file_path = quoted_match.group(1)
            else:
                words = query.split()
                file_path = None
                for i, word in enumerate(words):
                    # If word looks like a path
                    if ':' in word or '\\' in word or '/' in word or word.endswith('.csv'):
                        file_path = ' '.join(words[i:]).strip(' "\'?.,')
                        break
                    if word.lower() in ['csv', 'file']:
                        if i + 1 < len(words):
                            potential_path = ' '.join(words[i+1:]).strip(' "\'?.,')
                            if ':' in potential_path or '\\' in potential_path or '/' in potential_path or '.csv' in potential_path:
                                file_path = potential_path
                                break
            
            if file_path:
                result = self.document_processor.process_csv(file_path)
                if isinstance(result, dict):
                    if 'error' in result:
                        return result['error']
                    # Format the response
                    return f"CSV Analysis:\n  File: {result.get('file', 'Unknown')}\n  Rows: {result.get('rows', 0)}\n  Columns: {result.get('columns', 0)}\n  Column Names: {', '.join(result.get('column_names', []))}\n  Size: {result.get('size', 'Unknown')}"
                return str(result)
            return "Please specify a CSV file to process. Example: 'analyze csv C:\\path\\to\\data.csv'"
        
        # Report generation
        if 'generate report' in query_lower or 'create report' in query_lower:
            data = {"timestamp": "now", "status": "complete"}
            result = self.document_processor.generate_report(data, report_type='summary')
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                return f"Report Generated:\n  Title: {result.get('title', 'Report')}\n  Type: {result.get('type', 'summary')}\n  Generated: {result.get('generated_at', 'now')}"
            return str(result)
        
        return "I can organize documents, summarize files, or process CSV data. Try: 'organize documents by type'"
    
    def _handle_screen_time_tracker(self, query: str) -> str:
        """Handle screen time tracking requests"""
        query_lower = query.lower()
        
        # Start tracking
        if 'track screen time' in query_lower or 'start tracking' in query_lower:
            result = self.screen_time_tracker.start_tracking()
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                return result.get('message', 'Screen time tracking started')
            return str(result)
        
        # Stop tracking
        if 'stop tracking' in query_lower:
            return self.screen_time_tracker.stop_tracking()
        
        # Daily report
        if 'daily report' in query_lower:
            return self.screen_time_tracker.get_daily_report()
        
        # Weekly report
        if 'weekly report' in query_lower:
            result = self.screen_time_tracker.get_weekly_report()
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                return str(result)
            return str(result)
        
        # Break suggestion
        if 'break' in query_lower or 'take a break' in query_lower:
            result = self.screen_time_tracker.suggest_break()
            if isinstance(result, dict):
                if 'error' in result:
                    return result['error']
                return result.get('message', str(result))
            return str(result)
        
        return "I can track your screen time and suggest breaks. Try: 'track screen time' or 'daily report'"
    
    def _handle_youtube_music(self, query: str) -> str:
        """Handle YouTube Music commands - Phase 4 (14 features)"""
        try:
            # Use the built-in process_command method that handles all 14 features
            result = self.youtube_music.process_command(query)
            return result
        except Exception as e:
            return f"\u274c YouTube Music error: {str(e)}"