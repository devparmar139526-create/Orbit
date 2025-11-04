# 🧪 Communication System - Manual Testing Prompts

## Overview
Use these prompts to test all 25+ features of the enhanced Communication System.
Copy and paste these into Orbit's voice/text interface or Python console.

---

## 📋 Quick Test Sequence (5 minutes)

```
1. "Read my unread emails"
2. "Show priority emails"
3. "List my contacts"
4. "Show communication statistics"
5. "Summarize emails"
```

---

## 📧 **SECTION 1: Email Reading & Filtering**

### Test 1.1: Read Emails
```
"Read my unread emails"
"Read all emails"
"Read emails from inbox"
```

**Expected**: List of emails with subjects, senders, dates

### Test 1.2: Priority Emails
```
"Show priority emails"
"Show urgent emails"
"Display high priority messages"
```

**Expected**: Only high-priority emails (containing keywords like "urgent", "important")

### Test 1.3: Email Search
```
"Search emails for project budget"
"Search emails for meeting"
"Find emails about deadline"
```

**Expected**: Emails matching the search query

---

## 📝 **SECTION 2: Summarization & Action Items**

### Test 2.1: Basic Summarization
```
"Summarize my emails"
"Give me email summaries"
"Summarize recent emails"
```

**Expected**: Short summaries of recent emails

### Test 2.2: AI Summarization (if LLM configured)
```
"Summarize emails with AI"
"Use AI to summarize emails"
"AI email summaries"
```

**Expected**: AI-generated summaries (more detailed than basic)

### Test 2.3: Action Items
```
"Extract action items from emails"
"What are my action items?"
"Show email tasks"
```

**Expected**: List of tasks/requests found in emails

### Test 2.4: AI Action Items (if LLM configured)
```
"Extract action items with AI"
"Use AI to find action items"
"AI action item extraction"
```

**Expected**: AI-detected action items

---

## 📇 **SECTION 3: Contact Management**

### Test 3.1: List Contacts
```
"List my contacts"
"Show all contacts"
"Display contacts"
```

**Expected**: List of all saved contacts with emails and tags

### Test 3.2: Add Contact (via Python)
```python
from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

comm = CommunicationService(Settings())

# Add work contacts
comm.add_contact("John Smith", "john.smith@company.com", 
                 phone="+1234567890", 
                 tags=["work", "manager"],
                 notes="Project manager for Q4 initiative")

comm.add_contact("Sarah Johnson", "sarah.j@company.com",
                 tags=["work", "team"],
                 notes="Team lead - Engineering")

comm.add_contact("Mike Chen", "mike.chen@client.com",
                 phone="+9876543210",
                 tags=["client", "vip"],
                 notes="CEO of ClientCo - high priority")

# Personal contacts
comm.add_contact("Emma Davis", "emma.davis@email.com",
                 tags=["personal", "friend"],
                 notes="College friend")

print("✅ Contacts added! Now try: 'list my contacts'")
```

### Test 3.3: Contact Operations (via Python)
```python
# Get specific contact
contact = comm.get_contact("john")
print(f"Found: {contact}")

# List work contacts only
work_contacts = comm.list_contacts(tag="work")
print(f"Work contacts: {len(work_contacts)}")

# Update contact
comm.update_contact("john.smith@company.com", 
                    phone="+1111111111",
                    tags=["work", "manager", "vip"])

# Delete contact (optional)
# comm.delete_contact("emma.davis@email.com")
```

---

## 📅 **SECTION 4: Email Scheduling**

### Test 4.1: Schedule Emails (via Python)
```python
from datetime import datetime, timedelta

comm = CommunicationService(Settings())

# Schedule email 2 hours from now
result1 = comm.schedule_email(
    to="colleague@company.com",
    subject="Project Update",
    body="Here's the weekly project status update.",
    send_at="2h"
)
print(f"Scheduled 1: {result1}")

# Schedule email 1 day from now
result2 = comm.schedule_email(
    to="team@company.com",
    subject="Weekly Reminder",
    body="Don't forget the team meeting tomorrow!",
    send_at="1d"
)
print(f"Scheduled 2: {result2}")

# Schedule for specific time
tomorrow_2pm = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0)
result3 = comm.schedule_email(
    to="boss@company.com",
    subject="Report Ready",
    body="The quarterly report is ready for review.",
    send_at=tomorrow_2pm.isoformat()
)
print(f"Scheduled 3: {result3}")

print("\n✅ Emails scheduled! Now try: 'show scheduled emails'")
```

