#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for your application.
Run this script to generate a random secret key for use in production.

Usage:
    python generate_secret_key.py
"""

import secrets
import string

def generate_secret_key(length=64):
    """
    Generate a cryptographically secure random secret key.
    
    Args:
        length (int): Length of the secret key (default: 64)
    
    Returns:
        str: A secure random string
    """
    # Use secrets module for cryptographically strong random generation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

def main():
    print("=" * 70)
    print("SECRET KEY GENERATOR")
    print("=" * 70)
    print()
    print("Generating a secure random secret key for your application...")
    print()
    
    # Generate secret key
    secret_key = generate_secret_key(64)
    
    print("Your new SECRET_KEY:")
    print("-" * 70)
    print(secret_key)
    print("-" * 70)
    print()
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Copy this key and store it securely")
    print("2. Add it to your Render environment variables as SECRET_KEY")
    print("3. Never commit this key to version control")
    print("4. Never share this key publicly")
    print("5. Rotate this key every 3-6 months")
    print()
    print("For Render deployment:")
    print("  1. Go to Render Dashboard")
    print("  2. Select your service")
    print("  3. Go to Environment tab")
    print("  4. Add variable: SECRET_KEY = [paste the key above]")
    print("  5. Save and redeploy")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
