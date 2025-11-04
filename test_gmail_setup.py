"""
Gmail IMAP Connection Tester
Run this after completing the setup steps
"""
import imaplib
import sys

def test_gmail_connection():
    print("="*60)
    print("GMAIL IMAP CONNECTION TEST")
    print("="*60)
    
    # Get credentials
    email = input("\nEnter your Gmail address (e.g., yourname@gmail.com): ").strip()
    password = input("Enter your App Password (16 characters): ").strip()
    
    # Remove spaces if user copied with spaces
    password_clean = password.replace(" ", "")
    
    print(f"\n📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password_clean)} (length: {len(password_clean)})")
    
    if len(password_clean) != 16:
        print(f"\n❌ ERROR: App password should be 16 characters, but yours is {len(password_clean)}")
        print("   Make sure you copied the ENTIRE password from Google.")
        return False
    
    print("\n🔄 Attempting connection to imap.gmail.com:993...")
    
    try:
        # Connect
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        print("   ✅ Connected to Gmail IMAP server")
        
        # Login
        print("\n🔐 Attempting login...")
        mail.login(email, password_clean)
        print("   ✅ LOGIN SUCCESSFUL!")
        
        # Test folder access
        print("\n📁 Listing folders...")
        status, folders = mail.list()
        print(f"   ✅ Found {len(folders)} folders")
        
        # Test inbox access
        print("\n📬 Accessing INBOX...")
        status, messages = mail.select('INBOX')
        email_count = int(messages[0])
        print(f"   ✅ INBOX has {email_count} emails")
        
        # Logout
        mail.logout()
        
        print("\n" + "="*60)
        print("🎉 SUCCESS! Gmail IMAP is working perfectly!")
        print("="*60)
        print("\nYou can now use Orbit's email features:")
        print('  - "Read my unread emails"')
        print('  - "Show priority emails"')
        print('  - "Search emails for [topic]"')
        print("\nNext step: Update your .env file with these credentials")
        
        return True
        
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        print(f"\n❌ LOGIN FAILED: {error_msg}")
        
        if 'AUTHENTICATIONFAILED' in error_msg:
            print("\n🔍 TROUBLESHOOTING:")
            print("\n1. Is 2-Step Verification enabled?")
            print("   → Check: https://myaccount.google.com/security")
            print("   → You should see '2-Step Verification is ON'")
            
            print("\n2. Is IMAP enabled in Gmail?")
            print("   → Check: https://mail.google.com/mail/u/0/#settings/fwdandpop")
            print("   → 'Enable IMAP' should be selected")
            print("   → Make sure you clicked 'Save Changes'")
            print("   → Wait 5-10 minutes after enabling")
            
            print("\n3. Is the App Password correct?")
            print("   → Generate a NEW one: https://myaccount.google.com/apppasswords")
            print("   → App name: 'Orbit AI'")
            print("   → Copy the 16-character password EXACTLY")
            
            print("\n4. Account security restrictions?")
            print("   → Check: https://myaccount.google.com/security")
            print("   → Look for any security alerts or restrictions")
            print("   → Make sure 'Less secure app access' is not relevant (app passwords bypass this)")
        
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("\nThis might be a network issue or firewall blocking port 993")
        return False

if __name__ == "__main__":
    print("\n📋 BEFORE YOU RUN THIS TEST:")
    print("   1. Enable 2-Step Verification: https://myaccount.google.com/security")
    print("   2. Enable IMAP: https://mail.google.com/mail/u/0/#settings/fwdandpop")
    print("   3. Generate App Password: https://myaccount.google.com/apppasswords")
    print("   4. Wait 5-10 minutes after enabling IMAP")
    print()
    
    ready = input("Have you completed all steps above? (yes/no): ").strip().lower()
    
    if ready == 'yes' or ready == 'y':
        test_gmail_connection()
    else:
        print("\n⚠️  Please complete the setup steps first, then run this test again.")
        print("   Command: python test_gmail_setup.py")