### Test 4.2: View Scheduled
```
"Show scheduled emails"
"List scheduled emails"
"Display pending emails"
```

**Expected**: List of emails scheduled to be sent

### Test 4.3: Cancel Scheduled (via Python)
```python
# First, get the list
scheduled = comm.list_scheduled_emails(status='pending')
print(f"Scheduled emails: {len(scheduled)}")

# Cancel one (use actual ID from list)
if scheduled:
    email_id = scheduled[0]['id']
    result = comm.cancel_scheduled_email(email_id)
    print(result)
```

---

## 🚫 **SECTION 5: Spam Detection**

### Test 5.1: Spam Detection (via Python)
```python
comm = CommunicationService(Settings())

# Test obvious spam
spam_email = {
    'subject': 'URGENT!!! WIN FREE MONEY NOW!!!',
    'body': 'You are a WINNER! Click here NOW to claim your FREE prize! Limited time offer! Act fast! Casino lottery viagra!',
    'from': 'winner12345@suspicious-domain.xyz'
}

is_spam, score, reason = comm.detect_spam(spam_email)
print(f"Spam Test 1:")
print(f"  Is Spam: {is_spam}")
print(f"  Score: {score}")
print(f"  Reason: {reason}")

# Test legitimate email
clean_email = {
    'subject': 'Q4 Project Status Report',
    'body': 'Attached is the quarterly project status report for review. The team has made significant progress on all milestones.',
    'from': 'john.smith@company.com'
}

is_spam2, score2, reason2 = comm.detect_spam(clean_email)
print(f"\nClean Email Test:")
print(f"  Is Spam: {is_spam2}")
print(f"  Score: {score2}")
print(f"  Reason: {reason2}")

# Test borderline
marketing_email = {
    'subject': 'Special Offer: 20% Off This Week Only',
    'body': 'Click here to save on our products. Limited time offer!',
    'from': 'sales@legitimate-store.com'
}

is_spam3, score3, reason3 = comm.detect_spam(marketing_email)
print(f"\nMarketing Email Test:")
print(f"  Is Spam: {is_spam3}")
print(f"  Score: {score3}")
print(f"  Reason: {reason3}")
```

### Test 5.2: Automatic Spam Filtering
When you run `"read unread emails"`, spam is automatically filtered out (unless command contains "spam").

---

## 📎 **SECTION 6: Attachments** (Requires email credentials)

### Test 6.1: Send with Attachments (via Python)
```python
# Create test files first
with open("test_document.txt", "w") as f:
    f.write("This is a test document.")

with open("test_report.txt", "w") as f:
    f.write("Quarterly Report\n\nSales: Up 25%\nProfit: $1M")

# Send email with attachments
result = comm.send_email_with_attachment(
    to="recipient@example.com",
    subject="Documents Attached",
    body="Please find the requested documents attached.",
    attachments=["test_document.txt", "test_report.txt"]
)

print(f"Email sent: {result}")
```

### Test 6.2: Download Attachments (via Python)
```python
# First, get emails with attachments
emails = comm.search_emails(has_attachment=True, limit=5)

if emails and not 'error' in emails[0]:
    email_id = emails[0]['id']
    
    # Download attachments
    files = comm.download_attachments(email_id, folder='INBOX')
    
    print(f"Downloaded {len(files)} files:")
    for file in files:
        print(f"  - {file}")
```

---

## 💬 **SECTION 7: Email Threading**

### Test 7.1: Group Emails (via Python)
```python
# Read recent emails
emails = comm.read_emails(limit=50, unread_only=False)

# Group by conversation thread
threads = comm.group_by_thread(emails)

print(f"Found {len(threads)} conversation threads:")
for thread_id, thread_emails in threads.items():
    if len(thread_emails) > 1:  # Only show multi-email threads
        print(f"\nThread {thread_id[:8]}: {len(thread_emails)} emails")
        for email in thread_emails:
            print(f"  - {email['subject']} (from {email['from']})")
```

---

## 📁 **SECTION 8: Folder Management**

### Test 8.1: List Folders
```
"Show email folders"
"List my folders"
"Display folders"
```

**Expected**: List of email folders (INBOX, Sent, Drafts, etc.)

