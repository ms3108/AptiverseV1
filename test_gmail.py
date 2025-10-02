#!/usr/bin/env python3
"""Test Gmail SMTP connection"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your credentials
GMAIL_USER = "misna5984@gmail.com"
GMAIL_APP_PASSWORD = "xvibtvqnsshccbgu"  # The password from .env

print("=" * 70)
print("Testing Gmail SMTP Connection")
print("=" * 70)
print(f"\nGmail Account: {GMAIL_USER}")
print(f"App Password: {GMAIL_APP_PASSWORD[:4]}{'*' * (len(GMAIL_APP_PASSWORD) - 4)}")
print(f"App Password Length: {len(GMAIL_APP_PASSWORD)} characters")
print("\nAttempting to connect to Gmail SMTP server...\n")

try:
    # Create SMTP connection
    print("Step 1: Connecting to smtp.gmail.com:587...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    
    print("Step 2: Starting TLS encryption...")
    server.starttls()
    
    print("Step 3: Logging in with credentials...")
    server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Gmail SMTP connection works!")
    print("=" * 70)
    print("\nYour credentials are correct.")
    print("The issue might be with the backend container not reading .env properly.")
    
    server.quit()
    
except smtplib.SMTPAuthenticationError as e:
    print("\n" + "=" * 70)
    print("❌ AUTHENTICATION FAILED!")
    print("=" * 70)
    print(f"\nError: {e}")
    print("\nPossible reasons:")
    print("1. App Password is INCORRECT")
    print("2. 2-Step Verification is NOT enabled")
    print("3. You copied the password with spaces")
    print("\nVerify:")
    print(f"   - Go to: https://myaccount.google.com/apppasswords")
    print(f"   - Delete old password and create a NEW one")
    print(f"   - Copy it WITHOUT spaces: abcdefghijklmnop")
    print(f"   - Update .env file")
    
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ CONNECTION ERROR!")
    print("=" * 70)
    print(f"\nError: {e}")
    print("\nCheck your internet connection.")
