"""
Voice-Controlled Email Assistant for Orbit
Integrates email operations with voice commands and LLM for natural conversation
Optimized for Qwen 2.5 3B with conversation state management
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from .communication import CommunicationService


class EmailVoiceAssistant:
    """
    Voice-controlled email assistant with conversation state management
    Handles: check emails, reply, compose, context tracking
    """
    
    def __init__(self, communication_service: CommunicationService, llm_router, settings):
        self.comm = communication_service
        self.llm = llm_router
        self.settings = settings
        
        # Conversation state management
        self.state = {
            'mode': 'idle',  # idle, email_check, email_reply, email_compose
            'active_email': None,  # Currently referenced email
            'recent_emails': [],  # Last 3 emails for context
            'draft_email': None,  # Draft being composed
            'pending_send': False,  # Waiting for send confirmation
            'reply_body': None,  # Generated reply text
            'last_command_time': None
        }
        
        # Keywords for intent detection
        self.check_keywords = ['check email', 'read email', 'new email', 'unread email', 
                               'any email', 'get email', 'show email', 'how many email']
        
        self.reply_keywords = ['reply', 'respond', 'answer that', 'reply to', 'send reply']
        
        self.compose_keywords = ['compose', 'send email to', 'email', 'write email', 'new email to']
        
        self.confirmation_yes = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'send it', 
                                 'confirm', 'go ahead', 'send']
        
        self.confirmation_no = ['no', 'nope', 'cancel', 'don\'t send', 'stop', 'nevermind', 'never mind']
        
    def reset_state(self):
        """Reset conversation state"""
        self.state = {
            'mode': 'idle',
            'active_email': None,
            'recent_emails': [],
            'draft_email': None,
            'pending_send': False,
            'reply_body': None,
            'last_command_time': datetime.now()
        }
    
    def is_email_command(self, query: str) -> bool:
        """Check if query is email-related"""
        query_lower = query.lower()
        
        all_keywords = self.check_keywords + self.reply_keywords + self.compose_keywords
        return any(keyword in query_lower for keyword in all_keywords)
    
    def process_voice_command(self, query: str) -> str:
        """
        Main entry point for voice email commands
        Returns: Response string for TTS
        """
        query_lower = query.lower().strip()
        
        # Check for confirmation if pending send
        if self.state['pending_send']:
            return self._handle_confirmation(query_lower)
        
        # Detect command type
        if any(keyword in query_lower for keyword in self.check_keywords):
            return self._check_emails(query_lower)
        
        elif any(keyword in query_lower for keyword in self.reply_keywords):
            return self._reply_to_email(query_lower)
        
        elif any(keyword in query_lower for keyword in self.compose_keywords):
            return self._compose_email(query_lower)
        
        # Context-aware commands
        elif self.state['mode'] == 'email_check':
            # User might reference email by number or sender
            return self._handle_email_selection(query_lower)
        
        elif self.state['mode'] == 'email_reply':
            # User might be providing reply content
            return self._handle_reply_content(query_lower)
        
        else:
            return "I'm not sure what you want me to do. Try saying 'check emails' or 'reply to that email'."
    
    def _check_emails(self, query: str) -> str:
        """Check and read emails"""
        # Determine if unread only
        unread_only = 'unread' in query or 'new' in query
        
        # Fetch emails
        emails = self.comm.read_emails(unread_only=unread_only, limit=5)
        
        if not emails or 'error' in emails[0]:
            error_msg = emails[0].get('error', 'Could not fetch emails') if emails else 'No emails found'
            return f"Sorry, {error_msg}"
        
        # Store recent emails for context
        self.state['recent_emails'] = emails[:3]
        self.state['mode'] = 'email_check'
        
        count = len(emails)
        email_type = "unread" if unread_only else "recent"
        
        # Build voice-friendly response
        response = f"You have {count} {email_type} email"
        response += "s. " if count != 1 else ". "
        
        # Summarize up to 3 emails
        for i, email in enumerate(emails[:3], 1):
            from_name = email.get('from_name') or email.get('from', 'Unknown').split('@')[0]
            subject = email.get('subject', 'No subject')
            
            # Priority indicator
            priority = "Urgent: " if email.get('priority') == 'high' else ""
            
            response += f"{priority}From {from_name}: {subject}. "
        
        if count > 3:
            response += f"And {count - 3} more emails."
        
        return response
    
    def _reply_to_email(self, query: str) -> str:
        """Handle reply command"""
        # Check if we have context of recent emails
        if not self.state['recent_emails']:
            return "I don't have any recent emails loaded. Say 'check emails' first."
        
        # Determine which email to reply to
        email_to_reply = self._select_email_from_query(query)
        
        if not email_to_reply:
            # Ask for clarification
            if len(self.state['recent_emails']) > 1:
                names = [e.get('from_name', e.get('from', 'Unknown').split('@')[0]) 
                        for e in self.state['recent_emails']]
                return f"Which email? I have emails from {', '.join(names)}. Say 'reply to' followed by the name."
            else:
                email_to_reply = self.state['recent_emails'][0]
        
        self.state['active_email'] = email_to_reply
        self.state['mode'] = 'email_reply'
        
        # Extract reply content from query
        reply_content = self._extract_reply_content(query)
        
        if reply_content:
            # Generate formal email with LLM
            return self._generate_reply(reply_content, email_to_reply)
        else:
            # Ask for reply content
            from_name = email_to_reply.get('from_name', email_to_reply.get('from', 'Unknown'))
            return f"What would you like to say to {from_name}?"
    
    def _select_email_from_query(self, query: str) -> Optional[Dict]:
        """Select email based on query context"""
        # Check for "first", "last", "latest", etc.
        if 'first' in query or 'latest' in query or 'newest' in query or 'most recent' in query:
            return self.state['recent_emails'][0]
        
        if 'second' in query and len(self.state['recent_emails']) > 1:
            return self.state['recent_emails'][1]
        
        if 'third' in query and len(self.state['recent_emails']) > 2:
            return self.state['recent_emails'][2]
        
        if 'last' in query:
            return self.state['recent_emails'][-1]
        
        # Check for name in query
        for email in self.state['recent_emails']:
            from_name = email.get('from_name', '').lower()
            from_addr = email.get('from', '').lower()
            
            if from_name and from_name in query:
                return email
            
            if from_addr:
                name_part = from_addr.split('@')[0].lower()
                if name_part in query:
                    return email
        
        return None
    
    def _extract_reply_content(self, query: str) -> Optional[str]:
        """Extract reply message from query"""
        # Remove reply keywords
        content = query
        
        for keyword in self.reply_keywords:
            content = content.replace(keyword, '')
        
        # Remove "that" references
        content = re.sub(r'\bthat\s+email\b', '', content)
        content = re.sub(r'\bthe\s+email\b', '', content)
        content = re.sub(r'\bto\s+\w+@[\w\.]+\b', '', content)  # Remove email addresses
        
        # Remove leading/trailing "to", "that", etc.
        content = content.strip(' ,.:;!?to')
        
        # Check if there's actual content
        if len(content) > 5:
            return content
        
        return None
    
    def _generate_reply(self, casual_message: str, email_data: Dict) -> str:
        """Generate formal email reply using LLM"""
        # Build context for LLM
        from_name = email_data.get('from_name', email_data.get('from', 'Unknown'))
        subject = email_data.get('subject', 'Your email')
        original_body = email_data.get('body', '')[:200]  # First 200 chars for context
        
        # LLM prompt for formal email generation
        prompt = f"""Convert this casual message into a professional email reply.

