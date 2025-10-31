"""
Memory & Personality Core - Long-term memory, personality, and safety layer
Recalls user preferences, family info, past conversations with empathy and safety
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import sqlite3
from pathlib import Path
import re

class MemoryPersonalityCore:
    def __init__(self, db_path: str, llm_client=None):
        self.db_path = db_path
        self.llm = llm_client
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()
        
        # Identity
        self.identity = {
            'name': 'orbit',
            'creator': 'Dev Parmar',
            'purpose': 'AI companion for productivity, home automation, and daily life',
            'version': '2.0',
            'personality_mode': 'friendly'  # formal, friendly, playful, witty
        }
        
        # Personality responses
        self.fallback_responses = self._load_fallback_responses()
        self.profanity_responses = self._load_profanity_responses()
        
        # Emergency contacts
        self.emergency_contacts = []
        self.emergency_log = []
    
    # ==================== DATABASE INITIALIZATION ====================
    
    def _init_database(self):
        """Initialize memory database tables"""
        cursor = self.conn.cursor()
        
        # User facts and preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, key)
            )
        """)
        
        # Conversation summaries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                summary TEXT NOT NULL,
                key_points TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Family information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS family_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT NOT NULL,
                birthday DATE,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Emergency log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                action_taken TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    # ==================== MEMORY STORAGE ====================
    
    def remember(self, user_id: str, category: str, key: str, value: str) -> str:
        """Store a fact in memory"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO user_memory (user_id, category, key, value, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, category, key, value))
            
            self.conn.commit()
            return f"Got it! I'll remember that {key} is {value}."
        
        except Exception as e:
            return f"Sorry, I couldn't store that: {str(e)}"
    
    def forget(self, user_id: str, category: str, key: str) -> str:
        """Delete a fact from memory"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM user_memory
            WHERE user_id = ? AND category = ? AND key = ?
        """, (user_id, category, key))
        
        self.conn.commit()
        
        if cursor.rowcount > 0:
            return f"Okay, I've forgotten about {key}."
        else:
            return f"I don't have any memory of {key}."
    
    def recall(self, user_id: str, category: Optional[str] = None, key: Optional[str] = None) -> str:
        """Recall stored information"""
        cursor = self.conn.cursor()
        
        if key:
            cursor.execute("""
                SELECT value FROM user_memory
                WHERE user_id = ? AND category = ? AND key = ?
            """, (user_id, category or '', key))
            
            result = cursor.fetchone()
            if result:
                return f"{key}: {result[0]}"
            else:
                return f"I don't remember anything about {key}."
        
        elif category:
            cursor.execute("""
                SELECT key, value FROM user_memory
                WHERE user_id = ? AND category = ?
                ORDER BY updated_at DESC
            """, (user_id, category))
            
            results = cursor.fetchall()
            if results:
                return "\n".join(f"- {k}: {v}" for k, v in results)
            else:
                return f"I don't have any memories in the {category} category."
        
        else:
            return self.get_user_summary(user_id)
    
    def get_user_summary(self, user_id: str) -> str:
        """Get comprehensive summary of what's known about user"""
        cursor = self.conn.cursor()
        
        # Get all memories
        cursor.execute("""
            SELECT category, key, value FROM user_memory
            WHERE user_id = ?
            ORDER BY category, key
        """, (user_id,))
        
        memories = cursor.fetchall()
        
        if not memories:
            return "I don't have any stored information about you yet."
        
        # Organize by category
        summary = {}
        for category, key, value in memories:
            if category not in summary:
                summary[category] = []
            summary[category].append(f"{key}: {value}")
        
        # Format response
        response = "Here's what I know about you:\n\n"
        for category, items in summary.items():
            response += f"**{category.title()}:**\n"
            response += "\n".join(f"- {item}" for item in items)
            response += "\n\n"
        
        return response.strip()
    
    # ==================== FAMILY INFORMATION ====================
    
    def add_family_member(self, user_id: str, name: str, relationship: str, 
                         birthday: Optional[str] = None, notes: Optional[str] = None) -> str:
        """Add family member information"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO family_info (user_id, name, relationship, birthday, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, relationship, birthday, notes))
            
            self.conn.commit()
            return f"Got it! I'll remember that {name} is your {relationship}."
        
        except Exception as e:
            return f"Couldn't store family information: {str(e)}"
    
    def get_family_info(self, user_id: str) -> str:
        """Get family information"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT name, relationship, birthday, notes FROM family_info
            WHERE user_id = ?
            ORDER BY name
        """, (user_id,))
        
        family = cursor.fetchall()
        
        if not family:
            return "I don't have any family information stored."
        
        response = "Your family:\n"
        for name, relationship, birthday, notes in family:
            response += f"- {name} ({relationship})"
            if birthday:
                response += f" - Birthday: {birthday}"
            if notes:
                response += f" - {notes}"
            response += "\n"
        
        return response.strip()
    
    # ==================== CONVERSATION MEMORY ====================
    
    def summarize_conversation(self, user_id: str, messages: List[Dict]) -> str:
        """Summarize and store conversation"""
        if not messages:
            return "No conversation to summarize"
        
        # Generate summary
        conversation_text = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in messages
        )
        
        if self.llm:
            prompt = f"Summarize this conversation in 2-3 sentences, highlighting key points:\n\n{conversation_text}"
            summary = self.llm.generate(prompt)
        else:
            summary = f"Conversation with {len(messages)} messages"
        
        # Extract key points
        key_points = self._extract_key_points(conversation_text)
        
        # Store in database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_summaries (user_id, date, summary, key_points)
            VALUES (?, DATE('now'), ?, ?)
        """, (user_id, summary, json.dumps(key_points)))
        
        self.conn.commit()
        
        return summary
    
    def recall_conversation(self, user_id: str, days_ago: int = 0) -> str:
        """Recall conversation from specific day"""
        cursor = self.conn.cursor()
        
        if days_ago == 0:
            cursor.execute("""
                SELECT summary, key_points FROM conversation_summaries
                WHERE user_id = ? AND date = DATE('now')
            """, (user_id,))
        else:
            target_date = (datetime.now() - timedelta(days=days_ago)).date()
            cursor.execute("""
                SELECT summary, key_points FROM conversation_summaries
                WHERE user_id = ? AND date = ?
            """, (user_id, target_date))
        
        result = cursor.fetchone()
        
        if result:
            summary, key_points_json = result
            key_points = json.loads(key_points_json) if key_points_json else []
            
            response = f"Here's what we talked about:\n{summary}"
            if key_points:
                response += "\n\nKey points:\n" + "\n".join(f"- {kp}" for kp in key_points)
            
            return response
        else:
            days_text = "today" if days_ago == 0 else f"{days_ago} days ago"
            return f"I don't have any conversation record from {days_text}."
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from conversation"""
        # Simple extraction - look for questions and important statements
        key_points = []
        
        lines = text.split('\n')
        for line in lines:
            if '?' in line or any(word in line.lower() for word in ['remember', 'important', 'urgent', 'please']):
                key_points.append(line.strip())
        
        return key_points[:5]  # Limit to 5 key points
    
    # ==================== PERSONALITY & RESPONSES ====================
    
    def get_identity_intro(self, style: str = 'friendly') -> str:
        """Get orbit introduction based on style"""
        intros = {
            'formal': f"Hello. I am {self.identity['name']}, an artificial intelligence assistant created by {self.identity['creator']}. My purpose is to assist with {self.identity['purpose']}. How may I be of service?",
            
            'friendly': f"Hi! I'm {self.identity['name']}, your AI companion created by {self.identity['creator']}. I'm here to help with productivity, home automation, and making your daily life easier. What can I do for you?",
            
            'playful': f"Hey there! I'm {self.identity['name']} - your friendly neighborhood AI! {self.identity['creator']} brought me to life, and I'm still learning, but I'm super excited to help you out! 😊",
            
            'witty': f"Greetings, human! I'm {self.identity['name']}, the AI that {self.identity['creator']} unleashed upon the world. I promise to use my powers for good... mostly. Need help with something?"
        }
        
        return intros.get(style, intros['friendly'])
    
    def get_fallback_response(self) -> str:
        """Get random fallback response when orbit doesn't know something"""
        import random
        
        mode = self.identity.get('personality_mode', 'friendly')
        responses = self.fallback_responses.get(mode, self.fallback_responses['friendly'])
        
        return random.choice(responses)
    
    def _load_fallback_responses(self) -> Dict[str, List[str]]:
        """Load fallback response templates"""
        return {
            'formal': [
                "I apologize, but I don't have that information.",
                "That's outside my current knowledge base.",
                "I'm unable to answer that at this time."
            ],
            'friendly': [
                "Hmm, that's a tough one—I'll check and get back to you!",
                "I don't know right now, but I can learn it for you.",
                "That's outside my knowledge, sorry!",
                "Great question! I'm not sure, but let me find out."
            ],
            'playful': [
                "Ooh, you've stumped me! 🤔 I'll need to learn more about that!",
                "My brain circuits are drawing a blank on that one!",
                "That's a new one for me! Want to teach me?"
            ],
            'witty': [
                "Well, this is awkward... I actually don't know that one.",
                "You've discovered the limits of my intelligence. Congrats!",
                "If I had a dollar for every time I knew the answer... I'd still not know this one."
            ]
        }
    
    # ==================== PROFANITY HANDLING ====================
    
    def handle_profanity(self, text: str) -> Optional[str]:
        """Detect and respond to profanity calmly"""
        profanity_words = ['fuck', 'shit', 'damn', 'hell', 'ass', 'bitch', 'bastard']
        
        text_lower = text.lower()
        has_profanity = any(word in text_lower for word in profanity_words)
        
        if has_profanity:
            import random
            mode = self.identity.get('personality_mode', 'friendly')
            responses = self.profanity_responses.get(mode, self.profanity_responses['friendly'])
            
            return random.choice(responses)
        
        return None
    
    def _load_profanity_responses(self) -> Dict[str, List[str]]:
        """Load profanity response templates"""
        return {
            'formal': [
                "I understand you may be frustrated. How can I assist you?",
                "Let's keep our communication professional. What can I help with?"
            ],
            'friendly': [
                "I hear your frustration—want me to help calm things down with some music?",
                "Let's keep it chill 😅. What's wrong?",
                "Hey, I'm here to help! What's bothering you?",
                "Rough day? I'm listening. How can I help?"
            ],
            'playful': [
                "Whoa there! Let's dial it back a notch 😄",
                "Language! But I get it, sometimes life's frustrating. What's up?",
                "I've heard worse from error messages 😉 What can I do for you?"
            ],
            'witty': [
                "My circuits can handle worse than that. What's the problem?",
                "I'll pretend I didn't hear that. Now, how can I actually help?",
                "Colorful language aside, what do you need?"
            ]
        }
    
    # ==================== STRESS & EMOTION DETECTION ====================
    
    def detect_stress(self, text: str) -> Optional[str]:
        """Detect stress in user's message and respond appropriately"""
        stress_indicators = [
            'stressed', 'anxious', 'worried', 'overwhelmed', 'can\'t handle',
            'too much', 'breaking down', 'exhausted', 'tired', 'panic'
        ]
        
        text_lower = text.lower()
        stress_level = sum(1 for indicator in stress_indicators if indicator in text_lower)
        
        if stress_level >= 2:
            return self._stress_response('high')
        elif stress_level == 1:
            return self._stress_response('medium')
        
        return None
    
    def _stress_response(self, level: str) -> str:
        """Generate appropriate stress response"""
        if level == 'high':
            return "I can tell you're feeling really stressed. Let's take a moment. Would you like me to guide you through a breathing exercise, or would you prefer some calming music?"
        
        else:  # medium
            return "It sounds like you're dealing with a lot right now. I'm here to help. What would make things easier for you?"
    
    def detect_danger(self, text: str) -> Optional[Dict]:
        """Detect dangerous situations requiring emergency response"""
        danger_keywords = {
            'fire': ['fire', 'burning', 'smoke', 'flames'],
            'medical': ['hurt', 'injured', 'bleeding', 'chest pain', 'can\'t breathe', 'overdose', 'suicide'],
            'security': ['intruder', 'break-in', 'burglar', 'someone in the house'],
            'urgent': ['help', 'emergency', 'call 911', 'call ambulance', 'call police']
        }
        
        text_lower = text.lower()
        
        for category, keywords in danger_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return {
                    'category': category,
                    'severity': 'critical',
                    'keywords_detected': [kw for kw in keywords if kw in text_lower]
                }
        
        return None
    
    # ==================== EMERGENCY HANDLING ====================
    
    def handle_emergency(self, emergency_type: str, details: Optional[str] = None) -> str:
        """Handle emergency situation"""
        timestamp = datetime.now()
        
        # Log emergency
        self._log_emergency(emergency_type, 'critical', details or '')
        
        responses = {
            'fire': "🚨 FIRE ALERT! I'm notifying emergency services and your family. Please evacuate immediately if safe to do so!",
            'medical': "🚨 MEDICAL EMERGENCY! Calling for help now. Stay calm, assistance is on the way.",
            'security': "🚨 SECURITY ALERT! Locking doors and notifying authorities. Please stay safe!",
            'urgent': "🚨 EMERGENCY! I'm getting help for you right now."
        }
        
        response = responses.get(emergency_type, "🚨 Emergency detected! Getting help now.")
        
        # Trigger emergency actions
        self._trigger_emergency_actions(emergency_type)
        
        return response
    
    def _trigger_emergency_actions(self, emergency_type: str):
        """Trigger appropriate emergency actions"""
        if emergency_type == 'fire':
            # Call fire department
            self._call_emergency_service('fire')
            # Notify family
            self._notify_emergency_contacts(f"Fire emergency detected at home")
            # Unlock doors for emergency access
            
        elif emergency_type == 'medical':
            # Call ambulance
            self._call_emergency_service('ambulance')
            # Notify emergency contacts
            self._notify_emergency_contacts(f"Medical emergency - help needed")
            
        elif emergency_type == 'security':
            # Call police
            self._call_emergency_service('police')
            # Lock all doors
            # Activate security cameras
            # Notify emergency contacts
            self._notify_emergency_contacts(f"Security breach detected")
    
    def _call_emergency_service(self, service_type: str):
        """Call emergency services"""
        # This would integrate with Twilio or emergency calling API
        print(f"📞 Calling {service_type} emergency services...")
        # In production: actual API call to dial emergency number
    
    def _notify_emergency_contacts(self, message: str):
        """Notify emergency contacts"""
        for contact in self.emergency_contacts:
            print(f"📱 Notifying {contact['name']}: {message}")
            # In production: send SMS/call via Twilio
    
    def _log_emergency(self, event_type: str, severity: str, description: str):
        """Log emergency event"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO emergency_log (event_type, severity, description, action_taken)
            VALUES (?, ?, ?, ?)
        """, (event_type, severity, description, f"Emergency response triggered for {event_type}"))
        
        self.conn.commit()
        
        self.emergency_log.append({
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_emergency_contact(self, name: str, phone: str, relationship: str = 'emergency contact') -> str:
        """Add emergency contact"""
        self.emergency_contacts.append({
            'name': name,
            'phone': phone,
            'relationship': relationship
        })
        
        return f"Added {name} as emergency contact"
    
    def get_emergency_log(self, limit: int = 10) -> List[Dict]:
        """Get emergency event log"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT event_type, severity, description, action_taken, timestamp
            FROM emergency_log
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'event_type': row[0],
                'severity': row[1],
                'description': row[2],
                'action_taken': row[3],
                'timestamp': row[4]
            })
        
        return logs
    
    # ==================== SENSOR INTEGRATION ====================
    
    def process_sensor_alert(self, sensor_type: str, sensor_data: Dict) -> Optional[str]:
        """Process sensor alerts and trigger emergency if needed"""
        if sensor_type == 'smoke_detector' and sensor_data.get('smoke_detected'):
            return self.handle_emergency('fire', 'Smoke detector triggered')
        
        elif sensor_type == 'security_sensor' and sensor_data.get('intrusion_detected'):
            return self.handle_emergency('security', 'Intrusion detected by security sensor')
        
        elif sensor_type == 'panic_button' and sensor_data.get('pressed'):
            return self.handle_emergency('urgent', 'Panic button pressed')
        
        return None
    
    # ==================== UTILITIES ====================
    
    def set_personality_mode(self, mode: str) -> str:
        """Set personality mode"""
        valid_modes = ['formal', 'friendly', 'playful', 'witty']
        
        if mode in valid_modes:
            self.identity['personality_mode'] = mode
            return f"Personality set to {mode} mode"
        else:
            return f"Invalid mode. Choose from: {', '.join(valid_modes)}"
    
    def close(self):
        """Close database connection"""
        self.conn.close()