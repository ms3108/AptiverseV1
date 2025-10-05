# 🚀 Vercel + Render Deployment Guide (Simplified)

## Deploy on Just 2 Platforms - No External Database Needed!

This guide shows you how to deploy your Aptiverse app using:
- **Vercel** for Frontend (React)
- **Render** for Backend (FastAPI) + PostgreSQL Database

**Why This Approach?**
- ✅ Only 2 platforms (simpler than Vercel + Neon + Render)
- ✅ Database included with Render (no need for Neon.tech)
- ✅ Still professional and production-ready
- ✅ 20-25 minute setup time

---

## 📊 Quick Overview

```
┌────────────────────────────────────────┐
│     VERCEL + RENDER ARCHITECTURE       │
├────────────────────────────────────────┤
│  Frontend (React)    →  Vercel.com     │
│  Backend (FastAPI)   →  Render.com     │
│  Database (PostgreSQL) → Render.com    │
└────────────────────────────────────────┘
```

**Advantages:**
- Simpler than 3-platform setup
- Render manages both backend AND database
- Free tier available on both platforms
- Professional deployment

---

## 🗄️ Step 1: Set Up Render PostgreSQL Database (5 minutes)

### 1.1 Create Render Account
1. Go to https://render.com
2. Click "Get Started"
3. **Sign up with GitHub** (recommended for easy deployment)
4. Authorize Render to access your GitHub account

### 1.2 Create PostgreSQL Database
1. Click "New +" button in dashboard
2. Select **"PostgreSQL"**
3. Configure database:
   - **Name**: `aptiverse-db`
   - **Database**: `aptiverse` (default is fine)
   - **User**: `aptiverse` (default is fine)
   - **Region**: Choose closest to you (e.g., Oregon US West, Frankfurt EU, Singapore)
   - **PostgreSQL Version**: 16 (latest)
   - **Plan**: **Free** (or paid for better performance)

4. Click **"Create Database"**

5. Wait 2-3 minutes for database to be created

### 1.3 Get Connection String
1. Once created, you'll see the database dashboard
2. Scroll down to **"Connections"** section
3. Copy the **"Internal Database URL"** (important!)
   - It looks like: `postgresql://aptiverse:xxxxx@dpg-xxxxx/aptiverse`
   - This is for connecting from your Render backend
4. **SAVE THIS URL** - you'll need it in Step 2

**Why Internal URL?**
- Internal connection is faster and free (no bandwidth charges)
- Use internal when backend and database are both on Render

---

## 🚀 Step 2: Deploy Backend to Render (10 minutes)

### 2.1 Create Backend Web Service
1. In Render dashboard, click "New +" → **"Web Service"**
2. Click **"Build and deploy from a Git repository"**
3. Click **"Connect account"** if you haven't connected GitHub yet
4. Find and select your repository: `ms3108/AptiverseV1`
5. Click **"Connect"**

### 2.2 Configure Web Service
Fill in these settings:

**Basic Configuration:**
- **Name**: `aptiverse-backend` (or your preferred name)
- **Region**: **Same as your database** (important for performance!)
- **Branch**: `main`
- **Root Directory**: Leave blank (or `.`)
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `./start.sh`

**Instance Type:**
- **Plan**: Free (or Starter for $7/month - always on)

### 2.3 Add Environment Variables
Click **"Advanced"** button, then scroll to **"Environment Variables"**

Add these variables one by one (click "+ Add Environment Variable"):

```
DATABASE_URL = [Paste the Internal Database URL from Step 1.3]
SECRET_KEY = [Generate a random 32+ character string]
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
FRONTEND_URL = https://your-app.vercel.app
```

**Optional Variables** (if using email features):
```
GMAIL_USER = your-email@gmail.com
GMAIL_APP_PASSWORD = your-16-char-app-password
```

**Optional Variables** (if using Weaviate):
```
WEAVIATE_URL = http://localhost:8080
```

**How to Generate SECRET_KEY:**
```bash
# On Windows PowerShell:
python -c "import secrets; print(secrets.token_hex(32))"

# Or use the included script:
python generate_secret_key.py
```