Original email subject: {subject}
From: {from_name}
Original message excerpt: {original_body[:100]}...

Casual message: "{casual_message}"

Generate a formal, professional email reply. Keep it concise (2-4 sentences). Include:
1. Appropriate greeting (Hi/Dear {from_name})
2. Professional version of the casual message
3. Polite closing (Best regards/Thank you)

Reply:"""
        
        try:
            # Generate formal reply with LLM (streaming)
            formal_reply_parts = []
            for chunk in self.llm.generate(prompt, context=None):
                formal_reply_parts.append(chunk)
            
            formal_reply = ''.join(formal_reply_parts).strip()
            
            # Store draft
            self.state['reply_body'] = formal_reply
            self.state['pending_send'] = True
            
            # Return confirmation request
            response = f"I've prepared this reply: {formal_reply}. "
            response += "Should I send it? Say yes to send or no to cancel."
            
            return response
            
        except Exception as e:
            return f"Sorry, I had trouble generating the reply: {str(e)}"
    
    def _handle_confirmation(self, query: str) -> str:
        """Handle send confirmation"""
        # Check for yes/no
        is_yes = any(word in query for word in self.confirmation_yes)
        is_no = any(word in query for word in self.confirmation_no)
        
        if is_yes:
            return self._send_reply()
        elif is_no:
            self.reset_state()
            return "Okay, I've cancelled the email. What else can I help with?"
        else:
            return "I didn't catch that. Say yes to send or no to cancel."
    
    def _send_reply(self) -> str:
        """Actually send the email reply"""
        if not self.state['active_email'] or not self.state['reply_body']:
            return "Sorry, I lost the email context. Let's start over."
        
        email_data = self.state['active_email']
        to_address = email_data.get('from')
        
        # Get original subject and add Re: if needed
        subject = email_data.get('subject', 'Your email')
        if not subject.lower().startswith('re:'):
            subject = f"Re: {subject}"
        
        # Send via communication service
        result = self.comm.send_email(
            to=to_address,
            subject=subject,
            body=self.state['reply_body']
        )
        
        if result.get('status') == 'sent':
            from_name = email_data.get('from_name', to_address.split('@')[0])
            self.reset_state()
            return f"Email sent to {from_name}!"
        else:
            error = result.get('error', 'Unknown error')
            return f"Sorry, the email failed to send: {error}"
    
    def _compose_email(self, query: str) -> str:
        """Compose new email"""
        # Extract recipient and content
        match = re.search(r'(?:email|send)\s+(?:to\s+)?([^\s]+@[^\s]+)', query)
        
        if not match:
            # No email address found
            # Try to find name and ask for email
            return "Who would you like to email? Please include their email address."
        
        recipient = match.group(1)
        
        # Extract message content
        content = query.split(recipient)[-1].strip(' ,.:;!?')
        
        if len(content) < 5:
            self.state['draft_email'] = {'to': recipient}
            return f"What would you like to say to {recipient}?"
        
        # Generate formal email
        prompt = f"""Convert this casual message into a professional email.

