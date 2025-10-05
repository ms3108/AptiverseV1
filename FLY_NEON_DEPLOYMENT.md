# Deployment Guide: Fly.io + Neon.tech

This guide will help you deploy your **Aptiverse application** using:
- **Fly.io** for Backend (FastAPI) + Frontend (React)
- **Neon.tech** for PostgreSQL Database (Free)

**Total Cost: $0/month** 🎉

---

## 📋 Prerequisites

1. **Fly.io Account**: https://fly.io
2. **Neon.tech Account**: https://neon.tech
3. **Fly CLI installed**:
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```
4. **Login to Fly.io**:
   ```powershell
   fly auth login
   ```

---

## 🗄️ STEP 1: Set Up Neon.tech Database (5 minutes)

### 1.1 Create Neon Account
1. Go to https://neon.tech
2. Click **"Sign up"**
3. Sign up with **GitHub** (easiest)
4. Verify your email

### 1.2 Create Database Project
1. Click **"Create a Project"**
2. **Project Name**: `aptiverse-db`
3. **Region**: Choose **Asia Pacific (Singapore)** - Closest to Mumbai
4. **Postgres Version**: 16 (default)
5. Click **"Create Project"**

### 1.3 Get Connection String
1. After creation, you'll see **"Connection Details"**
2. Copy the **Connection string** (looks like this):
   ```
   postgresql://username:password@ep-xxx-xxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
3. **SAVE THIS!** You'll need it in Step 3.

**Neon.tech Free Tier:**
- ✅ 0.5 GB storage
- ✅ 3 GB data transfer/month
- ✅ Unlimited projects
- ✅ Automatic backups
- ✅ No credit card required

---

## 🚀 STEP 2: Deploy Backend to Fly.io

### 2.1 Close the Web UI ❌

**IMPORTANT**: Close the Fly.io web deployment page. It has issues with Docker detection.

**We'll use the terminal instead** - it's more reliable and forces Docker usage.

### 2.2 Run Deployment Script

Open PowerShell and run:

```powershell
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"

# Run the automated deployment script
.\fly-deploy-backend.ps1
```

**The script will:**
1. ✅ Check Fly CLI is installed
2. ✅ Check authentication
3. ✅ Create app if needed
4. ✅ Ask for Neon.tech database URL
5. ✅ Generate SECRET_KEY automatically
6. ✅ Set all environment secrets
7. ✅ Deploy using Docker (bypasses buildpack issues)
8. ✅ Optionally seed the database

**Just follow the prompts!**

### 2.3 What the Script Does

The script fixes the `mise invalid gzip header` error by:
- ✅ Using `--dockerfile` flag explicitly
- ✅ Using `--strategy immediate` to force Docker build
- ✅ Bypassing Fly.io's automatic buildpack detection
- ✅ Setting all secrets before deployment

### 2.4 Seed the Database

Once backend is deployed:

```powershell
# SSH into your backend
fly ssh console --app aptiverse-backend

# Inside the SSH session, run:
cd backend
python seed_data.py
python create_admin.py
exit
```

---

## 🌐 STEP 3: Deploy Frontend to Fly.io

### 3.1 Update Frontend Configuration

First, create a production environment file for frontend:

**Create file: `frontend/.env.production`**
```env
REACT_APP_API_URL=https://aptiverse-backend.fly.dev
```

### 3.2 Deploy Frontend

Run the frontend deployment script:

```powershell
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"

# Run the automated frontend deployment script
.\fly-deploy-frontend.ps1
```

Wait 2-3 minutes. You'll get a URL like: `https://aptiverse-frontend.fly.dev`

The script will automatically update backend CORS settings too!

### 3.3 Update Backend CORS

Now update backend to accept requests from frontend:

```powershell
# Update FRONTEND_URL secret
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
```

This will automatically redeploy the backend (~2 minutes).

---

## ✅ STEP 4: Verify Deployment

### 4.1 Test Backend
```powershell
# Check if backend is running
curl https://aptiverse-backend.fly.dev

# Open API docs in browser
start https://aptiverse-backend.fly.dev/docs
```

You should see: `{"message": "Welcome to Aptiverse API"}`

### 4.2 Test Frontend
```powershell
# Open frontend
start https://aptiverse-frontend.fly.dev
```

Try:
- ✅ Register a new user
- ✅ Login
- ✅ Load questions
- ✅ Take a practice test

### 4.3 Test Database

1. Go to **Neon.tech dashboard**
2. Click your project: `aptiverse-db`
3. Click **"SQL Editor"**
4. Run query:
   ```sql
   SELECT * FROM users;
   ```
5. You should see registered users!

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                   Internet                      │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼─────┐      ┌────▼──────┐
    │ Frontend │      │  Backend  │
    │ (Fly.io) │◄─────┤ (Fly.io)  │
    │  React   │      │  FastAPI  │
    └──────────┘      └─────┬─────┘
                            │
                      ┌─────▼──────┐
                      │ PostgreSQL │
                      │ (Neon.tech)│
                      └────────────┘
