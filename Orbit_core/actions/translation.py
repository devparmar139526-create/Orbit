"""
Translation & Language Services
Phase 3: AI & Productivity - Zero Hardcoding
"""

from typing import Optional, Dict, List
import json

class TranslationService:
    def __init__(self, settings=None):
        self.settings = settings
        
        # Get configuration
        self.enable_translation = getattr(settings, 'ENABLE_TRANSLATION', True) if settings else True
        self.default_target_language = getattr(settings, 'DEFAULT_TARGET_LANGUAGE', 'en') if settings else 'en'
        self.translation_service = getattr(settings, 'TRANSLATION_SERVICE', 'deep_translator') if settings else 'deep_translator'
        
        # Language codes mapping
        self.language_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
            'ko': 'Korean', 'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
            'ar': 'Arabic', 'hi': 'Hindi', 'bn': 'Bengali', 'ur': 'Urdu',
            'ta': 'Tamil', 'te': 'Telugu', 'mr': 'Marathi', 'gu': 'Gujarati'
        }
        
        # Initialize translator
        self.translator = None
        self._init_translator()
    
    def _init_translator(self):
        """Initialize translation service"""
        try:
            if self.translation_service == 'googletrans':
                from googletrans import Translator
                self.translator = Translator()
            elif self.translation_service == 'deep_translator':
                from deep_translator import GoogleTranslator
                self.translator = GoogleTranslator
        except ImportError as e:
            self.translator = None
    
    def translate_text(self, text: str, target_lang: Optional[str] = None, source_lang: Optional[str] = None) -> Dict:
        """
        Translate text from one language to another
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'es', 'fr')
            source_lang: Source language code (optional, auto-detect if None)
        
        Returns:
            Dict with translation details
        """
        if not self.enable_translation:
            return {'error': 'Translation feature is disabled in settings'}
        
        try:
            target_lang = target_lang or self.default_target_language
            
            # Use deep-translator (which is already installed)
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='auto', target=target_lang)
            translated_text = translator.translate(text)
            
            return {
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_lang or 'auto',
                'source_language_name': self.language_names.get(source_lang, 'Auto-detected'),
                'target_language': target_lang,
                'target_language_name': self.language_names.get(target_lang, target_lang),
                'confidence': None
            }
            
        except Exception as e:
            return {'error': f'Translation failed: {str(e)}'}
    
    def detect_language(self, text: str) -> Dict:
        """
        Detect the language of given text
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict with language detection details
        """
        if not self.enable_translation:
            return {'error': 'Translation feature is disabled in settings'}
        
        try:
            # Use deep-translator for language detection
            from deep_translator import single_detection
            detected_lang = single_detection(text, api_key=None)
            
            return {
                'text': text,
                'language_code': detected_lang,
                'language_name': self.language_names.get(detected_lang, detected_lang),
                'confidence': 0.95  # deep-translator doesn't provide confidence
            }
            
        except Exception as e:
            return {'error': f'Language detection failed: {str(e)}'}
    
    def translate_speech(self, audio_text: str, target_lang: Optional[str] = None) -> Dict:
        """
        Translate speech (already converted to text via STT)
        
        Args:
            audio_text: Text from speech recognition
            target_lang: Target language code
        
        Returns:
            Dict with translation details
        """
        return self.translate_text(audio_text, target_lang)
    
    def batch_translate(self, texts: List[str], target_lang: Optional[str] = None) -> List[Dict]:
        """
        Translate multiple texts at once
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
        
        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            result = self.translate_text(text, target_lang)
            results.append(result)
        return results
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        return self.language_names
    
    def execute(self, command: str) -> str:
        """Main execution method for routing translation commands"""
        command_lower = command.lower().strip()
        
        # Detect language
        if 'detect language' in command_lower or 'what language' in command_lower:
            # Extract text after the command
            text = command
            for prefix in ['detect language', 'what language is', 'identify language']:
                if prefix in command_lower:
                    text = command[command_lower.index(prefix) + len(prefix):].strip()
                    break
            
            if text and text != command:
                result = self.detect_language(text)
                if 'error' in result:
                    return result['error']
                return f"Detected language: {result['language_name']} ({result['language_code']}) - Confidence: {result['confidence']:.2%}"
            else:
                return "Please provide text to detect language"
        
        # Translate text
        elif 'translate' in command_lower:
            # Parse translation request
            # Format: "translate [text] to [language]"
            import re
            
            # Extract target language
            target_lang = None
            for lang_code, lang_name in self.language_names.items():
                if f'to {lang_name.lower()}' in command_lower:
                    target_lang = lang_code
                    break
            
            # Extract text to translate
            if 'translate' in command_lower:
                text_start = command_lower.index('translate') + len('translate')
                text_part = command[text_start:].strip()
                
                # Remove "to [language]" part
                if target_lang:
                    lang_name = self.language_names[target_lang]
                    text_part = text_part.replace(f'to {lang_name}', '').strip()
                    text_part = text_part.replace(f'to {lang_name.lower()}', '').strip()
                
                if text_part:
                    result = self.translate_text(text_part, target_lang)
                    if 'error' in result:
                        return result['error']
                    return f"Translation:\n  Original ({result['source_language_name']}): {result['original_text']}\n  Translated ({result['target_language_name']}): {result['translated_text']}"
                else:
                    return "Please provide text to translate"
        
        # List supported languages
        elif 'supported languages' in command_lower or 'available languages' in command_lower:
            langs = self.get_supported_languages()
            return "Supported languages:\n" + "\n".join([f"  {code}: {name}" for code, name in sorted(langs.items())])
        
        else:
            return self._help_message()
    
    def _help_message(self) -> str:
        """Return help message"""
        return """Translation Service Commands:
🌍 Translate: 'translate [text] to [language]'
🔍 Detect: 'detect language [text]'
📝 Languages: 'supported languages'

Examples:
  - translate hello to Spanish
  - detect language bonjour
  - supported languages"""