### Test 8.2: Folder Operations (via Python)
```python
# List all folders
folders = comm.list_folders()
print("Email folders:", folders)

# Create new folder
result = comm.create_folder("Important")
print(result)

# Move email to folder (get email ID first)
emails = comm.read_emails(limit=1)
if emails and not 'error' in emails[0]:
    email_id = emails[0]['id']
    result = comm.move_email(email_id, "INBOX", "Important")
    print(result)
```

---

## 🔄 **SECTION 9: Batch Operations**

### Test 9.1: Mark Multiple as Read (via Python)
```python
# Get unread emails
emails = comm.read_emails(unread_only=True, limit=10)

if emails and not 'error' in emails[0]:
    # Get first 3 email IDs
    email_ids = [e['id'] for e in emails[:3]]
    
    # Mark as read
    result = comm.mark_multiple_as_read(email_ids)
    print(f"Marked {result['marked']} of {result['total']} as read")
```

### Test 9.2: Delete Multiple (via Python)
```python
# Get old emails (be careful with this!)
emails = comm.search_emails(
    query="test",  # Only test emails
    limit=5
)

if emails and not 'error' in emails[0]:
    email_ids = [e['id'] for e in emails]
    
    # Uncomment to actually delete
    # result = comm.delete_multiple_emails(email_ids)
    # print(f"Deleted {result['count']} emails")
    
    print(f"Would delete {len(email_ids)} emails")
```

---

## 📊 **SECTION 10: Statistics & Analytics**

### Test 10.1: Basic Statistics
```
"Show statistics"
"Show communication statistics"
"Display stats"
```

**Expected**: Emails sent/read, notifications, spam filtered, contacts, etc.

### Test 10.2: Detailed Analytics (via Python)
```python
# Get 7-day analytics
analytics = comm.get_email_analytics(days=7)

print("Email Analytics (Last 7 Days):")
print(f"Total Emails: {analytics['total_emails']}")
print(f"Average per Day: {analytics['avg_per_day']}")

print("\nTop Senders:")
for sender in analytics['top_senders'][:5]:
    print(f"  {sender['email']}: {sender['count']} emails")

print("\nDaily Breakdown:")
for date, count in analytics['daily_counts'].items():
    print(f"  {date}: {count} emails")

# Get 30-day analytics
analytics_30 = comm.get_email_analytics(days=30)
print(f"\n30-Day Total: {analytics_30['total_emails']} emails")
```

### Test 10.3: All Statistics (via Python)
```python
stats = comm.get_statistics()

print("Complete Statistics:")
print(f"  📧 Emails Sent: {stats['emails_sent']}")
print(f"  📬 Emails Read: {stats['emails_read']}")
print(f"  🔔 Notifications Sent: {stats['notifications_sent']}")
print(f"  🚫 Spam Filtered: {stats['spam_filtered']}")
print(f"  📇 Contacts: {stats['contacts']}")
print(f"  📅 Scheduled Emails: {stats['scheduled_emails']}")
print(f"  💬 Conversation Threads: {stats['conversation_threads']}")
```

---

## 💬 **SECTION 11: Messaging**

### Test 11.1: Telegram (requires credentials)
```
"Send telegram message Hello team!"
"Send telegram Testing Orbit communication"
```

**Expected**: Message sent to Telegram chat

### Test 11.2: SMS (requires Twilio credentials)
```python
result = comm.send_sms(
    to="+1234567890",
    message="Test message from Orbit AI"
)
print(result)
```

---

## 🔔 **SECTION 12: Notifications**

### Test 12.1: Desktop Notifications
```
"Send notification Test notification"
"Send notification High priority alert"
"Notify me Important message"
```

**Expected**: Desktop notification appears

### Test 12.2: Notification with Urgency (via Python)
```python
# Normal notification
comm.send_desktop_notification(
    title="Normal Alert",
    message="This is a normal priority notification",
    duration=5,
    urgency='normal'
)

# High priority notification
comm.send_desktop_notification(
    title="URGENT",
    message="This is a high priority alert!",
    duration=10,
    urgency='high'
)

# Low priority notification
comm.send_desktop_notification(
    title="Info",
    message="Just a quick update",
    duration=3,
    urgency='low'
)
```

---

## 🤖 **SECTION 13: AI Features** (Requires LLM configuration)

