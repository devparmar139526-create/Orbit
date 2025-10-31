def _check_theme_allowed(self, theme: str) -> bool:
        """Check if theme is allowed"""
        blocked = self.parental_settings.get('blocked_themes', [])
        return theme.lower() not in blocked
    
    # ==================== PARENTAL CONTROLS ====================
    
    def update_parental_settings(self, settings: Dict) -> str:
        """Update parental control settings"""
        self.parental_settings.update(settings)
        return "Parental settings updated"
    
    def get_parental_settings(self) -> Dict:
        """Get current parental settings"""
        return self.parental_settings
    
    def get_story_history(self, limit: int = 20) -> List[Dict]:
        """Get story generation history"""
        stories = list(self.stories.values())
        return stories[-limit:]
    
    def delete_story(self, story_id: str) -> str:
        """Delete a story"""
        if story_id in self.stories:
            del self.stories[story_id]
            # Also delete from disk
            try:
                stories_dir = Path.home() / "Documents" / "orbit_Stories"
                filepath = stories_dir / f"{story_id}.json"
                if filepath.exists():
                    filepath.unlink()
            except:
                pass
            
            return f"Story {story_id} deleted"
        return "Story not found"
    
    # ==================== UTILITIES ====================
    
    def _validate_params(self, params: Dict) -> bool:
        """Validate story generation parameters"""
        required = ['child_name', 'age_group']
        
        for field in required:
            if field not in params:
                print(f"Missing required field: {field}")
                return False
        
        # Validate age
        age = params.get('age_group', 0)
        if not isinstance(age, int) or age < 3 or age > 12:
            print("Age group must be between 3 and 12")
            return False
        
        return True
    
    def _parse_story_json(self, response: str) -> Optional[Dict]:
        """Parse story JSON from LLM response"""
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except"""
AI Storyteller for Kids - Generate safe, interactive bedtime stories
Age-appropriate stories with TTS playback and branching choices
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import re
from pathlib import Path

class StorytellerForKids:
    def __init__(self, llm_client, tts_dispatcher):
        self.llm = llm_client
        self.tts = tts_dispatcher
        
        # Story storage
        self.stories = {}
        self.story_sessions = {}
        
        # Content filter
        self.banned_words = self._load_content_filter()
        
        # Parental controls
        self.parental_settings = {
            'enabled': True,
            'child_mode': 'reading_only',  # reading_only, interactive, parent_approval
            'max_story_length': 600,  # seconds
            'allowed_themes': ['adventure', 'friendship', 'animals', 'magic', 'nature'],
            'blocked_themes': ['scary', 'violence'],
            'save_stories': True
        }
    
    # ==================== STORY GENERATION ====================
    
    def generate_story(self, params: Dict) -> Dict:
        """
        Generate a new story
        
        params = {
            'child_name': 'Aarav',
            'age_group': 5,
            'characters': ['kitten', 'dragon'],
            'mood': 'calm',  # calm, funny, exciting
            'length_seconds': 300,
            'theme': 'friendship',
            'moral': 'sharing is caring',
            'language': 'en',
            'interactive': False
        }
        """
        # Validate inputs
        if not self._validate_params(params):
            return {'error': 'Invalid parameters'}
        
        # Check content safety
        if not self._check_theme_allowed(params.get('theme', '')):
            return {'error': f"Theme '{params.get('theme')}' not allowed in parental settings"}
        
        # Generate story using LLM
        story_data = self._generate_with_llm(params)
        
        if not story_data:
            return {'error': 'Story generation failed'}
        
        # Content filter check
        if not self._content_filter(story_data.get('text', '')):
            return {'error': 'Story failed content safety check'}
        
        # Create story ID
        story_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        story_data['story_id'] = story_id
        story_data['created_at'] = datetime.now().isoformat()
        story_data['params'] = params
        
        # Store story
        self.stories[story_id] = story_data
        
        # Save if enabled
        if self.parental_settings['save_stories']:
            self._save_story(story_id, story_data)
        
        return story_data
    
    def _generate_with_llm(self, params: Dict) -> Optional[Dict]:
        """Generate story using LLM"""
        if not self.llm:
            return self._generate_fallback_story(params)
        
        # Build prompt
        child_name = params.get('child_name', 'a child')
        age_group = params.get('age_group', 5)
        characters = params.get('characters', ['bunny'])
        mood = params.get('mood', 'calm')
        theme = params.get('theme', 'friendship')
        moral = params.get('moral', '')
        length_seconds = params.get('length_seconds', 300)
        interactive = params.get('interactive', False)
        
        # Estimate word count (average reading speed: 150 words/min)
        words_needed = int((length_seconds / 60) * 150)
        
        system_prompt = """You are a children's story author. Produce safe, age-appropriate stories.
Never include violence, scary descriptions, adult themes, or inappropriate content.
Focus on positive messages, friendship, kindness, and gentle adventures."""
        
        user_prompt = f"""Generate a {length_seconds}-second bedtime story for a {age_group}-year-old named {child_name}.

Story requirements:
- Include characters: {', '.join(characters)}
- Tone: {mood}
- Theme: {theme}
- Include a gentle moral: {moral if moral else 'kindness and friendship'}
- Length: approximately {words_needed} words
- Break into 4-6 short scenes
{'- Include 1-2 child-friendly choices per scene for interactive storytelling' if interactive else ''}

Return in JSON format:
{{
  "title": "story title",
  "summary": "one-line summary",
  "scenes": [
    {{
      "id": 1,
      "text": "scene text",
      "choices": [{{"key": "A", "text": "choice text"}}]  # only if interactive
    }}
  ],
  "moral": "the lesson",
  "age_group": {age_group}
}}

