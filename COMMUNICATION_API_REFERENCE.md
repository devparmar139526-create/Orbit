# 📚 Communication System - Complete API Reference

## Quick Start

```python
from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings
from Orbit_core.llm.router import LLMRouter  # Optional for AI features

# Basic initialization
settings = Settings()
comm = CommunicationService(settings=settings)

# With AI features
llm_router = LLMRouter(settings)
comm = CommunicationService(settings=settings, llm_router=llm_router)
```

---

## 📧 Core Email Features

### Read Emails
```python
emails = comm.read_emails(
    folder='INBOX',      # Folder name
    limit=10,            # Max emails to fetch
    unread_only=True     # Only unread emails
)

# Returns: List[Dict]
# Each email contains: id, subject, from, from_name, date, body, 
#                      priority, folder, has_attachment, is_contact
```

### Send Email
```python
result = comm.send_email(
    to="recipient@example.com",
    subject="Hello",
    body="Email body text",
    cc=["cc@example.com"]  # Optional
)

# Returns: {'status': 'sent', 'to': ..., 'subject': ..., 'timestamp': ...}
```

### Send with Attachments
```python
result = comm.send_email_with_attachment(
    to="recipient@example.com",
    subject="Files attached",
    body="Please see attached",
    attachments=["file1.pdf", "file2.docx"],
    cc=None  # Optional
)

# Returns: {'status': 'sent', 'attachments': 2, ...}
```

### Download Attachments
```python
files = comm.download_attachments(
    email_id="12345",
    folder='INBOX',
    save_dir=None  # Uses default: data/communication/attachments/
)

# Returns: List[str] - List of saved file paths
```

---

## 🔍 Email Filtering & Search

### Filter Priority Emails
```python
# Option 1: From cache
priority = comm.filter_priority_emails()

# Option 2: Custom list
emails = comm.read_emails(limit=50)
priority = comm.filter_priority_emails(emails)

# Returns: List[Dict] - Only high priority emails
```

### Advanced Search
```python
results = comm.search_emails(
    query="project budget",           # Text search
    sender="boss@company.com",        # Filter by sender
    subject="meeting",                # Subject keywords
    date_from="2025-10-01",          # Start date (YYYY-MM-DD)
    date_to="2025-10-31",            # End date
    has_attachment=True,              # Only with attachments
    folder='INBOX',                   # Folder to search
    limit=50                          # Max results
)

# Returns: List[Dict] - Matching emails
```

### Spam Detection
```python
# Check single email
is_spam, score, reason = comm.detect_spam(email_data)
# Returns: (True/False, 0.0-1.0, "reason string")

# Filter list
clean_emails, spam_emails = comm.filter_spam(emails)
# Returns: (List[Dict], List[Dict])
```

---

## 📇 Contact Management

### Add Contact
```python
result = comm.add_contact(
    name="John Doe",
    email="john@example.com",
    phone="+1234567890",          # Optional
    tags=["work", "vip"],         # Optional
    notes="CEO of company"        # Optional
)

# Returns: "✅ Added contact: John Doe <john@example.com>"
```

### Get Contact
```python
contact = comm.get_contact("john")  # Search by name or email

# Returns: Dict or None
# {
#   'name': 'John Doe',
#   'email': 'john@example.com',
#   'phone': '+1234567890',
#   'tags': ['work', 'vip'],
#   'notes': 'CEO of company',
#   'added_date': '2025-10-31T...',
#   'email_count': 5,
#   'last_contact': '2025-10-31T...'
# }
```

### List Contacts
```python
# All contacts
all_contacts = comm.list_contacts()

# Filter by tag
work_contacts = comm.list_contacts(tag="work")

# Returns: List[Dict] - Sorted by name
```

### Update Contact
```python
result = comm.update_contact(
    email="john@example.com",
    phone="+9876543210",
    tags=["work", "vip", "board"],
    notes="CEO and Board Member"
)

# Returns: "✅ Updated contact: john@example.com"
```

### Delete Contact
```python
result = comm.delete_contact("john@example.com")

# Returns: "✅ Deleted contact: John Doe"
```

---

## 📅 Email Scheduling

### Schedule Email
```python
# ISO format
result = comm.schedule_email(
    to="recipient@example.com",
    subject="Scheduled Email",
    body="This will be sent later",
    send_at="2025-11-01T14:00:00",
    cc=None  # Optional
)

# Relative format
result = comm.schedule_email(
    to="team@example.com",
    subject="Reminder",
    body="Don't forget!",
    send_at="2h"  # Options: "30m", "2h", "1d"
)

# Returns: {
#   'status': 'scheduled',
#   'id': 'abc12345',
#   'send_at': '2025-11-01 14:00:00',
#   'to': ...,
#   'subject': ...
# }
```

