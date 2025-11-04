"""
Communication Module - Complete Suite: 25+ Features
📧 Email (IMAP/SMTP), 💬 Messaging (Telegram/SMS), 🔔 Notifications, 📎 Attachments
Enhanced with AI integration, scheduling, contacts, and advanced filtering
Production-ready with comprehensive error handling and logging
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
import logging
import hashlib
import time
import base64
from collections import defaultdict


class CommunicationService:
    """Complete communication service - 25+ features with AI integration"""
    
    def __init__(self, settings=None, llm_router=None):
        self.settings = settings
        self.llm_router = llm_router  # For AI-powered features
        
        # Setup logging
        self.logger = self._setup_logging()
        
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
        
        # Spam keywords
        self.spam_keywords = getattr(settings, 'SPAM_KEYWORDS', [
            'viagra', 'casino', 'lottery', 'winner', 'claim prize', 'act now',
            'limited time', 'click here', 'unsubscribe', 'free money'
        ])
        
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
        
        # Attachments directory
        self.attachments_dir = self.data_dir / "attachments"
        self.attachments_dir.mkdir(exist_ok=True)
        
        # Contacts database
        self.contacts_file = self.data_dir / "contacts.json"
        self.contacts = self._load_contacts()
        
        # Scheduled emails
        self.scheduled_emails_file = self.data_dir / "scheduled_emails.json"
        self.scheduled_emails = self._load_scheduled_emails()
        
        # Email cache for recent operations
        self.email_cache = []
        self.conversation_threads = {}
        
        # Statistics
        self.stats = {
            'emails_sent': 0,
            'emails_read': 0,
            'notifications_sent': 0,
            'spam_filtered': 0
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logger for communication module"""
        logger = logging.getLogger('orbit.communication')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_contacts(self) -> Dict[str, Dict]:
        """Load contacts database"""
        if self.contacts_file.exists():
            try:
                with open(self.contacts_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_contacts(self):
        """Save contacts to file"""
        try:
            with open(self.contacts_file, 'w') as f:
                json.dump(self.contacts, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save contacts: {e}")
    
    def _load_scheduled_emails(self) -> List[Dict]:
        """Load scheduled emails"""
        if self.scheduled_emails_file.exists():
            try:
                with open(self.scheduled_emails_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_scheduled_emails(self):
        """Save scheduled emails to file"""
        try:
            with open(self.scheduled_emails_file, 'w') as f:
                json.dump(self.scheduled_emails, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save scheduled emails: {e}")
        
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
    
    # ==================== NEW FEATURES ====================
    
    # ========== FEATURE 13: CONTACT MANAGEMENT ==========
    
    def add_contact(self, name: str, email: str, phone: Optional[str] = None, 
                   tags: Optional[List[str]] = None, notes: Optional[str] = None) -> str:
        """
        ✅ NEW FEATURE 13: Add contact to database
        
        Args:
            name: Contact name
            email: Email address
            phone: Phone number (optional)
            tags: Tags/categories (optional)
            notes: Additional notes (optional)
        
        Returns:
            Status message
        """
        contact_id = hashlib.md5(email.lower().encode()).hexdigest()[:8]
        
        self.contacts[contact_id] = {
            'name': name,
            'email': email.lower(),
            'phone': phone,
            'tags': tags or [],
            'notes': notes,
            'added_date': datetime.now().isoformat(),
            'email_count': 0,
            'last_contact': None
        }
        
        self._save_contacts()
        self.logger.info(f"Added contact: {name} <{email}>")
        return f"✅ Added contact: {name} <{email}>"
    
    def get_contact(self, query: str) -> Optional[Dict]:
        """Get contact by name or email"""
        query = query.lower()
        
        for contact_id, contact in self.contacts.items():
            if query in contact['name'].lower() or query in contact['email']:
                return contact
        
        return None
    
    def list_contacts(self, tag: Optional[str] = None) -> List[Dict]:
        """List all contacts, optionally filtered by tag"""
        contacts = list(self.contacts.values())
        
        if tag:
            contacts = [c for c in contacts if tag.lower() in [t.lower() for t in c.get('tags', [])]]
        
        return sorted(contacts, key=lambda x: x['name'])
    
    def update_contact(self, email: str, **kwargs) -> str:
        """Update contact information"""
        contact = self.get_contact(email)
        
        if not contact:
            return f"❌ Contact not found: {email}"
        
        contact_id = hashlib.md5(email.lower().encode()).hexdigest()[:8]
        
        for key, value in kwargs.items():
            if key in ['name', 'phone', 'tags', 'notes']:
                self.contacts[contact_id][key] = value
        
        self._save_contacts()
        return f"✅ Updated contact: {email}"
    
    def delete_contact(self, email: str) -> str:
        """Delete contact from database"""
        contact_id = hashlib.md5(email.lower().encode()).hexdigest()[:8]
        
        if contact_id in self.contacts:
            name = self.contacts[contact_id]['name']
            del self.contacts[contact_id]
            self._save_contacts()
            return f"✅ Deleted contact: {name}"
        
        return f"❌ Contact not found: {email}"
    
    # ========== FEATURE 14: SCHEDULED EMAILS ==========
    
    def schedule_email(self, to: str, subject: str, body: str, 
                      send_at: str, cc: Optional[List[str]] = None) -> Dict:
        """
        ✅ NEW FEATURE 14: Schedule email for later
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            send_at: ISO format datetime or relative (e.g., "2h", "1d")
            cc: CC recipients
        
        Returns:
            Schedule status dict
        """
        try:
            # Parse send_at time
            send_time = self._parse_schedule_time(send_at)
            
            if not send_time:
                return {'error': 'Invalid time format. Use ISO format or relative (e.g., "2h", "1d")'}
            
            scheduled_email = {
                'id': hashlib.md5(f"{to}{subject}{time.time()}".encode()).hexdigest()[:8],
                'to': to,
                'subject': subject,
                'body': body,
                'cc': cc,
                'send_at': send_time.isoformat(),
                'scheduled_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            self.scheduled_emails.append(scheduled_email)
            self._save_scheduled_emails()
            
            time_str = send_time.strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(f"Scheduled email to {to} for {time_str}")
            
            return {
                'status': 'scheduled',
                'id': scheduled_email['id'],
                'send_at': time_str,
                'to': to,
                'subject': subject
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule email: {e}")
            return {'error': f'Failed to schedule: {str(e)}'}
    
    def _parse_schedule_time(self, time_str: str) -> Optional[datetime]:
        """Parse schedule time from various formats"""
        try:
            # Try ISO format first
            return datetime.fromisoformat(time_str)
        except:
            pass
        
        # Try relative format (e.g., "2h", "1d", "30m")
        match = re.match(r'(\d+)([mhd])', time_str.lower())
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            now = datetime.now()
            if unit == 'm':
                return now + timedelta(minutes=value)
            elif unit == 'h':
                return now + timedelta(hours=value)
            elif unit == 'd':
                return now + timedelta(days=value)
        
        return None
    
    def process_scheduled_emails(self) -> List[Dict]:
        """
        Process and send scheduled emails that are due
        Called periodically by scheduler
        
        Returns:
            List of sent email results
        """
        results = []
        now = datetime.now()
        
        pending = [e for e in self.scheduled_emails if e['status'] == 'pending']
        
        for scheduled in pending:
            send_time = datetime.fromisoformat(scheduled['send_at'])
            
            if send_time <= now:
                # Send the email
                result = self.send_email(
                    to=scheduled['to'],
                    subject=scheduled['subject'],
                    body=scheduled['body'],
                    cc=scheduled.get('cc')
                )
                
                # Update status
                scheduled['status'] = 'sent' if result.get('status') == 'sent' else 'failed'
                scheduled['sent_at'] = datetime.now().isoformat()
                scheduled['result'] = result
                
                results.append(result)
                self.logger.info(f"Sent scheduled email to {scheduled['to']}: {scheduled['status']}")
        
        self._save_scheduled_emails()
        return results
    
    def list_scheduled_emails(self, status: Optional[str] = None) -> List[Dict]:
        """List scheduled emails"""
        if status:
            return [e for e in self.scheduled_emails if e['status'] == status]
        return self.scheduled_emails
    
    def cancel_scheduled_email(self, email_id: str) -> str:
        """Cancel a scheduled email"""
        for scheduled in self.scheduled_emails:
            if scheduled['id'] == email_id and scheduled['status'] == 'pending':
                scheduled['status'] = 'cancelled'
                self._save_scheduled_emails()
                return f"✅ Cancelled scheduled email: {scheduled['subject']}"
        
        return f"❌ Scheduled email not found or already sent: {email_id}"
    
    # ========== FEATURE 15: ATTACHMENT HANDLING ==========
    
    def send_email_with_attachment(self, to: str, subject: str, body: str, 
                                   attachments: List[str], cc: Optional[List[str]] = None) -> Dict:
        """
        ✅ NEW FEATURE 15: Send email with attachments
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            attachments: List of file paths to attach
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
            
            # Attach files
            for filepath in attachments:
                path = Path(filepath)
                
                if not path.exists():
                    self.logger.warning(f"Attachment not found: {filepath}")
                    continue
                
                with open(path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={path.name}')
                msg.attach(part)
                
                self.logger.info(f"Attached file: {path.name}")
            
            # Send via SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            recipients = [to]
            if cc:
                recipients.extend(cc)
            
            server.send_message(msg, from_addr=self.email_address, to_addrs=recipients)
            server.quit()
            
            self.stats['emails_sent'] += 1
            
            return {
                'status': 'sent',
                'to': to,
                'subject': subject,
                'attachments': len(attachments),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send email with attachments: {e}")
            return {'error': f'Failed to send: {str(e)}'}
    
    def download_attachments(self, email_id: str, folder: str = 'INBOX', 
                           save_dir: Optional[str] = None) -> List[str]:
        """
        ✅ NEW FEATURE 15b: Download email attachments
        
        Args:
            email_id: Email ID
            folder: Email folder
            save_dir: Directory to save attachments (default: attachments_dir)
        
        Returns:
            List of saved file paths
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return []
            
            mail.select(folder)
            status, msg_data = mail.fetch(email_id.encode(), '(RFC822)')
            
            if status != 'OK':
                mail.logout()
                return []
            
            msg = email.message_from_bytes(msg_data[0][1])
            saved_files = []
            
            save_path = Path(save_dir) if save_dir else self.attachments_dir
            save_path.mkdir(parents=True, exist_ok=True)
            
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    # Sanitize filename
                    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
                    filepath = save_path / filename
                    
                    # Add timestamp if file exists
                    if filepath.exists():
                        name = filepath.stem
                        ext = filepath.suffix
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filepath = save_path / f"{name}_{timestamp}{ext}"
                    
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    saved_files.append(str(filepath))
                    self.logger.info(f"Downloaded attachment: {filename}")
            
            mail.close()
            mail.logout()
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"Failed to download attachments: {e}")
            return []
    
    # ========== FEATURE 16: SPAM DETECTION ==========
    
    def detect_spam(self, email_data: Dict) -> Tuple[bool, float, str]:
        """
        ✅ NEW FEATURE 16: Detect spam emails
        
        Args:
            email_data: Email dictionary
        
        Returns:
            (is_spam, spam_score, reason)
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        sender = email_data.get('from', '').lower()
        
        spam_score = 0.0
        reasons = []
        
        # Check spam keywords
        text = f"{subject} {body}"
        keyword_matches = 0
        for keyword in self.spam_keywords:
            if keyword in text:
                keyword_matches += 1
        
        if keyword_matches > 0:
            spam_score += min(keyword_matches * 0.15, 0.5)
            reasons.append(f"spam keywords ({keyword_matches})")
        
        # Check excessive caps
        if subject and sum(1 for c in subject if c.isupper()) / len(subject) > 0.5:
            spam_score += 0.2
            reasons.append("excessive caps")
        
        # Check excessive exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            spam_score += 0.15
            reasons.append("excessive punctuation")
        
        # Check suspicious sender patterns
        suspicious_patterns = [
            r'noreply',
            r'no-reply',
            r'donotreply',
            r'\d{5,}',  # Long numbers in email
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sender):
                spam_score += 0.1
                reasons.append("suspicious sender")
                break
        
        # Check for known contact (reduces spam score)
        if self.get_contact(sender):
            spam_score = max(0, spam_score - 0.3)
            reasons.append("known contact (-)")
        
        is_spam = spam_score >= 0.6
        reason = ", ".join(reasons) if reasons else "clean"
        
        if is_spam:
            self.stats['spam_filtered'] += 1
        
        return is_spam, round(spam_score, 2), reason
    
    def filter_spam(self, emails: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter spam from email list
        
        Returns:
            (clean_emails, spam_emails)
        """
        clean = []
        spam = []
        
        for email_data in emails:
            is_spam, score, reason = self.detect_spam(email_data)
            email_data['spam_score'] = score
            email_data['spam_reason'] = reason
            
            if is_spam:
                spam.append(email_data)
            else:
                clean.append(email_data)
        
        return clean, spam
    
    # ========== FEATURE 17: ADVANCED EMAIL SEARCH ==========
    
    def search_emails(self, query: Optional[str] = None, sender: Optional[str] = None,
                     subject: Optional[str] = None, date_from: Optional[str] = None,
                     date_to: Optional[str] = None, has_attachment: bool = False,
                     folder: str = 'INBOX', limit: int = 50) -> List[Dict]:
        """
        ✅ NEW FEATURE 17: Advanced email search
        
        Args:
            query: Text search in subject/body
            sender: Filter by sender email
            subject: Filter by subject keywords
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            has_attachment: Only emails with attachments
            folder: Email folder
            limit: Max results
        
        Returns:
            Matching emails
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return [{'error': 'Email not configured'}]
            
            mail.select(folder)
            
            # Build search criteria
            criteria = []
            
            if sender:
                criteria.append(f'FROM "{sender}"')
            
            if subject:
                criteria.append(f'SUBJECT "{subject}"')
            
            if date_from:
                date_obj = datetime.strptime(date_from, '%Y-%m-%d')
                criteria.append(f'SINCE {date_obj.strftime("%d-%b-%Y")}')
            
            if date_to:
                date_obj = datetime.strptime(date_to, '%Y-%m-%d')
                criteria.append(f'BEFORE {date_obj.strftime("%d-%b-%Y")}')
            
            search_str = ' '.join(criteria) if criteria else 'ALL'
            
            status, messages = mail.search(None, search_str)
            
            if status != 'OK':
                mail.logout()
                return [{'error': 'Search failed'}]
            
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            results = []
            
            for email_id in reversed(email_ids):
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Parse email
                    email_subject = self._decode_header(msg.get('Subject', ''))
                    from_addr = email.utils.parseaddr(msg.get('From', ''))[1]
                    body = self._get_email_body(msg)
                    
                    # Filter by query
                    if query:
                        text = f"{email_subject} {body}".lower()
                        if query.lower() not in text:
                            continue
                    
                    # Filter by attachment
                    if has_attachment:
                        has_attach = any(part.get_filename() for part in msg.walk())
                        if not has_attach:
                            continue
                    
                    email_data = {
                        'id': email_id.decode(),
                        'subject': email_subject,
                        'from': from_addr,
                        'date': msg.get('Date', ''),
                        'body': body[:500],
                        'has_attachment': any(part.get_filename() for part in msg.walk())
                    }
                    
                    results.append(email_data)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing email in search: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            self.logger.info(f"Search found {len(results)} emails")
            return results
            
        except Exception as e:
            self.logger.error(f"Email search failed: {e}")
            return [{'error': f'Search failed: {str(e)}'}]
    
    # ========== FEATURE 18: EMAIL THREADING ==========
    
    def group_by_thread(self, emails: List[Dict]) -> Dict[str, List[Dict]]:
        """
        ✅ NEW FEATURE 18: Group emails by conversation thread
        
        Args:
            emails: List of emails
        
        Returns:
            Dictionary of threads {thread_id: [emails]}
        """
        threads = defaultdict(list)
        
        for email_data in emails:
            # Extract thread ID from subject (remove Re:, Fwd:)
            subject = email_data.get('subject', '')
            thread_subject = re.sub(r'^(Re:|Fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()
            
            # Create thread ID from normalized subject
            thread_id = hashlib.md5(thread_subject.lower().encode()).hexdigest()[:8]
            
            threads[thread_id].append(email_data)
        
        # Sort emails in each thread by date
        for thread_id in threads:
            threads[thread_id].sort(key=lambda x: x.get('date', ''))
        
        self.conversation_threads = dict(threads)
        return dict(threads)
    
    def get_thread(self, email_data: Dict) -> List[Dict]:
        """Get all emails in the same thread"""
        subject = email_data.get('subject', '')
        thread_subject = re.sub(r'^(Re:|Fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()
        thread_id = hashlib.md5(thread_subject.lower().encode()).hexdigest()[:8]
        
        if thread_id in self.conversation_threads:
            return self.conversation_threads[thread_id]
        
        return [email_data]
    
    # ========== FEATURE 19: AI-POWERED SUMMARIZATION ==========
    
    def ai_summarize_email(self, email_data: Dict) -> str:
        """
        ✅ NEW FEATURE 19: AI-powered email summarization using LLM
        
        Args:
            email_data: Email dictionary
        
        Returns:
            AI-generated summary
        """
        if not self.llm_router:
            # Fallback to rule-based
            return self.summarize_email(email_data)
        
        try:
            subject = email_data.get('subject', 'No Subject')
            body = email_data.get('body', '')
            sender = email_data.get('from', 'Unknown')
            
            prompt = f"""Summarize this email in 1-2 concise sentences:

From: {sender}
Subject: {subject}

{body[:1000]}

Summary:"""
            
            response = self.llm_router.generate(prompt, max_tokens=100)
            summary = response.strip()
            
            return summary if summary else self.summarize_email(email_data)
            
        except Exception as e:
            self.logger.warning(f"AI summarization failed, using fallback: {e}")
            return self.summarize_email(email_data)
    
    def ai_extract_action_items(self, email_data: Dict) -> List[str]:
        """
        ✅ NEW FEATURE 19b: AI-powered action item extraction
        
        Args:
            email_data: Email dictionary
        
        Returns:
            List of action items
        """
        if not self.llm_router:
            return self.extract_action_items(email_data)
        
        try:
            body = email_data.get('body', '')
            
            prompt = f"""Extract action items from this email. List only specific tasks or requests:

{body[:1000]}

Action items (one per line):"""
            
            response = self.llm_router.generate(prompt, max_tokens=200)
            
            # Parse response
            lines = [line.strip() for line in response.strip().split('\n')]
            actions = [line for line in lines if line and len(line) > 10]
            
            return actions[:5] if actions else self.extract_action_items(email_data)
            
        except Exception as e:
            self.logger.warning(f"AI action extraction failed, using fallback: {e}")
            return self.extract_action_items(email_data)
    
    def ai_draft_reply(self, email_data: Dict, tone: str = 'professional') -> str:
        """
        ✅ NEW FEATURE 19c: AI-powered email reply drafting
        
        Args:
            email_data: Original email
            tone: Reply tone (professional, casual, friendly)
        
        Returns:
            Draft reply text
        """
        if not self.llm_router:
            return "AI reply drafting requires LLM configuration."
        
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('from', 'Unknown')
            
            prompt = f"""Draft a {tone} reply to this email:

From: {sender}
Subject: {subject}

{body[:800]}

Draft reply:"""
            
            response = self.llm_router.generate(prompt, max_tokens=300)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"AI reply drafting failed: {e}")
            return f"Error drafting reply: {str(e)}"
    
    # ========== FEATURE 20: FOLDER MANAGEMENT ==========
    
    def list_folders(self) -> List[str]:
        """
        ✅ NEW FEATURE 20: List all email folders
        
        Returns:
            List of folder names
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return ['INBOX']
            
            status, folders = mail.list()
            
            folder_names = []
            for folder in folders:
                # Parse folder name from IMAP response
                parts = folder.decode().split('"')
                if len(parts) >= 3:
                    folder_names.append(parts[-2])
            
            mail.logout()
            return folder_names
            
        except Exception as e:
            self.logger.error(f"Failed to list folders: {e}")
            return ['INBOX']
    
    def move_email(self, email_id: str, from_folder: str, to_folder: str) -> Dict:
        """
        ✅ NEW FEATURE 20b: Move email to different folder
        
        Args:
            email_id: Email ID
            from_folder: Source folder
            to_folder: Destination folder
        
        Returns:
            Status dict
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return {'error': 'Email not configured'}
            
            # Copy to new folder
            mail.select(from_folder)
            result = mail.copy(email_id.encode(), to_folder)
            
            if result[0] == 'OK':
                # Mark original as deleted
                mail.store(email_id.encode(), '+FLAGS', '\\Deleted')
                mail.expunge()
                
                mail.close()
                mail.logout()
                
                self.logger.info(f"Moved email {email_id} from {from_folder} to {to_folder}")
                return {'status': 'moved', 'from': from_folder, 'to': to_folder}
            else:
                mail.logout()
                return {'error': 'Failed to copy email'}
                
        except Exception as e:
            self.logger.error(f"Failed to move email: {e}")
            return {'error': f'Move failed: {str(e)}'}
    
    def create_folder(self, folder_name: str) -> Dict:
        """Create new email folder"""
        try:
            mail = self.connect_imap()
            if not mail:
                return {'error': 'Email not configured'}
            
            result = mail.create(folder_name)
            mail.logout()
            
            if result[0] == 'OK':
                return {'status': 'created', 'folder': folder_name}
            else:
                return {'error': 'Failed to create folder'}
                
        except Exception as e:
            self.logger.error(f"Failed to create folder: {e}")
            return {'error': f'Create failed: {str(e)}'}
    
    # ========== FEATURE 21: BATCH OPERATIONS ==========
    
    def mark_multiple_as_read(self, email_ids: List[str], folder: str = 'INBOX') -> Dict:
        """
        ✅ NEW FEATURE 21: Mark multiple emails as read
        
        Args:
            email_ids: List of email IDs
            folder: Folder name
        
        Returns:
            Status dict
        """
        try:
            mail = self.connect_imap()
            if not mail:
                return {'error': 'Email not configured'}
            
            mail.select(folder)
            
            success_count = 0
            for email_id in email_ids:
                try:
                    mail.store(email_id.encode(), '+FLAGS', '\\Seen')
                    success_count += 1
                except:
                    pass
            
            mail.close()
            mail.logout()
            
            return {
                'status': 'completed',
                'marked': success_count,
                'total': len(email_ids)
            }
            
        except Exception as e:
            self.logger.error(f"Batch mark as read failed: {e}")
            return {'error': f'Batch operation failed: {str(e)}'}
    
    def delete_multiple_emails(self, email_ids: List[str], folder: str = 'INBOX') -> Dict:
        """Delete multiple emails"""
        try:
            mail = self.connect_imap()
            if not mail:
                return {'error': 'Email not configured'}
            
            mail.select(folder)
            
            success_count = 0
            for email_id in email_ids:
                try:
                    mail.store(email_id.encode(), '+FLAGS', '\\Deleted')
                    success_count += 1
                except:
                    pass
            
            mail.expunge()
            mail.close()
            mail.logout()
            
            return {
                'status': 'deleted',
                'count': success_count,
                'total': len(email_ids)
            }
            
        except Exception as e:
            self.logger.error(f"Batch delete failed: {e}")
            return {'error': f'Delete failed: {str(e)}'}
    
    # ========== FEATURE 22: STATISTICS & ANALYTICS ==========
    
    def get_statistics(self) -> Dict:
        """
        ✅ NEW FEATURE 22: Get communication statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'emails_sent': self.stats['emails_sent'],
            'emails_read': self.stats['emails_read'],
            'notifications_sent': self.stats['notifications_sent'],
            'spam_filtered': self.stats['spam_filtered'],
            'contacts': len(self.contacts),
            'scheduled_emails': len([e for e in self.scheduled_emails if e['status'] == 'pending']),
            'conversation_threads': len(self.conversation_threads)
        }
    
    def get_email_analytics(self, days: int = 7) -> Dict:
        """
        ✅ NEW FEATURE 22b: Email analytics for recent days
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Analytics dictionary
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            emails = self.search_emails(
                date_from=cutoff_date.strftime('%Y-%m-%d'),
                limit=1000
            )
            
            if not emails or 'error' in emails[0]:
                return {'error': 'Failed to fetch emails for analytics'}
            
            # Analyze senders
            sender_counts = defaultdict(int)
            for email_data in emails:
                sender = email_data.get('from', 'Unknown')
                sender_counts[sender] += 1
            
            top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Count by day
            daily_counts = defaultdict(int)
            for email_data in emails:
                date_str = email_data.get('date', '')
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    day = date_obj.strftime('%Y-%m-%d')
                    daily_counts[day] += 1
                except:
                    pass
            
            return {
                'period_days': days,
                'total_emails': len(emails),
                'avg_per_day': round(len(emails) / days, 1),
                'top_senders': [{'email': s, 'count': c} for s, c in top_senders],
                'daily_counts': dict(daily_counts)
            }
            
        except Exception as e:
            self.logger.error(f"Analytics failed: {e}")
            return {'error': f'Analytics failed: {str(e)}'}
    
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
        ✅ FEATURE 1: Read emails via IMAP (ENHANCED)
        
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
                    
                    # Check for attachments
                    has_attachment = any(part.get_filename() for part in msg.walk())
                    
                    # Update contact stats
                    contact = self.get_contact(from_addr)
                    if contact:
                        contact_id = hashlib.md5(from_addr.lower().encode()).hexdigest()[:8]
                        self.contacts[contact_id]['email_count'] += 1
                        self.contacts[contact_id]['last_contact'] = datetime.now().isoformat()
                        self._save_contacts()
                    
                    email_data = {
                        'id': email_id.decode(),
                        'subject': subject,
                        'from': from_addr,
                        'from_name': from_name,
                        'date': date_str,
                        'body': body[:500],  # Truncate long emails
                        'priority': priority,
                        'folder': folder,
                        'has_attachment': has_attachment,
                        'is_contact': contact is not None
                    }
                    
                    emails.append(email_data)
                    self.stats['emails_read'] += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing email: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            self.email_cache = emails
            self.logger.info(f"Read {len(emails)} emails from {folder}")
            return emails
            
        except Exception as e:
            self.logger.error(f"Failed to read emails: {e}")
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
        ✅ FEATURE 2: Send emails via SMTP (ENHANCED)
        
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
            
            # Update stats and contact
            self.stats['emails_sent'] += 1
            contact = self.get_contact(to)
            if contact:
                contact_id = hashlib.md5(to.lower().encode()).hexdigest()[:8]
                self.contacts[contact_id]['email_count'] += 1
                self.contacts[contact_id]['last_contact'] = datetime.now().isoformat()
                self._save_contacts()
            
            self.logger.info(f"Sent email to {to}: {subject}")
            
            return {
                'status': 'sent',
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
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
    
    def send_desktop_notification(self, title: str, message: str, duration: int = 10, urgency: str = 'normal') -> Dict:
        """
        ✅ FEATURE 8: Send desktop notification (ENHANCED)
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in seconds
            urgency: Notification urgency (low, normal, high)
        
        Returns:
            Status dict
        """
        try:
            # Try Windows 10 Toast
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=duration, threaded=True)
                self.stats['notifications_sent'] += 1
                self.logger.info(f"Sent Windows notification: {title}")
                return {'status': 'sent', 'platform': 'windows'}
            except ImportError:
                pass
            except Exception as e:
                self.logger.debug(f"Windows toast failed: {e}")
            
            # Try cross-platform plyer
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name='Orbit AI',
                    timeout=duration
                )
                self.stats['notifications_sent'] += 1
                self.logger.info(f"Sent notification via plyer: {title}")
                return {'status': 'sent', 'platform': 'plyer'}
            except ImportError:
                pass
            except Exception as e:
                self.logger.debug(f"Plyer notification failed: {e}")
            
            # Fallback: console
            urgency_icon = {'low': 'ℹ️', 'normal': '🔔', 'high': '⚠️'}.get(urgency, '🔔')
            print(f"\n{urgency_icon} {title}\n   {message}\n")
            self.stats['notifications_sent'] += 1
            return {'status': 'sent', 'platform': 'console'}
            
        except Exception as e:
            self.logger.error(f"Notification failed: {e}")
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
        """Enhanced main command router with all features"""
        cmd = command.lower().strip()
        
        # === EMAIL READING ===
        if 'read' in cmd and 'email' in cmd:
            unread = 'unread' in cmd
            emails = self.read_emails(unread_only=unread)
            
            if not emails:
                return "📭 No emails found"
            
            if 'error' in emails[0]:
                return f"❌ {emails[0]['error']}"
            
            # Filter spam if requested
            if 'spam' not in cmd:
                clean, spam = self.filter_spam(emails)
                if spam:
                    self.logger.info(f"Filtered {len(spam)} spam emails")
                emails = clean
            
            result = f"📧 Found {len(emails)} email(s):\n\n"
            for i, e in enumerate(emails[:5], 1):
                icon = "⚠️ " if e.get('priority') == 'high' else ""
                icon += "📎 " if e.get('has_attachment') else ""
                result += f"{icon}{i}. From: {e.get('from_name')} <{e.get('from')}>\n"
                result += f"   Subject: {e.get('subject')}\n"
                result += f"   Date: {e.get('date')}\n\n"
            
            return result
        
        # === PRIORITY EMAILS ===
        elif 'priority' in cmd or 'urgent' in cmd:
            emails = self.read_emails(unread_only=False, limit=50)
            priority = self.filter_priority_emails(emails)
            
            if not priority:
                return "✅ No priority emails"
            
            result = f"⚠️  Priority Emails ({len(priority)}):\n\n"
            for i, e in enumerate(priority, 1):
                result += f"{i}. {e.get('from')}: {e.get('subject')}\n"
            
            return result
        
        # === SUMMARIZATION ===
        elif 'summarize' in cmd and 'email' in cmd:
            use_ai = 'ai' in cmd or self.llm_router
            emails = self.read_emails(limit=5)
            
            if not emails or 'error' in emails[0]:
                return "❌ No emails to summarize"
            
            result = f"📝 Email Summaries {'(AI-Powered)' if use_ai else ''}:\n\n"
            for i, e in enumerate(emails, 1):
                if use_ai and self.llm_router:
                    summary = self.ai_summarize_email(e)
                else:
                    summary = self.summarize_email(e)
                result += f"{i}. {summary}\n\n"
            
            return result
        
        # === ACTION ITEMS ===
        elif 'action' in cmd and 'item' in cmd:
            use_ai = 'ai' in cmd or self.llm_router
            emails = self.read_emails(limit=10)
            
            if not emails or 'error' in emails[0]:
                return "❌ No emails"
            
            all_actions = []
            for e in emails:
                if use_ai and self.llm_router:
                    actions = self.ai_extract_action_items(e)
                else:
                    actions = self.extract_action_items(e)
                all_actions.extend(actions)
            
            if not all_actions:
                return "✅ No action items found"
            
            result = f"✅ Action Items ({len(all_actions)}):\n\n"
            for i, action in enumerate(all_actions[:10], 1):
                result += f"{i}. {action}\n"
            
            return result
        
        # === CONTACTS ===
        elif 'contact' in cmd:
            if 'list' in cmd:
                contacts = self.list_contacts()
                if not contacts:
                    return "📇 No contacts"
                
                result = f"📇 Contacts ({len(contacts)}):\n\n"
                for i, c in enumerate(contacts[:20], 1):
                    tags = f" [{', '.join(c.get('tags', []))}]" if c.get('tags') else ""
                    result += f"{i}. {c['name']} <{c['email']}>{tags}\n"
                
                return result
            
            elif 'add' in cmd:
                return "Usage: Add contact via API: add_contact(name, email, phone, tags)"
            
            else:
                return "Contact commands: list contacts, add contact"
        
        # === SCHEDULED EMAILS ===
        elif 'schedul' in cmd:
            scheduled = self.list_scheduled_emails(status='pending')
            
            if not scheduled:
                return "📅 No scheduled emails"
            
            result = f"📅 Scheduled Emails ({len(scheduled)}):\n\n"
            for i, s in enumerate(scheduled, 1):
                send_time = datetime.fromisoformat(s['send_at']).strftime('%Y-%m-%d %H:%M')
                result += f"{i}. To: {s['to']}\n"
                result += f"   Subject: {s['subject']}\n"
                result += f"   Send at: {send_time}\n"
                result += f"   ID: {s['id']}\n\n"
            
            return result
        
        # === SEARCH EMAILS ===
        elif 'search' in cmd:
            # Extract search query
            query = cmd.replace('search', '').replace('email', '').strip()
            if not query:
                return "❌ Provide search query"
            
            results = self.search_emails(query=query, limit=20)
            
            if not results or 'error' in results[0]:
                return "❌ No results found"
            
            result = f"🔍 Search Results ({len(results)}):\n\n"
            for i, e in enumerate(results[:10], 1):
                result += f"{i}. {e.get('from')}: {e.get('subject')}\n"
            
            return result
        
        # === STATISTICS ===
        elif 'stat' in cmd or 'analytic' in cmd:
            stats = self.get_statistics()
            
            result = "📊 Communication Statistics:\n\n"
            result += f"📧 Emails Sent: {stats['emails_sent']}\n"
            result += f"📬 Emails Read: {stats['emails_read']}\n"
            result += f"🔔 Notifications: {stats['notifications_sent']}\n"
            result += f"🚫 Spam Filtered: {stats['spam_filtered']}\n"
            result += f"📇 Contacts: {stats['contacts']}\n"
            result += f"📅 Scheduled: {stats['scheduled_emails']}\n"
            result += f"💬 Threads: {stats['conversation_threads']}\n"
            
            return result
        
        # === FOLDERS ===
        elif 'folder' in cmd:
            folders = self.list_folders()
            result = f"📁 Email Folders ({len(folders)}):\n\n"
            for folder in folders:
                result += f"  • {folder}\n"
            return result
        
        # === TELEGRAM ===
        elif 'telegram' in cmd:
            message = cmd.replace('telegram', '').replace('send', '').strip()
            if message:
                result = self.send_telegram(message)
                return "✅ Telegram sent" if result.get('status') == 'sent' else f"❌ {result.get('error')}"
            return "❌ Provide a message"
        
        # === NOTIFICATIONS ===
        elif 'notif' in cmd:
            message = cmd.replace('notification', '').replace('notify', '').strip()
            urgency = 'high' if 'urgent' in cmd else 'normal'
            self.send_desktop_notification("Orbit", message or "Test notification", urgency=urgency)
            return "🔔 Notification sent"
        
        # === HELP ===
        else:
            return """📧 Communication Commands (Enhanced):

EMAIL:
  • read [unread] emails - Read emails
  • show priority emails - Priority only
  • summarize emails [ai] - AI/rule-based summaries
  • extract action items [ai] - Find action items
  • search [query] - Search emails

CONTACTS:
  • list contacts - Show all contacts
  
SCHEDULING:
  • show scheduled emails - Pending scheduled emails
  
ANALYTICS:
  • show statistics - Communication stats
  • show folders - List email folders

MESSAGING:
  • send telegram [message] - Telegram message
  • send notification [message] - Desktop notification

Type 'help communication' for API documentation."""