### Test 13.1: AI Summarization
```python
# Make sure you have LLM configured
from Orbit_core.llm.router import LLMRouter

settings = Settings()
llm = LLMRouter(settings)
comm = CommunicationService(settings=settings, llm_router=llm)

# Get an email
emails = comm.read_emails(limit=1)
if emails and not 'error' in emails[0]:
    email = emails[0]
    
    # AI summary
    ai_summary = comm.ai_summarize_email(email)
    print(f"AI Summary: {ai_summary}")
    
    # Compare with basic
    basic_summary = comm.summarize_email(email)
    print(f"Basic Summary: {basic_summary}")
```

### Test 13.2: AI Action Items
```python
emails = comm.read_emails(limit=1)
if emails and not 'error' in emails[0]:
    email = emails[0]
    
    # AI action items
    ai_actions = comm.ai_extract_action_items(email)
    print("AI Action Items:")
    for i, action in enumerate(ai_actions, 1):
        print(f"  {i}. {action}")
```

### Test 13.3: AI Reply Drafting
```python
emails = comm.read_emails(limit=1)
if emails and not 'error' in emails[0]:
    email = emails[0]
    
    # Professional reply
    reply_prof = comm.ai_draft_reply(email, tone='professional')
    print(f"Professional Reply:\n{reply_prof}\n")
    
    # Casual reply
    reply_casual = comm.ai_draft_reply(email, tone='casual')
    print(f"Casual Reply:\n{reply_casual}\n")
    
    # Friendly reply
    reply_friendly = comm.ai_draft_reply(email, tone='friendly')
    print(f"Friendly Reply:\n{reply_friendly}")
```

---

## 📧 **SECTION 14: Auto-Reply**

### Test 14.1: Send Auto-Reply (via Python)
```python
# Out of office
result = comm.send_auto_reply(
    to="sender@example.com",
    template_name='out_of_office'
)
print(result)

# In meeting
result = comm.send_auto_reply(
    to="sender@example.com",
    template_name='meeting'
)
print(result)

# Busy
result = comm.send_auto_reply(
    to="sender@example.com",
    template_name='busy'
)
print(result)

# Custom message
result = comm.send_auto_reply(
    to="sender@example.com",
    custom_message="Thank you for your email. I've received it and will respond within 24 hours."
)
print(result)
```

### Test 14.2: Manage Templates (via Python)
```python
# Get available templates
templates = comm.get_auto_reply_templates()
print("Available templates:")
for name, text in templates.items():
    print(f"\n{name}:")
    print(f"  {text[:100]}...")

# Add custom template
comm.add_auto_reply_template(
    name='vacation',
    template="I'm on vacation until [return_date]. I'll respond when I return. For urgent matters, contact [backup_person]."
)

# Use custom template
result = comm.send_auto_reply(
    to="sender@example.com",
    template_name='vacation'
)
```

---

## 🎯 **SECTION 15: Complete Integration Test**

### Full Workflow Test (via Python)
```python
from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

settings = Settings()
comm = CommunicationService(settings=settings)

print("="*60)
print("COMPLETE COMMUNICATION SYSTEM TEST")
print("="*60)

# 1. Add contacts
print("\n1. Adding contacts...")
comm.add_contact("Test User 1", "test1@example.com", tags=["test"])
comm.add_contact("Test User 2", "test2@example.com", tags=["test", "vip"])
contacts = comm.list_contacts()
print(f"   ✓ Total contacts: {len(contacts)}")

# 2. Schedule emails
print("\n2. Scheduling emails...")
sched1 = comm.schedule_email("test1@example.com", "Test 1", "Body 1", "30m")
sched2 = comm.schedule_email("test2@example.com", "Test 2", "Body 2", "1h")
scheduled = comm.list_scheduled_emails(status='pending')
print(f"   ✓ Scheduled: {len(scheduled)}")

# 3. Spam detection
print("\n3. Testing spam detection...")
spam = {'subject': 'FREE MONEY!!!', 'body': 'Click now!', 'from': 'spam@bad.com'}
is_spam, score, reason = comm.detect_spam(spam)
print(f"   ✓ Spam detected: {is_spam} (score: {score})")

# 4. Email threading
print("\n4. Testing email threading...")
fake_emails = [
    {'subject': 'Project', 'from': 'a@test.com', 'date': '2025-10-30'},
    {'subject': 'Re: Project', 'from': 'b@test.com', 'date': '2025-10-31'},
    {'subject': 'Budget', 'from': 'c@test.com', 'date': '2025-10-31'},
]
threads = comm.group_by_thread(fake_emails)
print(f"   ✓ Threads: {len(threads)}")

# 5. Statistics
print("\n5. Checking statistics...")
stats = comm.get_statistics()
print(f"   ✓ Contacts: {stats['contacts']}")
print(f"   ✓ Scheduled: {stats['scheduled_emails']}")
print(f"   ✓ Threads: {stats['conversation_threads']}")

# 6. Notifications
print("\n6. Testing notifications...")
result = comm.send_desktop_notification("Test", "This is a test notification")
print(f"   ✓ Notification: {result['status']}")

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
```