### List Scheduled Emails
```python
# All scheduled emails
all_scheduled = comm.list_scheduled_emails()

# Only pending
pending = comm.list_scheduled_emails(status='pending')

# Only sent
sent = comm.list_scheduled_emails(status='sent')

# Returns: List[Dict]
```

### Cancel Scheduled Email
```python
result = comm.cancel_scheduled_email("abc12345")

# Returns: "✅ Cancelled scheduled email: ..."
```

### Process Scheduled Emails
```python
# Call this periodically (e.g., every minute from scheduler)
results = comm.process_scheduled_emails()

# Returns: List[Dict] - Results of sent emails
```

---

## 💬 Email Threading

### Group by Thread
```python
emails = comm.read_emails(limit=100)
threads = comm.group_by_thread(emails)

# Returns: Dict[str, List[Dict]]
# {
#   'thread_id_1': [email1, email2, email3],
#   'thread_id_2': [email4, email5]
# }
```

### Get Thread
```python
thread_emails = comm.get_thread(email_data)

# Returns: List[Dict] - All emails in same thread
```

---

## 📝 Summarization (Rule-based & AI)

### Basic Summarization
```python
summary = comm.summarize_email(email_data)

# Returns: str - "From sender - subject: summary..."
```

### AI Summarization
```python
# Requires llm_router in __init__
summary = comm.ai_summarize_email(email_data)

# Returns: str - AI-generated summary
# Fallback: Uses rule-based if LLM unavailable
```

### Conversation Summary
```python
emails = comm.read_emails(limit=10)
summary = comm.summarize_conversation(emails)

# Returns: str - "Conversation: X emails, Participants: ..., Topic: ..."
```

---

## ✅ Action Item Extraction

### Basic Extraction
```python
actions = comm.extract_action_items(email_data)

# Returns: List[str] - Action items found
```

### AI Extraction
```python
# Requires llm_router
actions = comm.ai_extract_action_items(email_data)

# Returns: List[str] - AI-detected action items
# Fallback: Uses rule-based if LLM unavailable
```

---

## 🤖 AI-Powered Features

### Draft Reply
```python
# Requires llm_router
reply = comm.ai_draft_reply(
    email_data=original_email,
    tone='professional'  # Options: professional, casual, friendly
)

# Returns: str - Draft reply text
```

---

## 📁 Folder Management

### List Folders
```python
folders = comm.list_folders()

# Returns: List[str] - ['INBOX', 'Sent', 'Drafts', ...]
```

### Move Email
```python
result = comm.move_email(
    email_id="12345",
    from_folder="INBOX",
    to_folder="Archive"
)

# Returns: {'status': 'moved', 'from': ..., 'to': ...}
```

### Create Folder
```python
result = comm.create_folder("Projects")

# Returns: {'status': 'created', 'folder': 'Projects'}
```

---

## 🔄 Batch Operations

### Mark Multiple as Read
```python
result = comm.mark_multiple_as_read(
    email_ids=["123", "456", "789"],
    folder='INBOX'
)

# Returns: {'status': 'completed', 'marked': 3, 'total': 3}
```

### Delete Multiple Emails
```python
result = comm.delete_multiple_emails(
    email_ids=["123", "456"],
    folder='INBOX'
)

# Returns: {'status': 'deleted', 'count': 2, 'total': 2}
```

### Mark Single as Read
```python
result = comm.mark_as_read(
    email_id="12345",
    folder='INBOX'
)

# Returns: {'status': 'marked_read', 'email_id': '12345'}
```

---

## 📊 Statistics & Analytics

### Get Statistics
```python
stats = comm.get_statistics()

# Returns: {
#   'emails_sent': 42,
#   'emails_read': 150,
#   'notifications_sent': 8,
#   'spam_filtered': 12,
#   'contacts': 25,
#   'scheduled_emails': 3,
#   'conversation_threads': 10
# }
```

### Get Email Analytics
```python
analytics = comm.get_email_analytics(days=7)

# Returns: {
#   'period_days': 7,
#   'total_emails': 85,
#   'avg_per_day': 12.1,
#   'top_senders': [
#     {'email': 'sender1@example.com', 'count': 15},
#     {'email': 'sender2@example.com', 'count': 12}
#   ],
#   'daily_counts': {
#     '2025-10-25': 10,
#     '2025-10-26': 15,
#     ...
#   }
# }
```

