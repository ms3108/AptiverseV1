"""
Notifications Service — Aptiverse
Handles email (SendGrid) and SMS (Twilio) notifications with fallback to console.
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@aptiverse.app")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

# Console mode flag
CONSOLE_MODE = not all([SENDGRID_API_KEY, SENDGRID_FROM_EMAIL])

# ============================================================================
# SendGrid Email Integration
# ============================================================================

def send_email_sendgrid(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    text_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email using SendGrid API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content
        from_email: Sender email (optional, uses default)
        text_content: Plain text fallback (optional)
    
    Returns:
        Dict with success status and message
    """
    if CONSOLE_MODE:
        return _send_email_console(to_email, subject, html_content, text_content)
    
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Content, Email, To
        
        # Initialize SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Build email
        from_email_obj = Email(from_email or SENDGRID_FROM_EMAIL)
        to_email_obj = To(to_email)
        content_html = Content("text/html", html_content)
        
        mail = Mail(from_email_obj, to_email_obj, subject, content_html)
        
        # Add plain text content if provided
        if text_content:
            content_text = Content("text/plain", text_content)
            mail.add_content(content_text)
        
        # Send email
        response = sg.send(mail)
        
        if response.status_code == 202:
            logger.info(f"✅ Email sent successfully to {to_email}")
            return {
                "success": True,
                "message": "Email sent successfully",
                "status_code": response.status_code,
                "provider": "sendgrid"
            }
        else:
            logger.error(f"❌ SendGrid error: {response.status_code} - {response.body}")
            return {
                "success": False,
                "message": f"SendGrid error: {response.status_code}",
                "error": response.body,
                "provider": "sendgrid"
            }
            
    except ImportError:
        logger.warning("⚠️ SendGrid package not installed, falling back to console")
        return _send_email_console(to_email, subject, html_content, text_content)
    except Exception as e:
        logger.error(f"❌ SendGrid exception: {str(e)}")
        return {
            "success": False,
            "message": f"SendGrid exception: {str(e)}",
            "provider": "sendgrid"
        }

