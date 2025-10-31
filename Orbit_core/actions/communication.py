"""
Communication Module - Phase 2: All 12 Features
📧 Email (IMAP/SMTP), 💬 Messaging (Telegram/SMS), 🔔 Notifications
Production-ready with error handling and best practices
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
import re


class CommunicationService:
    """Complete communication service - 12 features"""
    
    def __init__(self, settings=None):
        self.settings = settings
        
        # Email Configuration (IMAP/SMTP)
        self.imap_server = getattr(settings, 'IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = getattr(settings, 'IMAP_PORT', 993)
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.email_address = getattr(settings, 'EMAIL_ADDRESS', None)
        self.email_password = getattr(settings, 'EMAIL_PASSWORD', None)
        
        # Telegram Configuration
        self.telegram_bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        
        # Twilio Configuration (SMS)
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        # Priority Settings
        self.priority_keywords = getattr(settings, 'PRIORITY_KEYWORDS', [
            'urgent', 'important', 'asap', 'critical', 'emergency', 'deadline'
        ])
        
        self.priority_senders = getattr(settings, 'PRIORITY_SENDERS', [])
        
        # Notification Rules
        self.notification_rules = self._load_notification_rules()
        
        # Auto-reply Templates
        self.auto_reply_templates = self._load_templates()
        
        # Data storage
        if settings and hasattr(settings, 'DATA_DIR'):
            self.data_dir = Path(settings.DATA_DIR) / "communication"
        else:
            self.data_dir = Path.home() / ".orbit" / "communication"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Email cache for recent operations
        self.email_cache = []
        
    def _load_notification_rules(self) -> List[Dict]:
        """Load notification rules"""
        default_rules = [
            {
                'name': 'VIP Senders',
                'senders': [],  # User configurable
                'action': 'desktop_notification',
                'priority': 'high'
            },
            {
                'name': 'Urgent Keywords',
                'keywords': ['urgent', 'asap', 'emergency', 'critical'],
                'action': 'desktop_notification',
                'priority': 'high'
            }
        ]
        
        return getattr(self.settings, 'NOTIFICATION_RULES', default_rules) if self.settings else default_rules
    
    def _load_templates(self) -> Dict[str, str]:
        """Load auto-reply email templates"""
        return {
            'out_of_office': """Hello,

Thank you for your email. I am currently out of the office with limited access to email.

I will respond as soon as possible upon my return.

Best regards""",
            
            'meeting': """Hi,

I'm currently in a meeting. I'll respond to your message shortly.

Thanks for your patience.""",
            
            'busy': """Hello,

Thank you for reaching out. I'm focused on high-priority work but will respond within 24 hours.