---

## 💬 Messaging

### Send Telegram
```python
result = comm.send_telegram("Hello from Orbit!")

# Requires: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in settings
# Returns: {'status': 'sent', 'platform': 'telegram', ...}
```

### Send SMS
```python
result = comm.send_sms(
    to="+1234567890",
    message="Hello via SMS"
)

# Requires: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
# Returns: {'status': 'sent', 'platform': 'sms', 'message_sid': ...}
```

---

## 🔔 Notifications

### Desktop Notification
```python
result = comm.send_desktop_notification(
    title="Important",
    message="You have a new high-priority email",
    duration=10,  # seconds
    urgency='high'  # Options: low, normal, high
)

# Returns: {'status': 'sent', 'platform': 'windows'/'plyer'/'console'}
```

### Notification Rules
```python
# Check if email matches rules
should_notify = comm.check_notification_rules(email_data)

# Add new rule
result = comm.add_notification_rule('sender', 'boss@company.com')
result = comm.add_notification_rule('keyword', 'urgent')

# Returns: bool / str
```

---

## 📧 Auto-Reply

### Send Auto-Reply
```python
# Using template
result = comm.send_auto_reply(
    to="sender@example.com",
    template_name='out_of_office'  # Options: out_of_office, meeting, busy
)

# Custom message
result = comm.send_auto_reply(
    to="sender@example.com",
    custom_message="I received your email and will respond soon."
)

# Returns: Same as send_email()
```

### Get Templates
```python
templates = comm.get_auto_reply_templates()

# Returns: Dict[str, str] - Template name -> template text
```

### Add Template
```python
result = comm.add_auto_reply_template(
    name='vacation',
    template="I'm on vacation until {date}. I'll respond when I return."
)

# Returns: "✅ Added auto-reply template: vacation"
```

---

## 🎤 Voice Commands (Execute Method)

The `execute()` method processes natural language commands:

```python
result = comm.execute("read unread emails")
result = comm.execute("show priority emails")
result = comm.execute("summarize emails")
result = comm.execute("summarize emails with AI")
result = comm.execute("extract action items")
result = comm.execute("extract action items with AI")
result = comm.execute("search project budget")
result = comm.execute("list contacts")
result = comm.execute("show scheduled emails")
result = comm.execute("show statistics")
result = comm.execute("show folders")
result = comm.execute("send telegram Hello team")
result = comm.execute("send notification Important message")
```

### Command Patterns

**Email Reading:**
- `"read emails"` - Read all
- `"read unread emails"` - Unread only
- `"show priority emails"` - Priority filter

**Summarization:**
- `"summarize emails"` - Rule-based
- `"summarize emails ai"` - AI-powered

**Action Items:**
- `"extract action items"` - Rule-based
- `"extract action items ai"` - AI-powered

**Search:**
- `"search [query]"` - Search emails

**Management:**
- `"list contacts"` - Show contacts
- `"show scheduled emails"` - Pending schedules
- `"show statistics"` - Get stats
- `"show folders"` - List folders

**Messaging:**
- `"send telegram [message]"` - Telegram
- `"send notification [message]"` - Desktop

---

## ⚙️ Configuration

### Email Settings
```python
settings.EMAIL_ADDRESS = "your@email.com"
settings.EMAIL_PASSWORD = "your_password"
settings.IMAP_SERVER = "imap.gmail.com"
settings.IMAP_PORT = 993
settings.SMTP_SERVER = "smtp.gmail.com"
settings.SMTP_PORT = 587
```

### Priority Settings
```python
settings.PRIORITY_KEYWORDS = [
    'urgent', 'important', 'asap', 'critical', 'emergency', 'deadline'
]

settings.PRIORITY_SENDERS = [
    'boss@company.com',
    'ceo@company.com'
]
```

### Spam Settings
```python
settings.SPAM_KEYWORDS = [
    'viagra', 'casino', 'lottery', 'winner', 
    'claim prize', 'act now', 'limited time', 
    'click here', 'unsubscribe', 'free money'
]
```

### Messaging Settings
```python
# Telegram
settings.TELEGRAM_BOT_TOKEN = "your_bot_token"
settings.TELEGRAM_CHAT_ID = "your_chat_id"

# Twilio SMS
settings.TWILIO_ACCOUNT_SID = "your_account_sid"
settings.TWILIO_AUTH_TOKEN = "your_auth_token"
settings.TWILIO_PHONE_NUMBER = "+1234567890"
```