**Important Notes:**
- `DATABASE_URL`: Use the **Internal Database URL** from Step 1.3
- `SECRET_KEY`: Must be a long, random string (32+ characters)
- `FRONTEND_URL`: We'll update this after deploying to Vercel

### 2.4 Deploy Backend
1. Click **"Create Web Service"**
2. Render will now:
   - Clone your repository
   - Run `./build.sh` (installs dependencies)
   - Run `./start.sh` (starts FastAPI server)
3. **Wait 5-10 minutes** for first deployment

### 2.5 Get Backend URL
1. Once deployed, you'll see a green "Live" badge
2. Your backend URL will be shown at the top:
   - Example: `https://aptiverse-backend.onrender.com`
3. **SAVE THIS URL** - you'll need it for Vercel
4. Test it by visiting the URL - you should see:
   ```json
   {"message": "Welcome to Aptiverse API"}
   ```

### 2.6 Seed the Database
Now populate your database with sample data:

1. In your backend service dashboard, click the **"Shell"** tab (top right)
2. A terminal will open - run these commands:
   ```bash
   cd backend
   python seed_data.py
   python create_admin.py
   ```
3. Wait for completion - you should see success messages
4. Type `exit` to close the shell

**What This Does:**
- Creates sample questions for aptitude tests
- Creates an admin user (admin@aptiverse.com)
- Sets up initial data structure

---

## 🌐 Step 3: Deploy Frontend to Vercel (8 minutes)

### 3.1 Create Vercel Account
1. Go to https://vercel.com
2. Click **"Sign Up"**
3. **Sign up with GitHub** (recommended)
4. Authorize Vercel to access your repositories

### 3.2 Import Your Project
1. From Vercel dashboard, click **"Add New..."** → **"Project"**
2. You'll see a list of your GitHub repositories
3. Find `AptiverseV1` and click **"Import"**
4. Vercel will analyze your repository

### 3.3 Configure Project Settings
Vercel will auto-detect your React app, but you need to configure:

**Framework Preset:**
- Should auto-detect as **"Create React App"** ✅

**Root Directory:**
- Click **"Edit"** next to Root Directory
- Select or type: `frontend`
- Click **"Continue"**

**Build Settings** (should be auto-filled):
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 3.4 Add Environment Variables
Before deploying, add environment variables:

1. Expand **"Environment Variables"** section
2. Add this variable:

**Key:** `REACT_APP_API_URL`  
**Value:** `https://aptiverse-backend.onrender.com`  
(Replace with YOUR actual Render backend URL from Step 2.5)

3. Make sure it applies to **all environments** (Production, Preview, Development)

### 3.5 Deploy
1. Click **"Deploy"**
2. Vercel will now:
   - Install dependencies
   - Build your React app
   - Deploy to global CDN
3. **Wait 2-3 minutes** for deployment

### 3.6 Get Your Frontend URL
1. Once deployed, you'll see a success screen with confetti! 🎉
2. Your URL will be shown:
   - Example: `https://aptiverse-v1.vercel.app`
   - Or: `https://aptiverse-frontend-[random].vercel.app`
3. **SAVE THIS URL**
4. Click "Visit" to see your live app!

---

## 🔄 Step 4: Update Backend CORS (2 minutes)

Now that you have your Vercel URL, update the backend to allow requests:

### 4.1 Update FRONTEND_URL
1. Go back to **Render dashboard**
2. Click on your **`aptiverse-backend`** service
3. Click the **"Environment"** tab
4. Find the `FRONTEND_URL` variable
5. Click the **pencil icon** (edit)
6. Update the value to your **actual Vercel URL**:
   ```
   https://aptiverse-v1.vercel.app
   ```
   (Use your exact URL from Step 3.6)
7. Click **"Save Changes"**

### 4.2 Wait for Redeploy
- Render will automatically redeploy your backend (takes ~2 minutes)
- Watch for the "Live" badge to turn green again
- Your backend now accepts requests from your frontend!

---

## ✅ Step 5: Test Your Deployment