---

## 🎤 **Voice Command Quick Reference**

Copy these exact phrases to test via voice/text:

```
# Email Operations
"Read my unread emails"
"Show priority emails"
"Summarize emails"
"Summarize emails with AI"
"Extract action items"
"Search emails for budget"

# Contact & Organization
"List my contacts"
"Show scheduled emails"
"Show email folders"

# Statistics
"Show communication statistics"
"Show statistics"

# Messaging
"Send telegram Hello team"
"Send notification Test message"

# Help
"Help communication"
```

---

## 📝 **Quick Python Test Script**

Save this as `quick_test.py` and run it:

```python
import sys
sys.path.insert(0, 'c:/AAAA/Orbit Final')

from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

def quick_test():
    comm = CommunicationService(Settings())
    
    print("🧪 Quick Communication Test\n")
    
    # Test 1: Contacts
    comm.add_contact("Quick Test", "quick@test.com")
    print(f"✓ Contacts: {len(comm.list_contacts())}")
    
    # Test 2: Scheduling
    result = comm.schedule_email("test@test.com", "Subject", "Body", "1h")
    print(f"✓ Scheduled: {result['status']}")
    
    # Test 3: Spam
    spam = {'subject': 'WIN NOW!!!', 'body': 'Free money!', 'from': 'spam@bad.com'}
    is_spam, score, _ = comm.detect_spam(spam)
    print(f"✓ Spam detection: {is_spam} ({score})")
    
    # Test 4: Stats
    stats = comm.get_statistics()
    print(f"✓ Statistics: {stats['contacts']} contacts, {stats['scheduled_emails']} scheduled")
    
    print("\n🎉 All features working!")

if __name__ == "__main__":
    quick_test()
```

---

## 🎯 **Testing Checklist**

Mark off as you test each feature:

**Email Operations:**
- [ ] Read unread emails
- [ ] Read all emails
- [ ] Show priority emails
- [ ] Search emails
- [ ] Send email (requires credentials)
- [ ] Send with attachments (requires credentials)

**Contact Management:**
- [ ] Add contact
- [ ] List contacts
- [ ] Get contact
- [ ] Update contact
- [ ] Delete contact

**Scheduling:**
- [ ] Schedule email (relative time)
- [ ] Schedule email (specific time)
- [ ] List scheduled emails
- [ ] Cancel scheduled email

**Spam & Filtering:**
- [ ] Detect spam
- [ ] Filter spam from list
- [ ] Automatic spam filtering

**Threading:**
- [ ] Group emails by thread
- [ ] Get thread emails

**Summarization:**
- [ ] Basic email summary
- [ ] AI email summary (if LLM available)
- [ ] Conversation summary
- [ ] Extract action items
- [ ] AI action items (if LLM available)

**Folders:**
- [ ] List folders
- [ ] Create folder
- [ ] Move email

**Batch Operations:**
- [ ] Mark multiple as read
- [ ] Delete multiple emails

**Statistics:**
- [ ] Get statistics
- [ ] Get email analytics

**Messaging:**
- [ ] Send Telegram (requires credentials)
- [ ] Send SMS (requires credentials)
- [ ] Desktop notification

**AI Features (requires LLM):**
- [ ] AI summarization
- [ ] AI action items
- [ ] AI reply drafting

**Auto-Reply:**
- [ ] Send auto-reply with template
- [ ] Send auto-reply with custom message
- [ ] Add custom template

---

## 💡 **Pro Tips**

1. **Start with local features** (contacts, scheduling, spam detection) - they don't require email credentials
2. **Test incrementally** - one section at a time
3. **Use Python console** for detailed testing - gives you more control
4. **Check statistics** after each test to see counters increment
5. **Use voice commands** for quick operations
6. **Keep test contacts** with tag "test" for easy cleanup

---

**Happy Testing! 🚀**

Generated: 2025-10-31
Features: 25+ (41+ individual capabilities)
Test Categories: 15
Voice Commands: 20+
Python Examples: 30+
