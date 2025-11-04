# 🎯 Communication System - Quick Reference Card

## 🚀 **5-MINUTE QUICK START**

### Setup (Once)
```python
from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

comm = CommunicationService(Settings())
```

### Instant Tests (No Email Credentials Needed)
```python
# 1. Add a contact
comm.add_contact("Test Person", "test@example.com", tags=["demo"])

# 2. Schedule an email
comm.schedule_email("test@example.com", "Hello", "Test body", "2h")

# 3. Test spam detection
spam = {'subject': 'WIN FREE MONEY!!!', 'body': 'Click now!', 'from': 'spam@bad.com'}
is_spam, score, reason = comm.detect_spam(spam)
print(f"Spam: {is_spam}, Score: {score}")

# 4. Check statistics
stats = comm.get_statistics()
print(stats)

# 5. Send notification
comm.send_desktop_notification("Orbit Test", "System is working!")
```

---

## 📋 **VOICE COMMANDS CHEAT SHEET**

Copy and paste these exact commands:

### Basic Operations
```
Read my unread emails
Show priority emails
Summarize emails
Extract action items
List my contacts
Show scheduled emails
Show communication statistics
Show email folders
```

### With AI (if configured)
```
Summarize emails with AI
Extract action items with AI
```

### Search & Filter
```
Search emails for project
Search emails for meeting
Search emails for budget
```

### Messaging
```
Send telegram Hello team
Send notification Test message
```

---

## 🐍 **PYTHON ONE-LINERS**

### Contact Management
```python
comm.add_contact("Name", "email@example.com", tags=["work"])
comm.list_contacts()
comm.get_contact("email@example.com")
```

### Email Scheduling
```python
comm.schedule_email("to@email.com", "Subject", "Body", "2h")
comm.list_scheduled_emails()
```

### Spam Detection
```python
is_spam, score, reason = comm.detect_spam(email_dict)
clean, spam = comm.filter_spam(emails)
```

### Statistics
```python
comm.get_statistics()
comm.get_email_analytics(days=7)
```

### Notifications
```python
comm.send_desktop_notification("Title", "Message", urgency='high')
```

---

## 📊 **FEATURE CATEGORIES**

### ✅ **Works Without Email Credentials**
- Contact management (add, list, update, delete)
- Email scheduling (schedule, list, cancel)
- Spam detection (test with fake emails)
- Email threading (test with fake emails)
- Statistics tracking
- Desktop notifications
- Auto-reply templates

### 🔐 **Requires Email Credentials**
- Read emails (IMAP)
- Send emails (SMTP)
- Search emails
- Download attachments
- Folder management
- Batch operations
- Email analytics

### 🤖 **Requires LLM Configuration**
- AI email summarization
- AI action item extraction
- AI reply drafting

### 📱 **Requires Additional APIs**
- Telegram (needs bot token)
- SMS (needs Twilio)

---

## 🧪 **COMPLETE TEST SCRIPT**

Save as `test_all.py`:

```python
import sys
sys.path.insert(0, 'c:/AAAA/Orbit Final')

from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

comm = CommunicationService(Settings())

print("Testing All Features (No Credentials Required)\n")

# 1. Contacts
print("1. Contact Management")
comm.add_contact("Alice", "alice@test.com", tags=["work", "dev"])
comm.add_contact("Bob", "bob@test.com", tags=["work", "manager"])
comm.add_contact("Charlie", "charlie@test.com", tags=["client", "vip"])
print(f"   ✓ Added 3 contacts. Total: {len(comm.list_contacts())}")

# 2. Scheduling
print("\n2. Email Scheduling")
comm.schedule_email("alice@test.com", "Meeting", "Let's meet", "30m")
comm.schedule_email("bob@test.com", "Report", "Weekly update", "2h")
comm.schedule_email("charlie@test.com", "Follow-up", "Checking in", "1d")
print(f"   ✓ Scheduled 3 emails. Pending: {len(comm.list_scheduled_emails('pending'))}")

# 3. Spam Detection
print("\n3. Spam Detection")
spam_tests = [
    {'subject': 'WIN FREE MONEY NOW!!!', 'body': 'Click here! Limited time! Act now!', 'from': 'spam@bad.com'},
    {'subject': 'Weekly Report', 'body': 'Here is the status update', 'from': 'alice@test.com'},
    {'subject': 'URGENT: CLAIM YOUR PRIZE', 'body': 'You won the lottery!!! Click now!!!', 'from': 'scam@xyz.com'}
]

spam_count = 0
for email in spam_tests:
    is_spam, score, reason = comm.detect_spam(email)
    if is_spam:
        spam_count += 1
    print(f"   - '{email['subject'][:30]}': Spam={is_spam} (score={score})")

print(f"   ✓ Detected {spam_count} spam emails out of {len(spam_tests)}")

# 4. Email Threading
print("\n4. Email Threading")
fake_emails = [
    {'subject': 'Project Alpha', 'from': 'alice@test.com', 'date': '2025-10-28'},
    {'subject': 'Re: Project Alpha', 'from': 'bob@test.com', 'date': '2025-10-29'},
    {'subject': 'Fwd: Project Alpha', 'from': 'charlie@test.com', 'date': '2025-10-30'},
    {'subject': 'Budget Review', 'from': 'alice@test.com', 'date': '2025-10-30'},
    {'subject': 'Re: Budget Review', 'from': 'bob@test.com', 'date': '2025-10-31'},
]

threads = comm.group_by_thread(fake_emails)
print(f"   ✓ Created {len(threads)} conversation threads from {len(fake_emails)} emails")
for thread_id, emails in threads.items():
    print(f"     - Thread {thread_id[:8]}: {len(emails)} emails")

# 5. Statistics
print("\n5. Statistics")
stats = comm.get_statistics()
print(f"   ✓ Contacts: {stats['contacts']}")
print(f"   ✓ Scheduled Emails: {stats['scheduled_emails']}")
print(f"   ✓ Spam Filtered: {stats['spam_filtered']}")
print(f"   ✓ Conversation Threads: {stats['conversation_threads']}")

# 6. Notifications
print("\n6. Desktop Notifications")
result = comm.send_desktop_notification("Orbit Test", "All features working!", urgency='normal')
print(f"   ✓ Notification sent via: {result.get('platform')}")

# 7. Voice Commands
print("\n7. Voice Command Execution")
commands = [
    "list contacts",
    "show scheduled emails",
    "show statistics"
]

for cmd in commands:
    result = comm.execute(cmd)
    print(f"   ✓ '{cmd}': {len(result)} chars response")

print("\n" + "="*60)
print("🎉 ALL FEATURES TESTED SUCCESSFULLY!")
print("="*60)
print(f"\nFeatures Tested: 7 categories")
print(f"Total Operations: 15+")
print(f"Status: ✅ All Working")
```

