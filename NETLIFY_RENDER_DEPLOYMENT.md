# 🚀 Netlify + Render Deployment Guide

Deploy your Aptiverse app using:
- **Netlify** for Frontend (React)
- **Render** for Backend (FastAPI) + Database (PostgreSQL)

---

## ⚠️ Important: Why This Setup?

**Netlify** only supports static sites and frontend apps. It **cannot** run Python backends.

So we split deployment:
- **Frontend** → Netlify (fast, free, global CDN)
- **Backend + Database** → Render (supports Python, PostgreSQL)

---

## 📋 Prerequisites

- GitHub account with your code pushed
- Netlify account (sign up at netlify.com)
- Render account (sign up at render.com)

---

## Part 1: Deploy Backend + Database to Render

### Step 1: Create Render PostgreSQL Database (5 min)

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "PostgreSQL"
4. Configure:
   - **Name**: `aptiverse-db`
   - **Region**: Choose closest (e.g., Oregon, Frankfurt, Singapore)
   - **Plan**: Free
5. Click "Create Database"
6. **Copy the Internal Database URL** (save it!)

### Step 2: Deploy Backend to Render (10 min)

1. Click "New +" → "Web Service"
2. Connect your repository: `ms3108/AptiverseV1`
3. Configure:
   - **Name**: `aptiverse-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: Free

4. Add Environment Variables:
   ```
   DATABASE_URL = [paste Internal Database URL from Step 1]
   SECRET_KEY = [generate with: python generate_secret_key.py]
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   FRONTEND_URL = https://your-app.netlify.app
   ```

5. Click "Create Web Service"
6. Wait 5-10 minutes for deployment
7. **Copy your backend URL**: `https://aptiverse-backend.onrender.com`

### Step 3: Seed Database

1. In Render dashboard → Your backend service
2. Click "Shell" tab
3. Run:
   ```bash
   cd backend
   python seed_data.py
   python create_admin.py
   ```

---

## Part 2: Deploy Frontend to Netlify

### Step 1: Configure Netlify (Already Done!)

Your project now has `netlify.toml` configuration file.

### Step 2: Deploy to Netlify

1. Go to https://netlify.com
2. Sign up with GitHub
3. Click "Add new site" → "Import an existing project"
4. Choose "Deploy with GitHub"
5. Select your repository: `ms3108/AptiverseV1`
6. Netlify will auto-detect settings from `netlify.toml`
7. Add Environment Variable:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://aptiverse-backend.onrender.com` (your backend URL from Part 1)
8. Click "Deploy site"
9. Wait 2-3 minutes
10. **Copy your Netlify URL**: `https://your-app.netlify.app`

### Step 3: Update Backend CORS

1. Go back to Render dashboard
2. Open your backend service
3. Go to "Environment" tab
4. Update `FRONTEND_URL` to your Netlify URL
5. Save (will auto-redeploy)

---

## ✅ Testing

### Test Backend
Visit: `https://aptiverse-backend.onrender.com`  
Should see: `{"message": "Welcome to Aptiverse API"}`

### Test Frontend
Visit: `https://your-app.netlify.app`  
Try:
- Register a user
- Login
- Take a quiz

---

## 🎉 You're Live!

**Frontend**: Netlify (global CDN, instant)  
**Backend**: Render (Python FastAPI)  
**Database**: Render (PostgreSQL)

---

## 💰 Costs

**Both are FREE!**

- Netlify: 100 GB bandwidth/month
- Render: 750 hours + 1 GB DB (free tier)

---

## 🚨 Common Issues

### Issue: CORS Error
**Fix**: Make sure `FRONTEND_URL` in Render matches your Netlify URL exactly (no trailing slash)

### Issue: Backend Cold Starts
**Normal**: Free tier sleeps after 15 min. First request takes 30-60s.

### Issue: Build Fails on Netlify
**Fix**: Make sure `netlify.toml` is in your project root and pushed to GitHub.

---

## 📞 Support

- Netlify Docs: https://docs.netlify.com
- Render Docs: https://render.com/docs

---

**Your app is now live on Netlify + Render!** 🚀
