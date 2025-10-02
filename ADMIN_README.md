# 👑 Aptiverse Admin System

A comprehensive admin panel for managing users, questions, and community content with full audit logging.

---

## 🚀 Quick Start

### Login Credentials
```
URL: http://localhost:3000/login
Email: misna5984@gmail.com
Password: S5iKorE*lXevedod&&$l3Ib
```

After login, click the **👑 Admin** button in the navigation.

---

## 📋 Features

### 👥 User Management
- Search & filter users
- View detailed profiles with stats
- Ban users (temporary or permanent)
- Block banned emails from re-registration
- Reset passwords with auto-generated secure passwords
- Delete users with cascade deletion
- Complete ban audit trail

### 📝 Question Management
- Upload questions via JSON file
- AI-powered duplicate detection (95% similarity via Weaviate)
- Batch upload with detailed results
- View & filter all questions
- Edit/Delete questions
- Automatic categorization

### 📊 Analytics Dashboard
- User statistics (total, verified, banned)
- Question counts by topic/difficulty
- Pending moderation reports
- Recent admin actions timeline

### 🔒 Security & Audit
- Admin-only access control
- Complete action audit logs
- Immutable log entries
- Ban enforcement at login & registration
- Protected destructive actions
- JWT token authentication

---

## 📦 What's Included

### Backend (FastAPI)
- **15 Admin Endpoints** across 4 categories
- Admin authentication middleware
- Ban enforcement system
- Audit logging infrastructure
- Vector-based duplicate detection

### Frontend (React)
- **3 Admin Pages:**
  - Dashboard with statistics
  - User management interface
  - Question upload & management
- Responsive design
- Real-time updates
- Confirmation modals

### Database (PostgreSQL)
- **4 New Tables:**
  - `admin_action_logs` - Audit trail
  - `banned_emails` - Permanent ban list
  - `reported_posts` - Community reports
  - Modified `users` table with admin fields

---

## 📁 File Structure

```
backend/
├── admin_routes.py         ✨ NEW - All admin endpoints
├── create_admin.py         ✨ NEW - Migration & setup script
├── models.py               ✏️ UPDATED - Admin tables & fields
├── auth.py                 ✏️ UPDATED - Admin auth & ban checks
├── main.py                 ✏️ UPDATED - Admin routes included
└── schemas.py              ✏️ UPDATED - is_admin field

frontend/src/components/
├── AdminDashboard.js       ✨ NEW - Main admin page
├── AdminUsers.js           ✨ NEW - User management
├── AdminQuestions.js       ✨ NEW - Question management
├── Navigation.js           ✏️ UPDATED - Admin button
└── App.js                  ✏️ UPDATED - Admin routes

documentation/
├── ADMIN_SYSTEM_GUIDE.md   ✨ NEW - Complete API docs
├── ADMIN_SETUP_COMPLETE.md ✨ NEW - Implementation summary
└── ADMIN_QUICK_START.md    ✨ NEW - Getting started guide

test-data/
└── sample_questions.json   ✨ NEW - 5 sample questions
```

---

## 🔧 API Endpoints

### User Management
```http
GET    /admin/users                              # List all users
GET    /admin/users/{id}                         # User details
POST   /admin/users/{id}/ban                     # Ban user
POST   /admin/users/{id}/unban                   # Unban user
POST   /admin/users/{id}/remove-permanent-ban    # Remove permanent ban
POST   /admin/users/{id}/reset-password          # Reset password
DELETE /admin/users/{id}                         # Delete user
```

### Question Management
```http
GET    /admin/questions                          # List questions
POST   /admin/questions/upload                   # Upload JSON file
PUT    /admin/questions/{id}                     # Update question
DELETE /admin/questions/{id}                     # Delete question
```

### Reports & Audit
```http
GET    /admin/reports                            # List reports
POST   /admin/reports/{id}/resolve               # Resolve report
GET    /admin/logs                               # View audit logs
GET    /admin/stats                              # Dashboard stats
```

---

## 🧪 Testing Guide

