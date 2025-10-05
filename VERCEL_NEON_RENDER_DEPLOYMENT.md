# Deployment Guide: Vercel + Neon.tech + Render

This guide will help you deploy your Aptiverse application using:
- **Vercel** for Frontend (React)
- **Neon.tech** for PostgreSQL Database
- **Render** for Backend (FastAPI)

---

## 🗄️ Step 1: Set Up Neon.tech PostgreSQL Database

### 1.1 Create Neon Account
1. Go to https://neon.tech
2. Sign up with GitHub or email
3. Click "Create a Project"

### 1.2 Configure Database
1. **Project Name**: `aptiverse-db`
2. **Region**: Choose closest to your users (e.g., US East, EU Central, Asia Pacific)
3. **Postgres Version**: 16 (latest)
4. Click "Create Project"

### 1.3 Get Connection String
1. After project creation, you'll see the connection details
2. Copy the **Connection String** (it looks like):
   ```
   postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
3. **IMPORTANT**: Save this connection string - you'll need it for Render

**Neon Features:**
- ✅ Free tier includes 0.5 GB storage
- ✅ Automatic backups
- ✅ Serverless architecture (scales to zero when not in use)
- ✅ SSL enabled by default

---

## 🚀 Step 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Connect your GitHub account and authorize Render

### 2.2 Deploy Backend Web Service
1. Click "New +" → "Web Service"
2. Connect to your repository: `ms3108/AptiverseV1`
3. Configure the service:

   **Basic Settings:**
   - **Name**: `aptiverse-backend`
   - **Region**: Choose same region as Neon (or closest)
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`

   **Instance Type:**
   - **Plan**: Free (or upgrade for better performance)

4. **Environment Variables** - Click "Advanced" → "Add Environment Variable":
   
   Add these variables one by one:
   ```
   DATABASE_URL = postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
   SECRET_KEY = generate-a-long-random-secret-key-here-use-at-least-32-characters
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   GMAIL_USER = your-email@gmail.com
   GMAIL_APP_PASSWORD = your-gmail-app-password-16-chars
   WEAVIATE_URL = http://localhost:8080
   FRONTEND_URL = https://your-app.vercel.app
   ```

   **Important Notes:**
   - `DATABASE_URL`: Use the Neon connection string from Step 1.3
   - `SECRET_KEY`: Generate with: `openssl rand -hex 32` or use a password generator
   - `GMAIL_APP_PASSWORD`: Get from Google Account → Security → 2-Step Verification → App passwords
   - `FRONTEND_URL`: Will update this after deploying frontend (use placeholder for now)

5. Click "Create Web Service"

6. Wait for deployment (5-10 minutes). Render will:
   - Clone your repository
   - Run `build.sh` to install dependencies
   - Run `start.sh` to start your FastAPI server

7. **Copy your backend URL**: 
   - After deployment, you'll see something like: `https://aptiverse-backend.onrender.com`
   - Save this URL - you'll need it for Vercel

### 2.3 Seed the Database
1. Go to your Render dashboard → `aptiverse-backend` service
2. Click the "Shell" tab (top right)
3. Run these commands to populate your database:
   ```bash
   cd backend
   python seed_data.py
   python create_admin.py
   ```
4. This will create sample questions and an admin user

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to https://vercel.com
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Authorize Vercel to access your repositories

### 3.2 Import Project
1. Click "Add New..." → "Project"
2. Import your repository: `ms3108/AptiverseV1`
3. Vercel will auto-detect it's a React app

### 3.3 Configure Project
1. **Framework Preset**: Create React App (auto-detected)
2. **Root Directory**: Click "Edit" and select `frontend`
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `build` (default)
5. **Install Command**: `npm install` (default)

### 3.4 Environment Variables
Click "Environment Variables" and add:

```
REACT_APP_API_URL = https://aptiverse-backend.onrender.com
```

Replace with your actual Render backend URL from Step 2.7

### 3.5 Deploy
1. Click "Deploy"
2. Wait 2-3 minutes for build to complete
3. Once deployed, you'll get a URL like: `https://aptiverse-frontend.vercel.app`
4. **Save this URL**

### 3.6 Set Up Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions

---

## 🔄 Step 4: Update Backend CORS Settings

Now that frontend is deployed, update backend to allow requests from Vercel:

1. Go to Render dashboard → `aptiverse-backend`
2. Click "Environment" tab
3. Find `FRONTEND_URL` variable
4. Update it to your Vercel URL: `https://aptiverse-frontend.vercel.app`
5. Click "Save Changes"
6. Render will automatically redeploy (takes ~2 minutes)

---

## ✅ Step 5: Verify Deployment