### 5.1 Test Backend
1. Visit your backend URL: `https://aptiverse-backend.onrender.com`
2. You should see:
   ```json
   {"message": "Welcome to Aptiverse API"}
   ```
3. Check API docs: `https://aptiverse-backend.onrender.com/docs`
4. You should see the interactive Swagger UI

### 5.2 Test Frontend
1. Visit your Vercel URL: `https://aptiverse-v1.vercel.app`
2. Try these actions:
   - **Register** a new user account
   - **Login** with your credentials
   - **View questions** (should load from backend)
   - **Take a quiz** (should submit to backend)

### 5.3 Check Database
1. Go to Render dashboard → Your database
2. Click **"SQL Editor"** (or use external tool)
3. Run query:
   ```sql
   SELECT * FROM users LIMIT 5;
   ```
4. You should see the users you created!

### 5.4 Common First-Time Issues

**❌ Frontend shows error connecting to backend**
- Check `REACT_APP_API_URL` in Vercel environment variables
- Make sure it matches your exact backend URL (no trailing slash)
- Redeploy frontend after changing env vars

**❌ CORS error in browser console**
- Check `FRONTEND_URL` in Render backend environment
- Make sure it matches your exact Vercel URL (no trailing slash)
- Wait for backend to redeploy

**❌ Database connection error**
- Make sure you used the **Internal Database URL** from Render
- Check that backend and database are in the same region
- Verify `DATABASE_URL` environment variable is set correctly

---

## 💰 Cost Breakdown (Free Tier)

### Render
**Database (Free Plan):**
- ✅ 1 GB storage
- ✅ 100 GB bandwidth/month
- ⚠️ Expires after 90 days (must upgrade or migrate)

**Web Service (Free Plan):**
- ✅ 750 hours/month (enough for one service 24/7)
- ✅ 512 MB RAM
- ✅ Shared CPU
- ⚠️ Sleeps after 15 minutes of inactivity
- ⚠️ Cold start: 30-60 seconds

### Vercel (Free Plan)
- ✅ 100 GB bandwidth/month
- ✅ Unlimited projects
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Instant deployments
- ✅ No sleep/cold starts

**Total Free Tier Cost:** $0/month 🎉

### Upgrade Options

**Render Starter ($7/month per service):**
- Always-on (no sleeping)
- 512 MB RAM
- Good for production

**Render Standard ($25/month per service):**
- 2 GB RAM
- Better performance
- Recommended for 1000+ users

**Vercel Pro ($20/month):**
- Unlimited bandwidth
- Better build performance
- Custom domains
- Priority support

---

## 🔧 Configuration Files You Already Have

Your repository includes these files for Render:

✅ **`build.sh`** - Installs Python dependencies
```bash
#!/bin/bash
cd backend
pip install -r requirements.txt
```

✅ **`start.sh`** - Starts your FastAPI server
```bash
#!/bin/bash
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT
```

✅ **`runtime.txt`** - Specifies Python version
```
python-3.11.4
```

✅ **`requirements.txt`** - Lists all Python dependencies

And for Vercel:

✅ **`vercel.json`** - Vercel configuration
✅ **`frontend/vercel.json`** - Frontend-specific config

**Everything is ready to use!**

---

## 🚨 Common Issues & Solutions

### Issue 1: Backend Cold Starts (Free Tier)
**Symptom:** First request after 15 min takes 30-60 seconds

**Solutions:**
- **Option A:** Upgrade to Render Starter ($7/month) for always-on
- **Option B:** Use UptimeRobot.com (free) to ping every 14 minutes
- **Option C:** Accept cold starts (fine for development/demos)

### Issue 2: CORS Errors
**Symptom:** Frontend shows "CORS policy" error in browser console

**Solutions:**
1. Verify `FRONTEND_URL` in Render matches Vercel URL **exactly**
2. No trailing slashes: `https://app.vercel.app` not `https://app.vercel.app/`
3. Check `backend/main.py` CORS configuration
4. Redeploy backend after changes

### Issue 3: Environment Variables Not Working
**Symptom:** App crashes or features don't work