### 1. Test User Ban
```bash
# Via UI
1. Login as admin
2. Navigate to Admin → Users
3. Select testuser (test@example.com)
4. Click "Ban" → Confirm
5. Logout
6. Try logging in as testuser → Should be blocked

# Verify in database
docker exec -it aptiverse_db psql -U postgres -d aptiverse -c \
  "SELECT username, is_banned, ban_reason FROM users WHERE email='test@example.com';"
```

### 2. Test Question Upload
```bash
# Via UI
1. Navigate to Admin → Questions
2. Select sample_questions.json
3. Click "Upload Questions"
4. Should see: "5 processed, 5 added, 0 duplicates"
5. Upload same file again
6. Should detect duplicates

# Verify in database
docker exec -it aptiverse_db psql -U postgres -d aptiverse -c \
  "SELECT COUNT(*) FROM questions;"
```

### 3. Test Duplicate Detection
```bash
# Create duplicate question
1. Take one question from sample_questions.json
2. Change wording slightly (keep meaning same)
3. Upload via admin panel
4. Should reject as duplicate (>95% similarity)
```

### 4. View Audit Logs
```bash
# Via UI
1. Admin Dashboard → "View All Action Logs"
2. Should see all test actions

# Via database
docker exec -it aptiverse_db psql -U postgres -d aptiverse -c \
  "SELECT action_type, created_at FROM admin_action_logs ORDER BY created_at DESC LIMIT 10;"
```

---

## 🔐 Security Features

### Access Control
- ✅ Admin-only routes (403 for non-admins)
- ✅ JWT token required for all endpoints
- ✅ Admin flag checked on every request
- ✅ Cannot ban/delete other admins

### Ban Enforcement
- ✅ Login blocked for banned users
- ✅ Registration blocked for banned emails
- ✅ Checked in auth middleware
- ✅ Frontend redirect for banned users

### Audit Trail
- ✅ All admin actions logged
- ✅ Includes: admin, action, target, details, timestamp
- ✅ Immutable logs (no delete API)
- ✅ Queryable by action type or admin

### Data Protection
- ✅ Password hashing (bcrypt)
- ✅ Cascade deletion prevents orphaned records
- ✅ Confirmation modals for destructive actions
- ✅ Input validation on all endpoints

---

## 📚 Documentation

### For Admins
- **ADMIN_QUICK_START.md** - Get started in 5 minutes
- **sample_questions.json** - Example upload format

### For Developers
- **ADMIN_SYSTEM_GUIDE.md** - Complete API reference, database schema, troubleshooting
- **ADMIN_SETUP_COMPLETE.md** - Implementation details, architecture, testing checklist

---

## 🎯 Use Cases

### Daily Admin Tasks
1. **Monitor new users** - Check registrations, verify legitimacy
2. **Handle reports** - Review flagged content, take action
3. **Upload questions** - Add new content weekly
4. **Ban spam accounts** - Remove bad actors
5. **Reset passwords** - Help users with access issues

### Moderation Workflows
1. **User misbehaving** → Soft ban → Warning → Permanent ban if needed
2. **Spam question upload** → Duplicate detection → Auto-reject
3. **Abusive post** → View reporter → Ban poster → Delete content
4. **Password forgotten** → Reset → Email new password

### Analytics Reviews
1. **Weekly stats** - User growth, question usage
2. **Monthly audit** - Review admin actions for accountability
3. **Quality check** - Review low-performing questions

---

## ⚠️ Important Notes

### Before Production
- [ ] Change admin password
- [ ] Set up email service for password resets
- [ ] Configure CORS for production domain
- [ ] Set up SSL/TLS certificates
- [ ] Review and adjust rate limits
- [ ] Set up monitoring & alerts

### Limitations
- **Email system not implemented** - Password resets return plaintext (admin must email user)
- **Discussion system framework only** - No posts to moderate yet
- **No bulk operations** - Actions are one-by-one
- **No role hierarchy** - All admins have full access

### Future Enhancements
- Email integration (SendGrid, AWS SES)
- User warning system (3 strikes)
- Bulk operations (select multiple users)
- Export data to CSV
- Question analytics dashboard
- Role-based permissions (super admin, moderator)
- IP ban capability
- Automated abuse detection