### Data Directory
```python
settings.DATA_DIR = "/path/to/data"
# Creates: /path/to/data/communication/
#   - contacts.json
#   - scheduled_emails.json
#   - attachments/
```

---

## 🐛 Error Handling

All methods return error information when something goes wrong:

```python
result = comm.send_email("invalid", "subject", "body")
# Returns: {'error': 'Email not configured'}

emails = comm.read_emails()
# Returns: [{'error': 'Failed to read emails: ...'}]
```

Check for errors:
```python
result = comm.send_email(...)
if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(f"Success: {result['status']}")
```

---

## 📝 Logging

All operations are logged:

```python
import logging

# Get logger
logger = logging.getLogger('orbit.communication')

# Set level
logger.setLevel(logging.DEBUG)  # See all operations
logger.setLevel(logging.INFO)   # Normal operations
logger.setLevel(logging.WARNING)  # Warnings and errors only
```

Log messages include:
- INFO: Successful operations (sent email, added contact, etc.)
- WARNING: Non-critical errors (failed to parse email, etc.)
- ERROR: Critical failures (IMAP connection failed, etc.)
- DEBUG: Detailed debugging information

---

## 🧪 Testing

```python
from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

# Initialize
settings = Settings()
comm = CommunicationService(settings=settings)

# Test without credentials (local features)
comm.add_contact("Test", "test@example.com")
contacts = comm.list_contacts()
print(f"Contacts: {len(contacts)}")

# Test spam detection
spam = {'subject': 'FREE MONEY!!!', 'body': 'Click now!', 'from': 'spam@bad.com'}
is_spam, score, reason = comm.detect_spam(spam)
print(f"Spam: {is_spam}, Score: {score}")

# Test scheduling
sched = comm.schedule_email("test@test.com", "Test", "Body", "2h")
print(f"Scheduled: {sched['status']}")

# Test statistics
stats = comm.get_statistics()
print(f"Stats: {stats}")
```

---

## 📚 Complete Feature List

### Email Operations (7)
1. Read emails (IMAP)
2. Send emails (SMTP)
3. Send with attachments
4. Download attachments
5. Mark as read
6. Search emails
7. Filter priority

### Contact Management (5)
8. Add contact
9. Get contact
10. List contacts
11. Update contact
12. Delete contact

### Scheduling (4)
13. Schedule email
14. List scheduled
15. Cancel scheduled
16. Process scheduled

### Filtering (3)
17. Spam detection
18. Filter spam
19. Priority filtering

### Threading (2)
20. Group by thread
21. Get thread

### Summarization (3)
22. Basic summarization
23. AI summarization
24. Conversation summary

### Action Items (2)
25. Basic extraction
26. AI extraction

### AI Features (1)
27. Draft reply

### Folder Management (3)
28. List folders
29. Move email
30. Create folder

### Batch Operations (2)
31. Mark multiple as read
32. Delete multiple

### Analytics (2)
33. Get statistics
34. Get email analytics

### Messaging (2)
35. Send Telegram
36. Send SMS

### Notifications (2)
37. Desktop notifications
38. Notification rules

### Auto-Reply (3)
39. Send auto-reply
40. Get templates
41. Add template

**Total: 41+ features!**

---

## 🎯 Best Practices

1. **Always check for errors**
   ```python
   result = comm.send_email(...)
   if 'error' in result:
       handle_error(result['error'])
   ```

2. **Use contacts for frequent senders**
   ```python
   comm.add_contact("Boss", "boss@company.com", tags=["priority"])
   ```

3. **Schedule instead of send for future emails**
   ```python
   comm.schedule_email(..., send_at="1d")  # Better than manual sending
   ```

4. **Filter spam before processing**
   ```python
   emails = comm.read_emails()
   clean, spam = comm.filter_spam(emails)
   process_emails(clean)
   ```

5. **Use AI features when available**
   ```python
   if comm.llm_router:
       summary = comm.ai_summarize_email(email)
   else:
       summary = comm.summarize_email(email)
   ```

6. **Process scheduled emails periodically**
   ```python
   # In your scheduler (every minute)
   comm.process_scheduled_emails()
   ```

7. **Monitor statistics**
   ```python
   stats = comm.get_statistics()
   if stats['spam_filtered'] > 100:
       review_spam_rules()
   ```

---

Generated: 2025-10-31  
Version: 2.0 (Enhanced)  
Features: 41+  
Architecture: Synchronous, Single Class  
AI Integration: Optional LLM Router