**Solutions:**
1. After changing env vars, **redeploy** the service
2. Check variable names are **case-sensitive**
3. For Vercel: Variable must start with `REACT_APP_`
4. For Render: Use exact names from guide

### Issue 4: Build Failures
**Symptom:** Deployment fails during build

**Solutions:**
1. Check **logs** in Render/Vercel dashboard
2. Verify `build.sh` has execute permissions
3. Make sure `requirements.txt` lists all dependencies
4. Check Python version matches `runtime.txt`

### Issue 5: Database Connection Fails
**Symptom:** Backend can't connect to database

**Solutions:**
1. Use **Internal Database URL** (not External)
2. Backend and database must be in **same region**
3. Verify `DATABASE_URL` environment variable
4. Check Render dashboard - database must be "Available"

---

## 🔐 Security Checklist

Before sharing your app publicly:

- [ ] **Strong SECRET_KEY** - Random 32+ characters
- [ ] **No `.env` files** committed to GitHub
- [ ] **GMAIL_APP_PASSWORD** - Not your real password
- [ ] **CORS configured** - Only your frontend URL allowed
- [ ] **HTTPS enabled** - Automatic on both platforms ✅
- [ ] **2FA enabled** - On GitHub, Vercel, Render accounts
- [ ] **Environment variables** - Never in code, only in dashboards
- [ ] **Database backups** - Check Render backup settings

---

## 📈 Monitoring Your App

### Render Dashboard
**Backend Service:**
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, response times
- **Events**: Deployment history
- **Shell**: Terminal access for debugging

**Database:**
- **Metrics**: Query performance, connections
- **Backups**: Automatic (check schedule)
- **SQL Editor**: Run queries directly

### Vercel Dashboard
- **Deployments**: Build status, history
- **Analytics**: Page views, performance (optional paid feature)
- **Logs**: Build and function logs
- **Domains**: Manage custom domains

---

## 🎯 Quick Commands

### Update Your App
```bash
# Make changes to code
git add .
git commit -m "Your update message"
git push origin main

# ✨ Both Vercel and Render auto-deploy!
```

### Check Backend Logs
Go to Render → Service → "Logs" tab

### Run Database Queries
Go to Render → Database → "SQL Editor"

### Generate New SECRET_KEY
```bash
python generate_secret_key.py
```

### Seed Database Again (if needed)
Render Shell:
```bash
cd backend
python seed_data.py
```

---

## 🎉 You're Live!

Your Aptiverse app is now running on:

**Frontend:**
- URL: `https://your-app.vercel.app`
- Hosted: Vercel Global CDN
- Performance: ⚡ Excellent

**Backend:**
- URL: `https://your-backend.onrender.com`
- Hosted: Render Cloud
- Performance: ✅ Good

**Database:**
- Type: PostgreSQL
- Hosted: Render Cloud
- Connected: Via internal network

---

## 🚀 Next Steps

### Immediate
1. ✅ Test all features thoroughly
2. ✅ Share URL with friends/testers
3. ✅ Monitor logs for errors
4. ✅ Set up error alerts (optional)

### Soon
1. 🌐 Add custom domain to Vercel (optional)
2. 📊 Enable Vercel Analytics (optional)
3. ⏰ Set up UptimeRobot to prevent cold starts
4. 💾 Configure database backup schedule

### When You Have Users
1. 💳 Upgrade Render to Starter ($7/mo) for always-on
2. 📈 Monitor performance metrics
3. 🔒 Review security settings
4. 📧 Set up email notifications for errors

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Your Deployment Guides**: Check other .md files in repository

---

## 🔄 Alternative: Add Neon.tech for Better Database

If you want a better database than Render's free tier:

**Replace Render Database with Neon.tech:**
- Better free tier (longer than 90 days)
- Serverless PostgreSQL
- More storage (0.5 GB on free tier)

**See:** `VERCEL_NEON_RENDER_DEPLOYMENT.md` for 3-platform setup

---

**Congratulations! Your app is live! 🎉**

**Total Setup Time:** ~25 minutes  
**Platforms Used:** 2 (Vercel + Render)  
**Cost:** $0/month (free tier)

**Happy Deploying! 🚀**