def _send_email_console(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Console fallback for email sending (development/testing).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n📧 EMAIL CONSOLE MODE - {timestamp}")
    print(f"📬 To: {to_email}")
    print(f"📋 Subject: {subject}")
    print(f"📄 HTML Content: {html_content[:100]}...")
    if text_content:
        print(f"📝 Text Content: {text_content[:100]}...")
    print(f"🔧 From: {SENDGRID_FROM_EMAIL}")
    print("=" * 50)
    
    return {
        "success": True,
        "message": "Email sent to console (development mode)",
        "provider": "console",
        "console_mode": True
    }

# ============================================================================
# Twilio SMS Integration
# ============================================================================

def send_sms_twilio(
    to_phone: str,
    body: str,
    from_number: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send SMS using Twilio API.
    
    Args:
        to_phone: Recipient phone number (with country code, e.g., +1234567890)
        body: SMS message content
        from_number: Sender phone number (optional, uses default)
    
    Returns:
        Dict with success status and message
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        return _send_sms_console(to_phone, body)
    
    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException
        
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS
        message = client.messages.create(
            body=body,
            from_=from_number or TWILIO_FROM_NUMBER,
            to=to_phone
        )
        
        logger.info(f"✅ SMS sent successfully to {to_phone} (SID: {message.sid})")
        return {
            "success": True,
            "message": "SMS sent successfully",
            "message_sid": message.sid,
            "status": message.status,
            "provider": "twilio"
        }
        
    except ImportError:
        logger.warning("⚠️ Twilio package not installed, falling back to console")
        return _send_sms_console(to_phone, body)
    except TwilioRestException as e:
        logger.error(f"❌ Twilio error: {str(e)}")
        return {
            "success": False,
            "message": f"Twilio error: {str(e)}",
            "provider": "twilio"
        }
    except Exception as e:
        logger.error(f"❌ Twilio exception: {str(e)}")
        return {
            "success": False,
            "message": f"Twilio exception: {str(e)}",
            "provider": "twilio"
        }

def _send_sms_console(
    to_phone: str,
    body: str
) -> Dict[str, Any]:
    """
    Console fallback for SMS sending (development/testing).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n📱 SMS CONSOLE MODE - {timestamp}")
    print(f"📞 To: {to_phone}")
    print(f"💬 Message: {body}")
    print(f"🔧 From: {TWILIO_FROM_NUMBER or 'Not configured'}")
    print("=" * 50)
    
    return {
        "success": True,
        "message": "SMS sent to console (development mode)",
        "provider": "console",
        "console_mode": True
    }

# ============================================================================
# Notification Templates
# ============================================================================

def send_practice_reminder_email(
    to_email: str,
    username: str,
    streak_days: int,
    practice_url: str
) -> Dict[str, Any]:
    """
    Send daily practice reminder email.
    """
    subject = f"🎯 Daily Practice Reminder - {streak_days} day streak!"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                <h1>🎯 Aptiverse Practice Reminder</h1>
                <p>Keep your learning streak alive!</p>
            </div>
            <div style="padding: 20px; background-color: #f8f9fa;">
                <h2>Hi {username},</h2>
                <p>You're on a <strong>{streak_days}-day streak</strong>! 🎉</p>
                <p>Don't break your momentum - complete today's practice set:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{practice_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Start Practice Session
                    </a>
                </div>
                <p>Just 10-15 minutes a day keeps your skills sharp!</p>
            </div>
            <div style="background: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                <p>Keep up the great work! 🚀</p>
                <p>The Aptiverse Team</p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    Hi {username},
    
    You're on a {streak_days}-day streak! 🎉
    
    Don't break your momentum - complete today's practice set:
    {practice_url}
    
    Just 10-15 minutes a day keeps your skills sharp!
    
    Keep up the great work! 🚀
    The Aptiverse Team
    """
    
    return send_email_sendgrid(to_email, subject, html_content, text_content=text_content)

def send_practice_reminder_sms(
    to_phone: str,
    username: str,
    streak_days: int
) -> Dict[str, Any]:
    """
    Send daily practice reminder SMS.
    """
    body = f"🎯 Hi {username}! You're on a {streak_days}-day streak! Complete today's Aptiverse practice to keep it going. 🚀"
    
    return send_sms_twilio(to_phone, body)

def send_badge_earned_email(
    to_email: str,
    username: str,
    badge_name: str,
    badge_description: str,
    profile_url: str
) -> Dict[str, Any]:
    """
    Send badge earned notification email.
    """
    subject = f"🏆 New Badge Unlocked: {badge_name}!"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center;">
                <h1>🏆 Badge Unlocked!</h1>
                <p>Congratulations on your achievement!</p>
            </div>
            <div style="padding: 20px; background-color: #f8f9fa;">
                <h2>Congratulations, {username}!</h2>
                <p>You've earned the <strong>{badge_name}</strong> badge!</p>
                <p><em>{badge_description}</em></p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{profile_url}" style="background: #f5576c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        View Your Profile
                    </a>
                </div>
                <p>Keep up the excellent work! 🌟</p>
            </div>
            <div style="background: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                <p>More achievements await!</p>
                <p>The Aptiverse Team</p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    Congratulations, {username}!
    
    You've earned the {badge_name} badge!
    
    {badge_description}
    
    View your profile: {profile_url}
    
    Keep up the excellent work! 🌟
    The Aptiverse Team
    """
    
    return send_email_sendgrid(to_email, subject, html_content, text_content=text_content)

# ============================================================================
# Configuration and Health Check
# ============================================================================

def get_notification_config() -> Dict[str, Any]:
    """
    Get current notification configuration status.
    """
    return {
        "email": {
            "provider": "sendgrid" if not CONSOLE_MODE else "console",
            "configured": not CONSOLE_MODE,
            "api_key_configured": bool(SENDGRID_API_KEY),
            "from_email": SENDGRID_FROM_EMAIL
        },
        "sms": {
            "provider": "twilio" if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]) else "console",
            "configured": all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]),
            "account_sid_configured": bool(TWILIO_ACCOUNT_SID),
            "from_number": TWILIO_FROM_NUMBER
        }
    }

def test_notification_services() -> Dict[str, Any]:
    """
    Test both email and SMS notification services.
    """
    results = {}
    
    # Test email
    email_result = send_email_sendgrid(
        to_email="test@example.com",
        subject="🧪 Aptiverse Notification Test",
        html_content="<h1>Test Email</h1><p>This is a test of the notification system.</p>",
        text_content="Test Email - This is a test of the notification system."
    )
    results["email"] = email_result
    
    # Test SMS
    sms_result = send_sms_twilio(
        to_phone="+1234567890",
        body="🧪 Aptiverse test SMS - Notification system test"
    )
    results["sms"] = sms_result
    
    return results

if __name__ == "__main__":
    # Test notification configuration
    config = get_notification_config()
    print("🔧 Notification Configuration:")
    print(f"📧 Email: {config['email']['provider']} (configured: {config['email']['configured']})")
    print(f"📱 SMS: {config['sms']['provider']} (configured: {config['sms']['configured']})")
    
    # Test notification services
    print("\n🧪 Testing Notification Services:")
    test_results = test_notification_services()
    print(f"📧 Email test: {'✅ Success' if test_results['email']['success'] else '❌ Failed'}")
    print(f"📱 SMS test: {'✅ Success' if test_results['sms']['success'] else '❌ Failed'}")