```

---

## 🔧 Useful Commands

### Update Backend Code
```powershell
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"
git add backend/
git commit -m "Update backend"
git push origin main
fly deploy --config fly.backend.toml
```

### Update Frontend Code
```powershell
git add frontend/
git commit -m "Update frontend"
git push origin main
fly deploy --config fly.frontend.toml
```

### View Backend Logs
```powershell
fly logs --app aptiverse-backend
```

### View Frontend Logs
```powershell
fly logs --app aptiverse-frontend
```

### SSH into Backend
```powershell
fly ssh console --app aptiverse-backend
```

### Check App Status
```powershell
fly status --app aptiverse-backend
fly status --app aptiverse-frontend
```

### Scale Backend (if needed)
```powershell
# Increase memory
fly scale memory 1024 --app aptiverse-backend

# Keep always running (no auto-stop)
fly scale count 1 --app aptiverse-backend
```

---

## 💰 Cost Breakdown

### Free Tier (Everything is FREE!)

**Neon.tech (Database)**
- ✅ 0.5 GB storage
- ✅ 3 GB data transfer/month
- ✅ Auto-pause after 5 min inactivity
- **Cost: $0/month**

**Fly.io (Backend)**
- ✅ Up to 3 shared-cpu VMs
- ✅ 160 GB outbound data
- ✅ Auto-stop after 15 min inactivity
- **Cost: $0/month**

**Fly.io (Frontend)**
- ✅ Included in free tier
- ✅ Global CDN
- **Cost: $0/month**

**Total: $0/month** 🎉

### When to Upgrade

**1,000-10,000 users:**
- Upgrade Fly.io backend to always-on: ~$5-10/month
- Neon.tech still free ✅

**10,000+ users:**
- Fly.io backend: ~$15-25/month
- Neon.tech Scale plan: ~$19/month
- **Total: ~$35-45/month**

---

## 🚨 Troubleshooting

### Issue 1: Backend Cold Start (15-30 seconds)
**Problem**: First request is slow after inactivity  
**Solution**: 
- Free tier auto-stops after 15 min
- Upgrade to always-on: `fly scale count 1`

### Issue 2: Database Connection Error
**Problem**: `could not connect to server`  
**Solution**:
```powershell
# Check DATABASE_URL is correct
fly secrets list --app aptiverse-backend

# Update if needed
fly secrets set DATABASE_URL="your-correct-neon-url" --app aptiverse-backend
```

### Issue 3: CORS Errors
**Problem**: Frontend can't connect to backend  
**Solution**:
```powershell
# Verify FRONTEND_URL matches exactly
fly secrets list --app aptiverse-backend

# Update if needed
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
```

### Issue 4: Neon Database Pauses
**Problem**: First query slow after inactivity  
**Why**: Free tier auto-pauses after 5 minutes
**Solution**: First query wakes it up (~1-2 seconds), subsequent queries are fast

### Issue 5: Build Fails on Fly.io
**Problem**: Deployment fails  
**Solution**:
```powershell
# Check logs
fly logs --app aptiverse-backend

# Try local build first
docker build -f Dockerfile.backend -t test-backend .
```

---

## 🔐 Security Best Practices

1. ✅ **Secrets are encrypted** by Fly.io
2. ✅ **Never commit `.env`** to GitHub
3. ✅ **Use SSL** for database (Neon provides it automatically)
4. ✅ **Enable 2FA** on Fly.io and Neon.tech accounts
5. ✅ **Rotate secrets** every 3-6 months:
   ```powershell
   # Generate new secret
   $newSecret = python -c "import secrets; print(secrets.token_hex(32))"
   fly secrets set SECRET_KEY=$newSecret --app aptiverse-backend
   ```

---

## 📈 Monitoring

### Neon.tech Dashboard
- Monitor database queries
- Check storage usage
- View connection stats
- Run SQL queries directly

### Fly.io Dashboard
- View app metrics (CPU, memory)
- Monitor response times
- Check deployment history
- View real-time logs

---

## 🎯 Quick Reference

**Your URLs:**
- Frontend: `https://aptiverse-frontend.fly.dev`
- Backend: `https://aptiverse-backend.fly.dev`
- API Docs: `https://aptiverse-backend.fly.dev/docs`
- Database: Neon.tech dashboard

**Default Admin (after seeding):**
- Username: Check `create_admin.py` output
- Password: Check `create_admin.py` output

**Important Files:**
- `Dockerfile.backend` - Backend Docker image
- `Dockerfile.frontend` - Frontend Docker image
- `fly.backend.toml` - Backend Fly.io config
- `fly.frontend.toml` - Frontend Fly.io config
- `nginx.conf` - Frontend web server config

---

## 🎉 Summary

**What You Have Now:**
✅ Backend API running on Fly.io (Mumbai region)  
✅ Frontend app running on Fly.io (global CDN)  
✅ PostgreSQL database on Neon.tech (Singapore region)  
✅ All SSL/HTTPS enabled automatically  
✅ Total cost: **$0/month**  
✅ Can handle **1,000+ users** on free tier  

**Next Steps:**
1. Test your app thoroughly
2. Share the frontend URL with users
3. Set up custom domain (optional)
4. Monitor usage in dashboards
5. Scale when needed

---

## 📞 Support Resources

- **Fly.io Docs**: https://fly.io/docs
- **Neon.tech Docs**: https://neon.tech/docs
- **Fly.io Community**: https://community.fly.io
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Happy Deploying! 🚀**

**Your app is production-ready and costs $0!**
