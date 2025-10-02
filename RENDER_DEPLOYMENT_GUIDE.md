# Render Deployment Guide for Aptiverse V1

## ✅ Files Added for Render Deployment

The following files have been created and pushed to GitHub:

1. **`render.yaml`** - Main deployment configuration
2. **`build.sh`** - Build script for backend
3. **`start.sh`** - Start script for backend
4. **`runtime.txt`** - Python version specification

---

## 🚀 Step-by-Step Deployment on Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (connect your GitHub account)

### Step 2: Create PostgreSQL Database First
1. Click "New +" button → "PostgreSQL"
2. **Name**: `aptiverse-db`
3. **Database**: `aptiverse`
4. **User**: `aptiverse`
5. **Region**: Choose closest to you (e.g., Singapore)
6. **Plan**: Select "Free"
7. Click "Create Database"
8. ⚠️ **IMPORTANT**: Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3: Deploy Backend
1. Click "New +" → "Web Service"
2. Connect to your GitHub repository: `ms3108/AptiverseV1`
3. Configure:
   - **Name**: `aptiverse-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or use `.`)
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: Free

4. **Environment Variables** (Click "Advanced" → "Add Environment Variable"):
   ```
   DATABASE_URL = [Paste Internal Database URL from Step 2]
   SECRET_KEY = [Generate random string, e.g., your-secret-key-here-12345]
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   GMAIL_USER = your-email@gmail.com
   GMAIL_APP_PASSWORD = your-app-password
   WEAVIATE_URL = http://localhost:8080
   ```

5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
7. ⚠️ **IMPORTANT**: Copy the service URL (e.g., `https://aptiverse-backend.onrender.com`)

### Step 4: Seed the Database
Once backend is deployed:
1. Go to your backend service dashboard
2. Click "Shell" tab
3. Run these commands:
   ```bash
   cd backend
   python seed_data.py
   python create_admin.py
   ```

### Step 5: Deploy Frontend
1. Click "New +" → "Static Site"
2. Connect to same GitHub repository
3. Configure:
   - **Name**: `aptiverse-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`

4. **Environment Variables**:
   ```
   REACT_APP_API_URL = [Paste backend URL from Step 3]
   ```

5. Click "Create Static Site"
6. Wait for deployment (3-5 minutes)

### Step 6: Update Backend CORS
After frontend is deployed:
1. Go to backend service
2. Click "Environment" tab
3. Add new environment variable:
   ```
   FRONTEND_URL = [Your frontend URL, e.g., https://aptiverse-frontend.onrender.com]
   ```
4. Backend will auto-redeploy

---

## 🔧 Manual Deployment (Alternative Method)

If the automatic deployment doesn't work, use manual service creation:

### Backend Service
```yaml
Name: aptiverse-backend
Environment: Python 3
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend Service
```yaml
Name: aptiverse-frontend
Environment: Static Site
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/build
```

---

## ⚙️ Environment Variables Reference

### Backend Required Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | From Render PostgreSQL | Database connection string |
| `SECRET_KEY` | Random string | JWT secret key |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |
| `GMAIL_USER` | your-email@gmail.com | Email for notifications |
| `GMAIL_APP_PASSWORD` | app-password | Gmail app password |

### Frontend Required Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `REACT_APP_API_URL` | Backend URL | API endpoint URL |

---

## 🐛 Troubleshooting

### Issue: Build fails with "Script start.sh not found"
**Solution**: Files have been added and pushed. Make sure Render is pulling latest code:
- Go to service → Manual Deploy → "Clear build cache & deploy"

### Issue: Database connection fails
**Solution**: 
1. Verify `DATABASE_URL` in backend environment variables
2. Use **Internal Database URL** (not External)
3. Check database is in same region as backend

### Issue: CORS errors in frontend
**Solution**: Update backend `main.py` CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.onrender.com"],
    ...
)
```

### Issue: Cold start takes 30+ seconds
**Solution**: This is normal for Render free tier. Services spin down after 15 minutes of inactivity.

### Issue: Database expires after 90 days
**Solution**: 
1. Backup database before expiration:
   ```bash
   pg_dump -h hostname -U username -d database > backup.sql
   ```
2. Create new database
3. Restore: `psql -h new-hostname -U username -d database < backup.sql`

---

## 📊 What Render Will Deploy

### Services Created:
1. ✅ **Backend** (Python/FastAPI) - `aptiverse-backend.onrender.com`
2. ✅ **Frontend** (React Static) - `aptiverse-frontend.onrender.com`
3. ✅ **Database** (PostgreSQL) - Internal only

### Features Supported:
- ✅ REST APIs
- ✅ WebSocket (Battle Mode)
- ✅ PostgreSQL database
- ✅ Auto-deploy from GitHub
- ✅ HTTPS/SSL included
- ✅ Custom domains (paid plans)

### Features NOT Supported on Free Tier:
- ❌ Weaviate Vector DB (requires paid plan or external hosting)
- ❌ Always-on services (spin down after 15 min)
- ❌ Long-term database (90 day limit)

---

## 🔄 Updating Your Deployment

When you make code changes:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. **Auto-deploy**: Render will automatically detect changes and redeploy

3. **Manual deploy**: Go to service dashboard → "Manual Deploy" → "Deploy latest commit"

---

## 💰 Cost Breakdown (FREE!)

| Service | Free Tier Limits | Cost |
|---------|------------------|------|
| PostgreSQL | 1GB storage, 90 day expiration | $0 |
| Backend Web Service | 750 hours/month, cold starts | $0 |
| Frontend Static Site | 100GB bandwidth | $0 |
| **Total** | | **$0/month** |

---

## 🎯 Post-Deployment Checklist

After deployment is complete:

- [ ] Backend is running and accessible
- [ ] Frontend is running and accessible
- [ ] Database is connected
- [ ] Seed data is loaded (`seed_data.py`)
- [ ] Admin account is created (`create_admin.py`)
- [ ] Test login functionality
- [ ] Test question bank
- [ ] Test battle mode (WebSocket)
- [ ] Test email verification (if configured)
- [ ] Update GitHub repo with deployment URLs

---

## 🌐 Your Deployed URLs

Once deployed, your app will be accessible at:
- **Frontend**: `https://aptiverse-frontend.onrender.com`
- **Backend API**: `https://aptiverse-backend.onrender.com`
- **API Docs**: `https://aptiverse-backend.onrender.com/docs`

---

## 📝 Notes

1. **Weaviate Not Included**: The free tier doesn't support Docker services well. You can:
   - Use Weaviate Cloud (has free tier)
   - Remove duplicate detection feature
   - Upgrade to paid Render plan

2. **Cold Starts**: First request after 15 min inactivity takes ~30s. Acceptable for demos.

3. **Database Backup**: Set a reminder to backup your database every 80 days!

4. **Email Setup**: If you don't configure Gmail, email features will be disabled (app will still work).

---

## ✅ Current Status

- [x] Deployment files created
- [x] Files pushed to GitHub
- [ ] Services created on Render
- [ ] Database created
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Database seeded
- [ ] Admin created
- [ ] App tested

---

## 🆘 Need Help?

If deployment fails:
1. Check Render logs (click "Logs" tab)
2. Verify all environment variables are set
3. Ensure database is created first
4. Check GitHub repo has latest code
5. Try "Clear build cache & deploy"

---

**Ready to deploy!** Go to https://render.com and follow Step 1 above! 🚀
