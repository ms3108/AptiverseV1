# Aptiverse Reminder System Setup & Verification Guide

## 🎯 Current Status

Based on the verification test, here's what we found:

### ✅ **What's Working:**
- **Celery Setup**: ✅ Configured and ready
- **Reminder Logic**: ✅ All code implemented correctly
- **Database Integration**: ✅ User queries and notifications ready
- **Fallback Email**: ✅ Console output working (for testing)

### ❌ **What Needs Configuration:**
- **SendGrid API Key**: ❌ Not configured
- **Twilio Credentials**: ❌ Not configured  
- **Environment Variables**: ❌ Reminders disabled
- **Database Connection**: ❌ PostgreSQL not running locally

## 🔧 **Step-by-Step Setup Guide**

### **1. Configure Email Service (SendGrid)**

```bash
# Set SendGrid environment variables
export SENDGRID_API_KEY="your-sendgrid-api-key"
export SENDGRID_FROM_EMAIL="noreply@aptiverse.com"

# Or add to your .env file:
# SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
# SENDGRID_FROM_EMAIL=noreply@aptiverse.com
```

**Get SendGrid API Key:**
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Go to Settings → API Keys
3. Create API Key with "Mail Send" permissions
4. Verify sender email/domain

### **2. Configure SMS Service (Twilio)**

```bash
# Set Twilio environment variables
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
export TWILIO_FROM_NUMBER="+1234567890"

# Or add to .env:
# TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxx
# TWILIO_AUTH_TOKEN=your-auth-token
# TWILIO_FROM_NUMBER=+1234567890
```

**Get Twilio Credentials:**
1. Sign up at [twilio.com](https://twilio.com)
2. Get Account SID and Auth Token from Console
3. Purchase a phone number or use trial number

### **3. Enable Reminders**

```bash
# Enable reminder system
export ENABLE_PRACTICE_REMINDERS=true
export PRACTICE_REMINDER_HOUR=9
export PRACTICE_REMINDER_MINUTE=0

# Or add to .env:
# ENABLE_PRACTICE_REMINDERS=true
# PRACTICE_REMINDER_HOUR=9
# PRACTICE_REMINDER_MINUTE=0
```

### **4. Start Services with Docker**

```bash
# Start complete stack (includes Redis for Celery)
docker-compose up -d

# Verify services are running
docker-compose ps

# Start Celery worker and beat
docker-compose exec backend celery -A celery_app.celery_app worker --loglevel=info &
docker-compose exec backend celery -A celery_app.celery beat --loglevel=info &
```

## 🧪 **Testing the Reminder System**

### **Method 1: Manual Test (Recommended)**
```bash
# Run the comprehensive test
docker-compose exec backend python reminder_test.py

# This will:
# - Test email/SMS services
# - Find eligible users
# - Send manual test reminder
# - Trigger daily reminder task
```

### **Method 2: Individual Component Tests**

#### **Test Email Only:**
```bash
docker-compose exec backend python -c "
import notifications
result = notifications.send_email_sendgrid(
    to_email='test@example.com',
    subject='Test Email',
    html_content='<h1>Test</h1>',
    plain_text='Test'
)
print(f'Email sent: {result}')
"
```

#### **Test SMS Only:**
```bash
docker-compose exec backend python -c "
import notifications
result = notifications.send_sms_twilio(
    to_phone='+1234567890',
    body='Test SMS message'
)
print(f'SMS sent: {result}')
"
```

#### **Test Celery Task:**
```bash
docker-compose exec backend python -c "
from celery_tasks import send_daily_practice_reminders
result = send_daily_practice_reminders()
print(f'Reminder task result: {result}')
"
```

## 📋 **Verification Checklist**

### **Before Testing:**
- [ ] SendGrid API key configured
- [ ] Twilio credentials configured (optional)
- [ ] ENABLE_PRACTICE_REMINDERS=true
- [ ] Docker services running
- [ ] Celery worker and beat started

### **Testing Steps:**
- [ ] Run `python reminder_test.py`
- [ ] Check email arrives (check spam folder)
- [ ] Verify SMS received (if configured)
- [ ] Check in-app notifications in database
- [ ] Review Celery logs for task execution

### **Expected Results:**
- [ ] Email service returns `True`
- [ ] SMS service returns `True` (if configured)
- [ ] Eligible users count > 0
- [ ] Manual test shows "success"
- [ ] Daily task shows "success"

## 🔍 **How to Verify Reminders Are Working**

### **1. Check Email Delivery**
```bash
# Look for email in SendGrid dashboard
# Check your email inbox (including spam)
# Look for test email with subject "🧪 Aptiverse Manual Test Reminder"
```

### **2. Check SMS Delivery**
```bash
# Check Twilio console for message logs
# Verify SMS received on your phone
# Look for message starting with "🧪 Aptiverse test"
```

### **3. Check In-App Notifications**
```bash
# Query database directly:
docker-compose exec backend python -c "
from database import SessionLocal
import models
db = SessionLocal()
warnings = db.query(models.UserWarning).filter(
    models.UserWarning.reason.ilike('%test%')
).all()
print(f'Found {len(warnings)} test notifications')
for w in warnings:
    print(f'User {w.user_id}: {w.reason}')
"
```

### **4. Check Celery Logs**
```bash
# View Celery worker logs
docker-compose logs celery_worker

# Look for entries like:
# "Sent X daily practice reminders"
# "process_kafka_events" or "send_daily_practice_reminders"
```

### **5. Check Redis (for deduplication)**
```bash
# Check Redis reminder locks
docker-compose exec redis redis-cli keys "reminder:daily_practice:*"

# Should show keys like:
# "reminder:daily_practice:1:2026-05-01"
```

## 🚨 **Troubleshooting**

### **Email Not Sending:**
- Verify SendGrid API key is valid
- Check sender email is verified in SendGrid
- Look for "Console Mode" output (fallback working)

### **SMS Not Sending:**
- Verify Twilio credentials
- Check phone number format (+country_code)
- Ensure trial account has credits

### **No Eligible Users:**
- Check users exist in database
- Verify users haven't practiced today
- Check `last_activity_date` field

### **Celery Tasks Not Running:**
- Verify Redis is accessible
- Check Celery worker logs
- Ensure `ENABLE_PRACTICE_REMINDERS=true`

## 📊 **Production Monitoring**

### **Key Metrics to Monitor:**
1. **Email Delivery Rate**: SendGrid dashboard
2. **SMS Delivery Rate**: Twilio console  
3. **Task Success Rate**: Celery logs
4. **User Engagement**: Database activity logs
5. **Reminders Sent**: Redis key counts

### **Alerts to Set Up:**
- Email service failures
- SMS delivery failures
- Celery task errors
- High Redis memory usage

## ✅ **Success Confirmation**

Your reminder system is working when you see:

```
📧 Email Service: success
📱 SMS Service: success (if configured)
⚙️ Celery Setup: configured
👥 Eligible Users: >0
📋 Manual Test: success
⏰ Daily Task: success
```

And you receive:
- Test email in your inbox
- Test SMS on your phone (if configured)
- In-app notification in database
- "Sent X daily practice reminders" in Celery logs

**🎉 Once all these are working, your reminder system is production-ready!**