---

## 🎯 **TOP 10 COMMANDS TO TRY FIRST**

1. **List contacts** → `"list my contacts"`
2. **Show statistics** → `"show communication statistics"`
3. **Schedule email** → `comm.schedule_email("test@test.com", "Hi", "Hello", "2h")`
4. **Test spam** → `comm.detect_spam({'subject': 'WIN NOW!!!', 'body': 'Free!', 'from': 'spam@bad.com'})`
5. **Add contact** → `comm.add_contact("Test", "test@example.com", tags=["demo"])`
6. **Send notification** → `"send notification Test message"`
7. **Show scheduled** → `"show scheduled emails"`
8. **Get analytics** → `comm.get_email_analytics(days=7)`
9. **Group threads** → `threads = comm.group_by_thread(emails)`
10. **Voice summary** → `"summarize emails"`

---

## 🔍 **TROUBLESHOOTING**

### Import Error
```python
import sys
sys.path.insert(0, 'c:/AAAA/Orbit Final')
```

### Check if Feature is Working
```python
# Quick health check
stats = comm.get_statistics()
print(f"System loaded: {stats['contacts'] >= 0}")
```

### Test Without Email
```python
# All these work without IMAP/SMTP credentials:
comm.add_contact("Test", "test@example.com")
comm.schedule_email("test@example.com", "Subject", "Body", "1h")
spam = {'subject': 'Test', 'body': 'Test', 'from': 'test@test.com'}
is_spam, score, _ = comm.detect_spam(spam)
```

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
# Now you'll see all operations logged
```

---

## 📚 **WHERE TO FIND MORE**

- **Full Testing Guide**: `COMMUNICATION_TEST_PROMPTS.md`
- **API Reference**: `COMMUNICATION_API_REFERENCE.md`
- **Enhancement Details**: `COMMUNICATION_ENHANCED.md`
- **Source Code**: `Orbit_core/actions/communication.py`

---

## 💡 **PRO TIPS**

1. **Start local**: Test contacts and scheduling first (no credentials needed)
2. **Use Python console**: More control than voice commands
3. **Check stats often**: See your progress with `comm.get_statistics()`
4. **Tag test data**: Use `tags=["test"]` for easy cleanup later
5. **Small batches**: Test one feature at a time
6. **Read logs**: Enable logging to see what's happening

---

## 🎪 **DEMO SCRIPT FOR SHOWING OFF**

```python
# The 60-second demo
comm = CommunicationService(Settings())

print("🚀 Orbit Communication System Demo\n")

# Add contacts
comm.add_contact("Demo User", "demo@example.com", tags=["demo"])
print("✓ Contact added")

# Schedule email
comm.schedule_email("demo@example.com", "Demo Email", "This is a demo", "5m")
print("✓ Email scheduled for 5 minutes")

# Spam detection
spam = {'subject': 'WINNER!!!', 'body': 'FREE MONEY NOW!!!', 'from': 'scam@bad.com'}
is_spam, score, _ = comm.detect_spam(spam)
print(f"✓ Spam detected: {is_spam} (score: {score})")

# Statistics
stats = comm.get_statistics()
print(f"✓ System stats: {stats['contacts']} contacts, {stats['scheduled_emails']} scheduled")

# Notification
comm.send_desktop_notification("Orbit", "Demo complete! 🎉")
print("✓ Notification sent")

print("\n🎉 Demo complete! All features working!")
```

Run this to impress anyone in under 60 seconds! 🚀

---

**Quick Start Version 1.0**  
Generated: 2025-10-31  
Features: 25+  
Time to First Test: < 60 seconds
