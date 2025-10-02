# Admin System Documentation

## Overview
The Aptiverse admin system provides comprehensive tools for managing users, questions, and community content with full audit logging.

## Admin Account

**Email:** misna5984@gmail.com  
**Password:** S5iKorE*lXevedod&&$l3Ib

**Admin Panel Access:** http://localhost:3000/admin

---

## Features

### 1. Admin Dashboard (`/admin`)
**Overview statistics and quick actions**

**Stats Displayed:**
- Total Users (with verified count)
- Banned Users
- Total Questions
- Pending Reports

**Quick Actions:**
- Navigate to User Management
- Navigate to Question Management
- Navigate to Reports

**Recent Activity Log:**
- Shows last 10 admin actions
- Action type, admin username, and timestamp

---

### 2. User Management (`/admin/users`)

#### View All Users
- **Endpoint:** `GET /admin/users?search=query&skip=0&limit=100`
- **Search:** Filter by username or email
- **Display:**
  - Username and email
  - Status badges (Admin, Verified, Banned, Permanent Ban)
  - User stats (Level, XP, Questions Solved, Streak)
  - Join date
  - Action buttons

#### User Actions

##### Ban User (Soft Ban)
- **Endpoint:** `POST /admin/users/{user_id}/ban`
- **Effect:** User cannot login, but can be unbanned
- **Data stored:** ban_reason, banned_at, banned_by_admin_id
- **Reversible:** Yes (via Unban)

##### Permanent Ban
- **Endpoint:** `POST /admin/users/{user_id}/ban` with `permanent=true`
- **Effect:** 
  - User cannot login
  - Email added to `banned_emails` table
  - User cannot re-register with same email
- **Reversible:** Yes (via Remove Permanent Ban)

##### Unban User
- **Endpoint:** `POST /admin/users/{user_id}/unban`
- **Effect:** Removes soft ban only
- **Note:** Cannot unban permanently banned users with this endpoint

##### Remove Permanent Ban
- **Endpoint:** `POST /admin/users/{user_id}/remove-permanent-ban`
- **Effect:**
  - Removes all ban flags
  - Removes email from banned_emails table
  - User can re-register

##### Reset Password
- **Endpoint:** `POST /admin/users/{user_id}/reset-password`
- **Effect:** Generates new random password
- **Returns:** New password for admin to email to user
- **Note:** Implement email sending in production

##### Delete User
- **Endpoint:** `DELETE /admin/users/{user_id}`
- **Effect:** Permanently deletes user and all related data (cascade)
- **Protected:** Cannot delete admin users
- **Irreversible:** Yes

#### View User Details
- **Endpoint:** `GET /admin/users/{user_id}`
- **Returns:**
  - Full user profile
  - Stats (attempts, battle participations, reported posts)
  - Recent 50 question attempts
  - Ban history

---

### 3. Question Management (`/admin/questions`)

#### Upload Questions
- **Endpoint:** `POST /admin/questions/upload`
- **Method:** File upload (JSON only)
- **Duplicate Detection:** Uses Weaviate vector similarity (95% threshold)

**JSON Format:**
```json
[
  {
    "question": "If a train runs at 60 km/h for 2 hours, how far does it travel?",
    "options": ["100 km", "120 km", "110 km", "130 km"],
    "answer": "120 km",
    "difficulty": "easy",
    "topic": "quants",
    "subtopic": "speed_distance_time",
    "solution": "Distance = Speed × Time = 60 × 2 = 120 km"
  }
]
```

**Upload Process:**
1. Validate JSON schema
2. Check each question against Vector DB for duplicates
3. If similarity > 95% → Reject as duplicate
4. If unique → Add to PostgreSQL + Weaviate
5. Return results summary

**Upload Result:**
```json
{
  "total": 10,
  "added": 8,
  "duplicates": 2,
  "errors": []
}
```

#### View All Questions
- **Endpoint:** `GET /admin/questions?topic=&difficulty=&skip=0&limit=50`
- **Filters:** Topic, Difficulty
- **Display:** ID, Title, Topic, Subtopic, Difficulty, Created Date

#### Update Question
- **Endpoint:** `PUT /admin/questions/{question_id}`
- **Body:** JSON with fields to update
- **Logged:** Yes

#### Delete Question
- **Endpoint:** `DELETE /admin/questions/{question_id}`
- **Effect:** Permanently removes question
- **Logged:** Yes

---

### 4. Community & Reports (`/admin/reports`)

#### View Reported Posts
- **Endpoint:** `GET /admin/reports?status=pending&skip=0&limit=50`
- **Filter by Status:** pending, reviewed, resolved
- **Display:**
  - Post content
  - Posted by (user details)
  - Reported by (user details)
  - Report reason
  - Status and resolution action
  - Timestamps

#### Resolve Report
- **Endpoint:** `POST /admin/reports/{report_id}/resolve`
- **Body:**
```json
{
  "action": "delete_post" | "warn_user" | "ban_user" | "no_action",
  "ban_permanent": false
}
```

**Actions:**
- **delete_post:** Remove the post (TODO: when discussion system is ready)
- **warn_user:** Send warning (TODO: implement warning system)
- **ban_user:** Ban the user who posted
- **no_action:** Mark as reviewed, no consequences

---

### 5. Admin Action Logs (`/admin/logs`)

**Endpoint:** `GET /admin/logs?action_type=&admin_id=&skip=0&limit=100`

**Logged Actions:**
- ban_user
- ban_user_permanent
- unban_user
- remove_permanent_ban
- reset_password
- delete_user
- upload_questions
- update_question
- delete_question
- resolve_report