### 5.1 Test Backend
1. Visit: `https://aptiverse-backend.onrender.com`
2. You should see: `{"message": "Welcome to Aptiverse API"}`
3. Test API docs: `https://aptiverse-backend.onrender.com/docs`

### 5.2 Test Frontend
1. Visit your Vercel URL: `https://aptiverse-frontend.vercel.app`
2. Try registering a new user
3. Try logging in
4. Check if questions load properly

### 5.3 Test Database
1. Register a user on frontend
2. Go to Neon.tech dashboard
3. Click "SQL Editor"
4. Run: `SELECT * FROM users;`
5. You should see your newly registered user

---

## 📊 Service Comparison & Costs

### Free Tier Limits:

**Neon.tech (Database)**
- ✅ 0.5 GB storage
- ✅ 3 GB data transfer/month
- ✅ Unlimited projects
- ⚠️ Sleeps after 5 minutes of inactivity (wakes up automatically)

**Render (Backend)**
- ✅ 750 hours/month
- ✅ 512 MB RAM
- ✅ Shared CPU
- ⚠️ Sleeps after 15 minutes of inactivity
- ⚠️ Cold start: 30-60 seconds

**Vercel (Frontend)**
- ✅ 100 GB bandwidth/month
- ✅ Unlimited projects
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Instant deployments

---

## 🔧 Configuration Files Included

Your repository now includes:

1. **`vercel.json`** - Root level Vercel configuration
2. **`frontend/vercel.json`** - Frontend-specific Vercel config
3. **`build.sh`** - Render backend build script
4. **`start.sh`** - Render backend start script
5. **`.env.example`** - Template for environment variables

---

## 🚨 Common Issues & Solutions

### Issue 1: Backend Cold Starts (Render Free Tier)
**Problem**: First request after 15 minutes takes 30-60 seconds  
**Solution**: 
- Upgrade to paid plan ($7/month) for always-on
- Or use a uptime monitor like UptimeRobot to ping every 14 minutes

### Issue 2: Database Connection Errors
**Problem**: `could not connect to server`  
**Solution**: 
- Verify `DATABASE_URL` includes `?sslmode=require`
- Check Neon dashboard - database might be paused
- Verify IP allowlist in Neon (should allow all IPs)

### Issue 3: CORS Errors
**Problem**: Frontend can't connect to backend  
**Solution**: 
- Verify `FRONTEND_URL` in Render matches your Vercel URL exactly
- Check CORS middleware in `backend/main.py`
- Try without trailing slash

### Issue 4: Neon Database Pauses
**Problem**: Database becomes inactive  
**Solution**: 
- Free tier pauses after inactivity
- First query wakes it up (takes ~1-2 seconds)
- Upgrade to paid tier for always-active database

### Issue 5: Environment Variables Not Working
**Problem**: App can't read env vars  
**Solution**: 
- Render: Redeploy after changing env vars
- Vercel: Redeploy after changing env vars
- Check variable names match exactly (case-sensitive)

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** to GitHub
2. **Use strong SECRET_KEY**: Generate with `openssl rand -hex 32`
3. **Use GMAIL_APP_PASSWORD**: Don't use actual Gmail password
4. **Enable 2FA** on all platforms (Vercel, Render, Neon, GitHub)
5. **Rotate secrets** every 3-6 months
6. **Monitor logs** for suspicious activity

---

## 📈 Monitoring & Maintenance

### Neon.tech
- **Dashboard**: Monitor queries, storage, connections
- **SQL Editor**: Run queries directly
- **Backups**: Automatic, available in dashboard

### Render
- **Logs**: View real-time application logs
- **Metrics**: CPU, memory, response times
- **Shell**: SSH into container for debugging

### Vercel
- **Analytics**: Page views, performance metrics
- **Logs**: Function execution logs
- **Deployments**: Automatic on git push

---

## 🎯 Quick Command Reference

### Update Backend Code
```bash
git add .
git commit -m "Update backend"
git push origin main
# Render auto-deploys
```

### Update Frontend Code
```bash
git add .
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys
```

### Check Backend Logs (Render)
1. Go to Render dashboard
2. Click on service
3. Click "Logs" tab

### Run Database Migrations (Render Shell)
```bash
cd backend
python migrate_*.py
```

### Generate New SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🎉 You're Done!

Your app is now live with:
- ⚡ Fast frontend on Vercel's global CDN
- 🗄️ Scalable PostgreSQL on Neon.tech
- 🚀 Python FastAPI backend on Render

**Your URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.onrender.com`
- Database: Managed through Neon.tech dashboard

**Next Steps:**
1. Share your app URL with users
2. Set up custom domain (optional)
3. Monitor usage and scale as needed
4. Set up automatic backups
5. Consider upgrading to paid tiers for production

---

## 📞 Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Happy Deploying! 🚀**