---

## 🐛 Troubleshooting

### Admin button not showing?
```bash
# Check if user is admin
docker exec -it aptiverse_backend python -c \
  "from database import SessionLocal; from models import User; \
   db = SessionLocal(); \
   u = db.query(User).filter(User.email=='misna5984@gmail.com').first(); \
   print(f'Is Admin: {u.is_admin}'); \
   db.close()"
```

### Cannot upload questions?
```bash
# Check Weaviate is running
docker ps | grep weaviate

# Check backend logs
docker logs aptiverse_backend --tail 50
```

### Ban not working?
```bash
# Check user ban status
docker exec -it aptiverse_db psql -U postgres -d aptiverse -c \
  "SELECT username, is_banned, is_permanently_banned, ban_reason FROM users WHERE email='user@example.com';"
```

---

## 📊 Database Schema

### Admin Tables
```sql
-- New columns in users table
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN is_permanently_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN ban_reason TEXT;
ALTER TABLE users ADD COLUMN banned_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN banned_by_admin_id INTEGER REFERENCES users(id);

-- Admin action logs
CREATE TABLE admin_action_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id),
    action_type VARCHAR NOT NULL,
    target_type VARCHAR,
    target_id INTEGER,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Banned emails (prevents re-registration)
CREATE TABLE banned_emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    reason TEXT,
    banned_by_admin_id INTEGER REFERENCES users(id),
    banned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reported posts (community moderation)
CREATE TABLE reported_posts (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    post_content TEXT NOT NULL,
    posted_by_user_id INTEGER REFERENCES users(id),
    reported_by_user_id INTEGER REFERENCES users(id),
    reason TEXT,
    status VARCHAR DEFAULT 'pending',
    resolved_by_admin_id INTEGER REFERENCES users(id),
    resolution_action VARCHAR,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🎓 Example Workflows

### Scenario 1: Spam User
```
1. Admin notices spam in community
2. Navigate to Admin → Users
3. Search for spammer's username
4. Click "Permanent Ban"
5. Add reason: "Posting spam content"
6. Confirm action
7. User immediately logged out
8. Email added to banned_emails table
9. Action logged in audit trail
10. User cannot re-register
```

### Scenario 2: Bulk Question Upload
```
1. Prepare JSON file with 100 questions
2. Navigate to Admin → Questions
3. Upload file
4. System checks each against Weaviate
5. Duplicates auto-rejected
6. New questions added to PostgreSQL + Weaviate
7. Results: "100 processed, 87 added, 13 duplicates"
8. Upload logged in audit trail
```

### Scenario 3: Password Reset Request
```
1. User emails: "I forgot my password"
2. Admin navigates to Admin → Users
3. Search for user by email
4. Click "Reset Password"
5. System generates: "Xy9#kL2mN@pQ"
6. Admin copies password
7. Admin emails user with new password
8. User logs in and changes password in Settings
9. Action logged in audit trail
```

---

## 🤝 Contributing

### Adding New Admin Features
1. Add endpoint in `admin_routes.py`
2. Add UI component in `frontend/src/components/`
3. Add route in `App.js`
4. Log action in `log_admin_action()`
5. Update documentation
6. Test thoroughly

### Code Standards
- All admin routes must use `get_current_admin()` dependency
- All destructive actions must have confirmation modals
- All actions must be logged
- All endpoints must validate input
- All responses must include clear error messages

---

## 📞 Support

For issues or questions:
1. Check **ADMIN_SYSTEM_GUIDE.md** for detailed documentation
2. Review backend logs: `docker logs aptiverse_backend`
3. Check database directly if needed
4. Test with sample_questions.json for uploads

---

## ✅ Status

**System Status:** OPERATIONAL ✅

- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ Database migrated & healthy
- ✅ Admin account created & verified
- ✅ All endpoints tested & working
- ✅ Audit logging active
- ✅ Ban enforcement enabled
- ✅ Duplicate detection operational

**Ready for:** Development, Testing, Staging  
**Production readiness:** 90% (needs email integration)

---

**Made with ❤️ for Aptiverse Admin Team**
