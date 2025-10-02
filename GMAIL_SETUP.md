# Gmail SMTP Setup Guide 📧

This guide will help you set up Gmail SMTP for sending verification emails.

## 🎯 Quick Setup (5 minutes)

### Step 1: Enable 2-Step Verification

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Scroll down to "How you sign in to Google"
3. Click on "2-Step Verification"
4. Follow the prompts to enable it (if not already enabled)

### Step 2: Generate App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - If you don't see this option, make sure 2-Step Verification is enabled
2. Select app: **Mail**
3. Select device: **Other (Custom name)** - type "Aptiverse"
4. Click **Generate**
5. Copy the **16-character password** (it looks like: `abcd efgh ijkl mnop`)

### Step 3: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy the example file
Copy-Item .env.example .env
```

Edit `.env` and add your Gmail credentials:

```env
GMAIL_USER=your-actual-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
SKIP_EMAIL_VERIFICATION=false
```

**Important:** Use the 16-character App Password (remove spaces), NOT your regular Gmail password!

### Step 4: Run the Application

```bash
docker-compose up --build
```

That's it! Your app will now send verification emails via Gmail.

---

## 📝 Configuration Options

### Option 1: Full Email Verification (Recommended for Production)

```env
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
SKIP_EMAIL_VERIFICATION=false
```

- Users receive verification emails
- Must click link to verify
- Most secure option

### Option 2: Development Mode (Console Only)

Don't set Gmail credentials, or use placeholders:

```env
GMAIL_USER=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
SKIP_EMAIL_VERIFICATION=false
```

- Verification links printed to console/logs
- No actual emails sent
- Good for testing

### Option 3: Skip Verification (Fastest for Development)

```env
SKIP_EMAIL_VERIFICATION=true
```

- Users auto-verified on signup
- Can login immediately
- No emails sent
- **NOT recommended for production!**

---

## 🔍 How to View Verification Links

If emails aren't sending (or you're in console mode), check the backend logs:

```bash
# View logs
docker-compose logs -f backend

# Look for output like:
# ================================================================================
# 📧 VERIFICATION EMAIL (Console Mode)
# ================================================================================
# To: user@example.com
# Subject: Verify Your Email - Aptiverse
#
# Verification Link:
# 👉 http://localhost:3000/verify?token=abc123...
# ================================================================================
```

Copy the link and paste it in your browser to verify the account.

---

## 🐛 Troubleshooting

### "Username and Password not accepted"

**Solution:** Make sure you're using an **App Password**, not your regular Gmail password.

1. Re-check that 2-Step Verification is enabled
2. Generate a new App Password
3. Use the 16-character password (remove spaces)

### "SMTP Authentication Error"

**Possible causes:**
- Using regular password instead of App Password
- Spaces in the App Password (remove them)
- Gmail account has security restrictions

**Solution:**
- Double-check your credentials in `.env`
- Try generating a new App Password
- Make sure your Gmail account allows "Less secure app access" is NOT needed (App Passwords work without this)

### Emails Going to Spam

**Solution:**
- Ask users to check spam folder
- Add your email to contacts
- Use a custom domain (not @gmail.com) in production
- Consider using a dedicated email service for production (SendGrid, AWS SES, etc.)

### No Email Received

**Check:**
1. Backend logs: `docker-compose logs backend`
2. Is the email address correct?
3. Check spam/junk folder
4. Verify Gmail credentials are correct

**Fallback:** Use console mode to get verification link from logs

---

## 🚀 Testing Email Sending

### Test 1: Register a User

1. Go to http://localhost:3000/signup
2. Fill in the form with your email
3. Click "Sign up"
4. Check:
   - Your email inbox
   - Backend logs: `docker-compose logs -f backend`

### Test 2: Verify Console Output

If configured in console mode, you should see:

```
✅ Email sent successfully to user@example.com via Gmail!
```

Or if not configured:

```
📧 VERIFICATION EMAIL (Console Mode)
👉 http://localhost:3000/verify?token=...
```

---

## 🔒 Security Best Practices

### For Development:
- ✅ Use App Passwords (never regular passwords)
- ✅ Keep `.env` in `.gitignore` (already configured)
- ✅ Don't commit credentials to Git

### For Production:
- 🔐 Use environment variables (not `.env` files)
- 🔐 Consider using a dedicated email service
- 🔐 Use a custom domain email
- 🔐 Implement rate limiting on registration
- 🔐 Add email verification expiration (currently 24h)
- 🔐 Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)

---

## 🎭 Alternative: Skip Email for Quick Testing

Want to test without setting up email? Just set:

```env
SKIP_EMAIL_VERIFICATION=true
```

Then:
1. Register → Users are auto-verified
2. Login → Works immediately
3. No email configuration needed!

**Remember:** Change this to `false` before deploying to production!

---

## 📞 Need Help?

- Check backend logs: `docker-compose logs -f backend`
- Verify your `.env` file exists and has correct values
- Make sure Docker containers are running: `docker-compose ps`
- Try generating a new Gmail App Password

---

## 🎉 Success!

Once configured, your users will receive beautiful HTML emails with verification links!

**Email Preview:**
```
┌─────────────────────────────────────────┐
│  Welcome to Aptiverse! 🎉               │
│                                         │
│  Thank you for registering...           │
│                                         │
│  ┌─────────────────┐                   │
│  │  Verify Email   │  (Blue Button)    │
│  └─────────────────┘                   │
│                                         │
│  Or copy and paste this link...         │
└─────────────────────────────────────────┘
```

Happy coding! 🚀
