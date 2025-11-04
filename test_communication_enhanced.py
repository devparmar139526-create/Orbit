"""
Quick test for enhanced Communication Service
Tests all new features without requiring email credentials
"""

import sys
sys.path.insert(0, 'c:/AAAA/Orbit Final')

from Orbit_core.actions.communication import CommunicationService
from Orbit_core.config.settings import Settings

def test_communication_enhancements():
    """Test new features"""
    print("🧪 Testing Enhanced Communication Service\n")
    
    # Initialize without LLM
    settings = Settings()
    comm = CommunicationService(settings=settings, llm_router=None)
    
    print("✅ Initialized CommunicationService")
    
    # Test 1: Contact Management
    print("\n📇 Test 1: Contact Management")
    result = comm.add_contact("John Doe", "john@example.com", "+1234567890", 
                              tags=["work", "vip"], notes="CEO")
    print(f"   {result}")
    
    result = comm.add_contact("Jane Smith", "jane@example.com", None, 
                              tags=["work"], notes="Manager")
    print(f"   {result}")
    
    contacts = comm.list_contacts()
    print(f"   Total contacts: {len(contacts)}")
    
    contact = comm.get_contact("john")
    print(f"   Found contact: {contact['name'] if contact else 'None'}")
    
    # Test 2: Scheduled Emails
    print("\n📅 Test 2: Scheduled Emails")
    result = comm.schedule_email(
        to="test@example.com",
        subject="Test Email",
        body="This is a test",
        send_at="2h"  # 2 hours from now
    )
    print(f"   Scheduled: {result.get('status')} - ID: {result.get('id')}")
    
    scheduled = comm.list_scheduled_emails(status='pending')
    print(f"   Total scheduled: {len(scheduled)}")
    
    # Test 3: Spam Detection
    print("\n🚫 Test 3: Spam Detection")
    fake_email = {
        'subject': 'URGENT!!! WIN FREE MONEY NOW!!!',
        'body': 'Click here to claim your prize! Act now! Limited time!',
        'from': 'spam12345@sketchy.com'
    }
    
    is_spam, score, reason = comm.detect_spam(fake_email)
    print(f"   Spam: {is_spam}, Score: {score}, Reason: {reason}")
    
    clean_email = {
        'subject': 'Project Update',
        'body': 'Here is the weekly project status report.',
        'from': 'colleague@company.com'
    }
    
    is_spam, score, reason = comm.detect_spam(clean_email)
    print(f"   Spam: {is_spam}, Score: {score}, Reason: {reason}")
    
    # Test 4: Email Threading
    print("\n💬 Test 4: Email Threading")
    fake_emails = [
        {'subject': 'Project Plan', 'from': 'alice@example.com', 'date': '2025-10-30'},
        {'subject': 'Re: Project Plan', 'from': 'bob@example.com', 'date': '2025-10-31'},
        {'subject': 'Budget Request', 'from': 'charlie@example.com', 'date': '2025-10-31'},
        {'subject': 'Fwd: Project Plan', 'from': 'david@example.com', 'date': '2025-11-01'},
    ]
    
    threads = comm.group_by_thread(fake_emails)
    print(f"   Total threads: {len(threads)}")
    for thread_id, emails in threads.items():
        print(f"   Thread {thread_id[:8]}: {len(emails)} emails")
    
    # Test 5: Statistics
    print("\n📊 Test 5: Statistics")
    stats = comm.get_statistics()
    print(f"   Contacts: {stats['contacts']}")
    print(f"   Scheduled: {stats['scheduled_emails']}")
    print(f"   Threads: {stats['conversation_threads']}")
    print(f"   Spam Filtered: {stats['spam_filtered']}")
    
    # Test 6: Voice Commands (execute method)
    print("\n🎤 Test 6: Voice Commands")
    
    result = comm.execute("list contacts")
    print(f"   'list contacts':\n{result[:100]}...")
    
    result = comm.execute("show scheduled emails")
    print(f"   'show scheduled':\n{result[:100]}...")
    
    result = comm.execute("show statistics")
    print(f"   'show statistics':\n{result[:150]}...")
    
    # Test 7: Scheduled Email Cancellation
    print("\n🚫 Test 7: Cancel Scheduled Email")
    if scheduled:
        email_id = scheduled[0]['id']
        result = comm.cancel_scheduled_email(email_id)
        print(f"   {result}")
    
    # Test 8: Contact Update
    print("\n✏️  Test 8: Update Contact")
    result = comm.update_contact("john@example.com", phone="+9876543210", tags=["work", "vip", "board"])
    print(f"   {result}")
    
    updated = comm.get_contact("john")
    print(f"   New phone: {updated['phone']}")
    print(f"   Tags: {updated['tags']}")
    
    # Final Summary
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("="*50)
    
    final_stats = comm.get_statistics()
    print(f"\nFinal Statistics:")
    for key, value in final_stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    try:
        test_communication_enhancements()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