**Log Entry:**
```json
{
  "id": 1,
  "admin": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  "action_type": "ban_user_permanent",
  "target_type": "user",
  "target_id": 123,
  "details": {
    "reason": "Spam",
    "permanent": true
  },
  "created_at": "2025-10-02T12:00:00Z"
}
```

---

## Database Schema

### New Tables

#### `admin_action_logs`
```sql
id                SERIAL PRIMARY KEY
admin_id          INTEGER REFERENCES users(id)
action_type       VARCHAR NOT NULL
target_type       VARCHAR
target_id         INTEGER
details           JSONB
created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### `banned_emails`
```sql
id                SERIAL PRIMARY KEY
email             VARCHAR UNIQUE NOT NULL
reason            TEXT
banned_by_admin_id INTEGER REFERENCES users(id)
banned_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### `reported_posts`
```sql
id                    SERIAL PRIMARY KEY
post_id               INTEGER NOT NULL
post_content          TEXT NOT NULL
posted_by_user_id     INTEGER REFERENCES users(id)
reported_by_user_id   INTEGER REFERENCES users(id)
reason                TEXT
status                VARCHAR DEFAULT 'pending'
resolved_by_admin_id  INTEGER REFERENCES users(id)
resolution_action     VARCHAR
resolved_at           TIMESTAMP WITH TIME ZONE
created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

### Modified Tables

#### `users` (new columns)
```sql
is_admin                 BOOLEAN DEFAULT FALSE
is_banned                BOOLEAN DEFAULT FALSE
is_permanently_banned    BOOLEAN DEFAULT FALSE
ban_reason               TEXT
banned_at                TIMESTAMP WITH TIME ZONE
banned_by_admin_id       INTEGER REFERENCES users(id)
```

---

## Security Features

### Authentication & Authorization
- **Admin Check:** `get_current_admin()` dependency in all admin routes
- **Ban Check:** Login blocked for banned users
- **Registration Block:** Banned emails cannot register

### Protected Actions
- Cannot ban/delete admin users
- Cannot unban permanently banned users without remove-permanent-ban
- Audit log for all admin actions

### Frontend Protection
- Admin navigation only shown to admin users
- ProtectedRoute wrapper on all admin pages
- Token-based authentication for all API calls

---

## Usage Examples

### 1. Ban a User for Spam
```javascript
// Frontend
await axios.post(`${API_URL}/admin/users/123/ban`, 
  { 
    reason: "Posting spam content",
    permanent: false 
  },
  { headers: { Authorization: `Bearer ${token}` } }
);
```

### 2. Upload Questions Bulk
```javascript
// Frontend
const formData = new FormData();
formData.append('file', jsonFile);

await axios.post(`${API_URL}/admin/questions/upload`, formData, {
  headers: {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'multipart/form-data'
  }
});
```

### 3. View User Details
```javascript
// Frontend
const response = await axios.get(`${API_URL}/admin/users/123`, {
  headers: { Authorization: `Bearer ${token}` }
});

// Response includes:
// - User profile
// - Stats (attempts, battles, reports)
// - Recent 50 attempts
```

---

## Future Enhancements

### Email Integration
- Send password reset emails
- Notify users of warnings
- Send ban notifications

### Discussion System
- Implement post deletion
- User warning system
- Comment moderation

### Advanced Analytics
- User behavior patterns
- Question difficulty analytics
- Popular topics dashboard
- Abuse pattern detection

### Batch Operations
- Bulk ban users
- Bulk delete questions
- Export user data

---

## Troubleshooting

### Admin Cannot Access Panel
1. Verify user has `is_admin=true` in database
2. Check token is valid and includes user info
3. Look for 403 Forbidden errors in console

### Questions Not Uploading
1. Verify JSON format matches schema
2. Check Weaviate is running (`docker ps`)
3. Look for duplicate detection rejections
4. Check backend logs: `docker logs aptiverse_backend`

### Ban Not Working
1. Check user is not an admin (admins cannot be banned)
2. Verify ban endpoint response
3. Check `is_banned` and `is_permanently_banned` in database
4. Test login attempt (should be blocked)

---

## API Reference Summary

### User Management
- `GET /admin/users` - List all users
- `GET /admin/users/{id}` - User details
- `POST /admin/users/{id}/ban` - Ban user
- `POST /admin/users/{id}/unban` - Unban user
- `POST /admin/users/{id}/remove-permanent-ban` - Remove permanent ban
- `POST /admin/users/{id}/reset-password` - Reset password
- `DELETE /admin/users/{id}` - Delete user

### Question Management
- `GET /admin/questions` - List questions
- `POST /admin/questions/upload` - Upload questions (file)
- `PUT /admin/questions/{id}` - Update question
- `DELETE /admin/questions/{id}` - Delete question

### Reports
- `GET /admin/reports` - List reports
- `POST /admin/reports/{id}/resolve` - Resolve report

### Audit
- `GET /admin/logs` - View action logs
- `GET /admin/stats` - Dashboard statistics

---

## Migration

To set up admin features on an existing instance:

```bash
# Run migration script
docker exec -it aptiverse_backend python create_admin.py

# This will:
# 1. Add admin columns to users table
# 2. Create admin_action_logs table
# 3. Create banned_emails table
# 4. Create reported_posts table
# 5. Create admin account
```

---

## Notes

- All timestamps are in UTC
- Passwords are bcrypt hashed
- JWT tokens expire after 30 minutes
- Vector similarity threshold: 95% for duplicates
- Cascade delete removes all user-related data
- Admin actions are immutable (cannot delete logs)