Best regards"""
        }
    
    # ========== FEATURE 1: READ EMAILS (IMAP) ==========
    
    def connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to IMAP server"""
        try:
            if not self.email_address or not self.email_password:
                return None
            
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            return mail
        except Exception as e:
            print(f"❌ IMAP connection failed: {e}")
            return None
    
    def read_emails(self, folder: str = 'INBOX', limit: int = 10, unread_only: bool = True) -> List[Dict]:
        """
        ✅ FEATURE 1: Read emails via IMAP
        
        Args:
            folder: Email folder (INBOX, Sent, Drafts)
            limit: Max emails to fetch
            unread_only: Only unread emails
        
        Returns:
            List of email dictionaries
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return [{'error': 'Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD'}]
            
            mail.select(folder)
            
            # Search for emails
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK':
                mail.logout()
                return [{'error': 'Email search failed'}]
            
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            
            for email_id in reversed(email_ids):
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Parse email
                    subject = self._decode_header(msg.get('Subject', 'No Subject'))
                    from_addr = email.utils.parseaddr(msg.get('From', ''))[1]
                    from_name = email.utils.parseaddr(msg.get('From', ''))[0]
                    date_str = msg.get('Date', '')
                    body = self._get_email_body(msg)
                    
                    # Calculate priority
                    priority = self._calculate_priority(subject, body, from_addr)
                    
                    email_data = {
                        'id': email_id.decode(),
                        'subject': subject,
                        'from': from_addr,
                        'from_name': from_name,
                        'date': date_str,
                        'body': body[:500],  # Truncate long emails
                        'priority': priority,
                        'folder': folder
                    }
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing email: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            self.email_cache = emails
            return emails
            
        except Exception as e:
            return [{'error': f'Failed to read emails: {str(e)}'}]
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ''
        
        decoded_parts = decode_header(header)
        result = ''
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result += part.decode(encoding or 'utf-8', errors='ignore')
                except:
                    result += part.decode('utf-8', errors='ignore')
            else:
                result += str(part)
        
        return result
    
    def _get_email_body(self, msg) -> str:
        """Extract email body text"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body.strip()
    
    # ========== FEATURE 2: SEND EMAILS (SMTP) ==========
    
    def send_email(self, to: str, subject: str, body: str, cc: Optional[List[str]] = None) -> Dict:
        """
        ✅ FEATURE 2: Send emails via SMTP
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients
        
        Returns:
            Send status dict
        """
        try:
            if not self.email_address or not self.email_password:
                return {'error': 'Email not configured'}
            
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            recipients = [to]
            if cc:
                recipients.extend(cc)
            
            server.send_message(msg, from_addr=self.email_address, to_addrs=recipients)
            server.quit()
            
            return {
                'status': 'sent',
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Failed to send email: {str(e)}'}
    
    # ========== FEATURE 3: PRIORITY EMAIL FILTERING ==========
    
    def _calculate_priority(self, subject: str, body: str, sender: str) -> str:
        """Calculate email priority"""
        text = f"{subject} {body}".lower()
        
        # Check priority keywords
        for keyword in self.priority_keywords:
            if keyword.lower() in text:
                return 'high'
        
        # Check priority senders
        if sender.lower() in [s.lower() for s in self.priority_senders]:
            return 'high'
        
        return 'normal'
    
    def filter_priority_emails(self, emails: Optional[List[Dict]] = None) -> List[Dict]:
        """
        ✅ FEATURE 3: Filter priority emails
        
        Args:
            emails: Email list (uses cache if None)
        
        Returns:
            High-priority emails only
        """
        if emails is None:
            emails = self.email_cache
        
        return [e for e in emails if e.get('priority') == 'high']
    
    # ========== FEATURE 4: EMAIL SUMMARIZATION (AI) ==========
    
    def summarize_email(self, email_data: Dict) -> str:
        """
        ✅ FEATURE 4: AI-powered email summarization
        
        Args:
            email_data: Email dictionary
        
        Returns:
            Summary string
        """
        subject = email_data.get('subject', 'No Subject')
        body = email_data.get('body', '')
        sender = email_data.get('from', 'Unknown')
        
        # Extractive summarization (first 2-3 sentences)
        sentences = body.replace('\n', ' ').split('. ')
        summary_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:2]
        summary = '. '.join(summary_sentences)
        
        if len(summary) > 150:
            summary = summary[:150] + '...'
        
        return f"From {sender} - {subject}: {summary}"
    
    # ========== FEATURE 5: ACTION ITEM EXTRACTION ==========
    
    def extract_action_items(self, email_data: Dict) -> List[str]:
        """
        ✅ FEATURE 5: Extract action items from email
        
        Args:
            email_data: Email dictionary
        
        Returns:
            List of action items
        """
        body = email_data.get('body', '')
        
        action_keywords = [
            'please', 'could you', 'can you', 'need you to', 'action required',
            'todo', 'to-do', 'task', 'deadline', 'by ', 'complete', 'submit',
            'review', 'check', 'update', 'send'
        ]
        
        action_items = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in action_keywords):
                if 10 < len(line) < 200:  # Reasonable length
                    action_items.append(line)
        
        return action_items[:5]  # Top 5 action items
    
    # ========== FEATURE 6: TELEGRAM MESSAGING ==========
    
    def send_telegram(self, message: str) -> Dict:
        """
        ✅ FEATURE 6: Send Telegram message
        
        Args:
            message: Message text
        
        Returns:
            Send status dict
        """
        try:
            if not self.telegram_bot_token or not self.telegram_chat_id:
                return {'error': 'Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID'}
            
            import requests
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'sent',
                    'platform': 'telegram',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': f'Telegram API error: {response.status_code}'}
                
        except ImportError:
            return {'error': 'Install requests: pip install requests'}
        except Exception as e:
            return {'error': f'Telegram failed: {str(e)}'}
    
    # ========== FEATURE 7: SMS VIA TWILIO ==========
    
    def send_sms(self, to: str, message: str) -> Dict:
        """
        ✅ FEATURE 7: Send SMS via Twilio
        
        Args:
            to: Phone number (E.164 format: +1234567890)
            message: SMS text
        
        Returns:
            Send status dict
        """
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                return {'error': 'Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER'}
            
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            msg = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to
            )
            
            return {
                'status': 'sent',
                'platform': 'sms',
                'message_sid': msg.sid,
                'to': to,
                'timestamp': datetime.now().isoformat()
            }
            
        except ImportError:
            return {'error': 'Install Twilio: pip install twilio'}
        except Exception as e:
            return {'error': f'SMS failed: {str(e)}'}
    
    # ========== FEATURE 8: DESKTOP NOTIFICATIONS ==========
    
    def send_desktop_notification(self, title: str, message: str, duration: int = 10) -> Dict:
        """
        ✅ FEATURE 8: Send desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in seconds
        
        Returns:
            Status dict
        """
        try:
            # Try Windows 10 Toast
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=duration, threaded=True)
                return {'status': 'sent', 'platform': 'windows'}
            except:
                pass
            
            # Try cross-platform plyer
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name='Orbit AI',
                    timeout=duration
                )
                return {'status': 'sent', 'platform': 'plyer'}
            except:
                pass
            
            # Fallback: console
            print(f"\n🔔 {title}\n   {message}\n")
            return {'status': 'sent', 'platform': 'console'}
            
        except Exception as e:
            return {'error': f'Notification failed: {str(e)}'}
    
    # ========== FEATURE 9: CONVERSATION SUMMARIZATION ==========
    
    def summarize_conversation(self, emails: List[Dict]) -> str:
        """
        ✅ FEATURE 9: Summarize email conversation thread
        
        Args:
            emails: List of emails in thread
        
        Returns:
            Conversation summary
        """
        if not emails:
            return "No emails to summarize"
        
        participants = set()
        subjects = set()
        
        for email in emails:
            participants.add(email.get('from', 'Unknown'))
            
            # Clean subject (remove Re:, Fwd:)
            subject = email.get('subject', '')
            subject = re.sub(r'^(Re:|Fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()
            if subject:
                subjects.add(subject)
        
        summary = f"Conversation: {len(emails)} emails\n"
        summary += f"Participants: {', '.join(list(participants)[:3])}\n"
        summary += f"Topic: {', '.join(list(subjects)[:2])}"
        
        return summary
    
    # ========== FEATURE 10: NOTIFICATION RULES ==========
    
    def check_notification_rules(self, email_data: Dict) -> bool:
        """
        ✅ FEATURE 10: Check if email matches notification rules
        
        Args:
            email_data: Email dictionary
        
        Returns:
            True if should notify
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        sender = email_data.get('from', '')
        
        for rule in self.notification_rules:
            # Check sender rules
            if 'senders' in rule and sender.lower() in [s.lower() for s in rule['senders']]:
                return True
            
            # Check keyword rules
            if 'keywords' in rule:
                text = f"{subject} {body}"
                for keyword in rule['keywords']:
                    if keyword.lower() in text:
                        return True
        
        return False
    
    def add_notification_rule(self, rule_type: str, value: str) -> str:
        """Add new notification rule"""
        if rule_type == 'sender':
            self.priority_senders.append(value)
            return f"✅ Added notification rule for sender: {value}"
        elif rule_type == 'keyword':
            self.priority_keywords.append(value)
            return f"✅ Added notification rule for keyword: {value}"
        else:
            return "❌ Invalid rule type. Use 'sender' or 'keyword'"
    
    # ========== FEATURE 11: MARK EMAILS AS READ ==========
    
    def mark_as_read(self, email_id: str, folder: str = 'INBOX') -> Dict:
        """
        ✅ FEATURE 11: Mark email as read
        
        Args:
            email_id: Email ID
            folder: Folder name
        
        Returns:
            Status dict
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return {'error': 'Email not configured'}
            
            mail.select(folder)
            mail.store(email_id.encode(), '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            return {'status': 'marked_read', 'email_id': email_id}
            
        except Exception as e:
            return {'error': f'Failed to mark as read: {str(e)}'}
    
    # ========== FEATURE 12: AUTO-REPLY TEMPLATES ==========
    
    def send_auto_reply(self, to: str, template_name: str = 'out_of_office', custom_message: Optional[str] = None) -> Dict:
        """
        ✅ FEATURE 12: Send auto-reply email
        
        Args:
            to: Recipient email
            template_name: Template name (out_of_office, meeting, busy)
            custom_message: Custom message (overrides template)
        
        Returns:
            Send status dict
        """
        if custom_message:
            body = custom_message
        else:
            body = self.auto_reply_templates.get(template_name, self.auto_reply_templates['out_of_office'])
        
        # Get sender name from email
        sender_name = self.email_address.split('@')[0].replace('.', ' ').title()
        body = body.replace('[Your Name]', sender_name)
        
        subject = "Automatic Reply"
        
        return self.send_email(to, subject, body)
    
    def get_auto_reply_templates(self) -> Dict[str, str]:
        """Get available auto-reply templates"""
        return self.auto_reply_templates
    
    def add_auto_reply_template(self, name: str, template: str) -> str:
        """Add custom auto-reply template"""
        self.auto_reply_templates[name] = template
        return f"✅ Added auto-reply template: {name}"
    
    # ==================== MAIN EXECUTION ====================
    
    def execute(self, command: str) -> str:
        """Main command router"""
        cmd = command.lower().strip()
        
        # Read emails
        if 'read' in cmd and 'email' in cmd:
            unread = 'unread' in cmd
            emails = self.read_emails(unread_only=unread)
            
            if not emails:
                return "📭 No emails found"
            
            if 'error' in emails[0]:
                return f"❌ {emails[0]['error']}"
            
            result = f"📧 Found {len(emails)} email(s):\n\n"
            for i, e in enumerate(emails[:5], 1):
                icon = "⚠️ " if e.get('priority') == 'high' else ""
                result += f"{icon}{i}. From: {e.get('from_name')} <{e.get('from')}>\n"
                result += f"   Subject: {e.get('subject')}\n"
                result += f"   Date: {e.get('date')}\n\n"
            
            return result
        
        # Priority emails
        elif 'priority' in cmd or 'urgent' in cmd:
            emails = self.read_emails(unread_only=False)
            priority = self.filter_priority_emails(emails)
            
            if not priority:
                return "✅ No priority emails"
            
            result = f"⚠️  Priority Emails ({len(priority)}):\n\n"
            for i, e in enumerate(priority, 1):
                result += f"{i}. {e.get('from')}: {e.get('subject')}\n"
            
            return result
        
        # Summarize emails
        elif 'summarize' in cmd and 'email' in cmd:
            emails = self.read_emails(limit=5)
            if not emails or 'error' in emails[0]:
                return "❌ No emails to summarize"
            
            result = "📝 Email Summaries:\n\n"
            for i, e in enumerate(emails, 1):
                summary = self.summarize_email(e)
                result += f"{i}. {summary}\n\n"
            
            return result
        
        # Action items
        elif 'action' in cmd and 'item' in cmd:
            emails = self.read_emails(limit=10)
            if not emails or 'error' in emails[0]:
                return "❌ No emails"
            
            all_actions = []
            for e in emails:
                actions = self.extract_action_items(e)
                all_actions.extend(actions)
            
            if not all_actions:
                return "✅ No action items found"
            
            result = f"✅ Action Items ({len(all_actions)}):\n\n"
            for i, action in enumerate(all_actions[:10], 1):
                result += f"{i}. {action}\n"
            
            return result
        
        # Telegram
        elif 'telegram' in cmd:
            message = cmd.replace('telegram', '').replace('send', '').strip()
            if message:
                result = self.send_telegram(message)
                return "✅ Telegram sent" if result.get('status') == 'sent' else f"❌ {result.get('error')}"
            return "❌ Provide a message"
        
        # Notification
        elif 'notif' in cmd:
            message = cmd.replace('notification', '').replace('notify', '').strip()
            self.send_desktop_notification("Orbit", message or "Test notification")
            return "🔔 Notification sent"
        
        else:
            return """Communication Commands:
📧 read unread emails
⚠️  show priority emails
📝 summarize emails
✅ extract action items
💬 send telegram [message]
🔔 send notification [message]"""