Recipient: {recipient}
Casual message: "{content}"

Generate a formal, professional email. Keep it concise. Include:
1. Appropriate greeting
2. Professional version of the message
3. Polite closing

Email:"""
        
        try:
            formal_email_parts = []
            for chunk in self.llm.generate(prompt, context=None):
                formal_email_parts.append(chunk)
            
            formal_email = ''.join(formal_email_parts).strip()
            
            self.state['draft_email'] = {
                'to': recipient,
                'subject': self._extract_subject_from_content(content),
                'body': formal_email
            }
            self.state['pending_send'] = True
            
            return f"I've prepared this email to {recipient}: {formal_email}. Should I send it?"
            
        except Exception as e:
            return f"Sorry, I had trouble composing the email: {str(e)}"
    
    def _extract_subject_from_content(self, content: str) -> str:
        """Generate email subject from content"""
        # Use first few words or let LLM generate
        words = content.split()[:5]
        subject = ' '.join(words)
        
        if len(subject) > 50:
            subject = subject[:47] + "..."
        
        return subject
    
    def _handle_email_selection(self, query: str) -> str:
        """Handle email selection in check mode"""
        email = self._select_email_from_query(query)
        
        if email:
            self.state['active_email'] = email
            
            # Read full email
            from_name = email.get('from_name', email.get('from', 'Unknown'))
            subject = email.get('subject', 'No subject')
            body = email.get('body', 'No content')[:500]
            
            return f"Email from {from_name}. Subject: {subject}. Message: {body}. Would you like to reply?"
        else:
            return "I couldn't find that email. Try saying 'first email' or 'email from [name]'."
    
    def _handle_reply_content(self, query: str) -> str:
        """Handle reply content in reply mode"""
        if not self.state['active_email']:
            return "I don't have an email selected. Say 'check emails' first."
        
        # User is providing reply content
        return self._generate_reply(query, self.state['active_email'])
    
    def get_state_summary(self) -> str:
        """Get current state for debugging"""
        return f"Mode: {self.state['mode']}, Pending: {self.state['pending_send']}, Recent emails: {len(self.state['recent_emails'])}"


# Integration helper functions for source_selector.py

def create_email_assistant(settings, llm_router, communication_service):
    """Factory function to create email assistant"""
    return EmailVoiceAssistant(communication_service, llm_router, settings)


def is_email_voice_command(query: str) -> bool:
    """Quick check if query is email-related (for intent classification)"""
    email_keywords = [
        'check email', 'read email', 'new email', 'unread email',
        'reply', 'reply to', 'send reply', 'answer email',
        'compose email', 'send email to', 'write email'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in email_keywords)