Make it warm, engaging, and perfect for bedtime."""
        
        try:
            response = self.llm.generate(user_prompt)
            
            # Parse JSON from response
            story_data = self._parse_story_json(response)
            
            if story_data:
                # Add full text
                story_data['text'] = '\n\n'.join(
                    scene['text'] for scene in story_data.get('scenes', [])
                )
                return story_data
        
        except Exception as e:
            print(f"Story generation error: {e}")
        
        return None
    
    def _generate_fallback_story(self, params: Dict) -> Dict:
        """Generate a simple template story when LLM unavailable"""
        child_name = params.get('child_name', 'a child')
        characters = params.get('characters', ['bunny'])
        main_char = characters[0] if characters else 'bunny'
        
        story = {
            'title': f"The Adventure of {main_char.title()}",
            'summary': f"A gentle tale about a friendly {main_char}",
            'scenes': [
                {
                    'id': 1,
                    'text': f"Once upon a time, there was a kind little {main_char} named Fluffy. Fluffy lived in a cozy home with lots of friends."
                },
                {
                    'id': 2,
                    'text': f"One sunny day, Fluffy decided to explore the nearby meadow. The flowers were blooming and butterflies danced in the air."
                },
                {
                    'id': 3,
                    'text': f"Fluffy met a wise old owl who shared a wonderful secret about being a good friend."
                },
                {
                    'id': 4,
                    'text': f"Fluffy learned that sharing and kindness make everyone happy. And from that day on, Fluffy always remembered to be kind."
                }
            ],
            'moral': 'Kindness and sharing make the world a better place',
            'age_group': params.get('age_group', 5)
        }
        
        story['text'] = '\n\n'.join(scene['text'] for scene in story['scenes'])
        return story
    
    # ==================== INTERACTIVE STORYTELLING ====================
    
    def start_interactive_session(self, story_id: str) -> Dict:
        """Start an interactive storytelling session"""
        if story_id not in self.stories:
            return {'error': 'Story not found'}
        
        story = self.stories[story_id]
        
        session = {
            'story_id': story_id,
            'current_scene': 0,
            'path_taken': [],
            'started_at': datetime.now().isoformat()
        }
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.story_sessions[session_id] = session
        
        return {
            'session_id': session_id,
            'scene': story['scenes'][0]
        }
    
    def make_choice(self, session_id: str, choice_key: str) -> Dict:
        """Process user's choice in interactive story"""
        if session_id not in self.story_sessions:
            return {'error': 'Session not found'}
        
        session = self.story_sessions[session_id]
        story = self.stories[session['story_id']]
        
        # Record choice
        session['path_taken'].append({
            'scene': session['current_scene'],
            'choice': choice_key
        })
        
        # Get current scene
        current_scene = story['scenes'][session['current_scene']]
        
        # Generate next scene based on choice
        next_scene = self._generate_next_scene(story, current_scene, choice_key)
        
        # Add to story scenes
        scene_id = len(story['scenes']) + 1
        next_scene['id'] = scene_id
        story['scenes'].append(next_scene)
        
        session['current_scene'] = scene_id - 1
        
        return {
            'session_id': session_id,
            'scene': next_scene,
            'is_ending': len(story['scenes']) >= 10  # Max 10 scenes
        }
    
    def _generate_next_scene(self, story: Dict, current_scene: Dict, choice: str) -> Dict:
        """Generate next scene based on choice"""
        if not self.llm:
            return {
                'text': "And so the adventure continued, bringing more joy and wonder...",
                'choices': []
            }
        
        prompt = f"""Continue this children's story based on the choice made:

Story so far: {story.get('summary')}
Current scene: {current_scene.get('text')}
Child chose: {choice}

Generate the next scene (2-3 sentences) that follows naturally from this choice.
Keep it age-appropriate, gentle, and positive.
Include 1-2 new choices for what happens next.

Return JSON:
{{
  "text": "next scene text",
  "choices": [{{"key": "A", "text": "choice 1"}}, {{"key": "B", "text": "choice 2"}}]
}}"""
        
        try:
            response = self.llm.generate(prompt)
            scene_data = self._parse_scene_json(response)
            return scene_data if scene_data else {'text': 'The story continues...', 'choices': []}
        except:
            return {'text': 'The story continues...', 'choices': []}
    
    # ==================== TEXT-TO-SPEECH ====================
    
    def narrate_story(self, story_id: str) -> str:
        """Narrate entire story using TTS"""
        if story_id not in self.stories:
            return "Story not found"
        
        story = self.stories[story_id]
        
        # Create narration
        narration = f"{story['title']}.\n\n"
        narration += story['text']
        narration += f"\n\nThe end. Remember: {story['moral']}"
        
        # Speak using TTS
        self.tts.speak(narration)
        
        return "Story narrated successfully"
    
    def narrate_scene(self, story_id: str, scene_id: int) -> str:
        """Narrate a single scene"""
        if story_id not in self.stories:
            return "Story not found"
        
        story = self.stories[story_id]
        scenes = story.get('scenes', [])
        
        if scene_id >= len(scenes):
            return "Scene not found"
        
        scene = scenes[scene_id]
        self.tts.speak(scene['text'])
        
        # If choices, read them
        choices = scene.get('choices', [])
        if choices:
            self.tts.speak("What should happen next?")
            for choice in choices:
                self.tts.speak(f"Option {choice['key']}: {choice['text']}")
        
        return "Scene narrated"
    
    # ==================== CONTENT SAFETY ====================
    
    def _content_filter(self, text: str) -> bool:
        """Check content for safety"""
        text_lower = text.lower()
        
        # Check banned words
        for word in self.banned_words:
            if word in text_lower:
                print(f"Content filter: