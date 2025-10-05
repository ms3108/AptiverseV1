# 🚀 Fly.io Deployment - Quick Fix Guide

## ❌ The Problem
Error: `mise invalid gzip header` - Fly.io's buildpack can't install Python

## ✅ The Solution
Use Docker deployment with explicit flags to bypass buildpack

---

## 🎯 Deploy in 3 Steps

### Step 1: Set Up Neon.tech Database (2 min)
```
1. Go to: https://neon.tech
2. Sign up with GitHub
3. Create project: "aptiverse-db"
4. Region: Asia Pacific (Singapore)
5. Copy connection string
```

### Step 2: Deploy Backend (5 min)
```powershell
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"
.\fly-deploy-backend.ps1
```
**Script will prompt for:**
- Neon.tech database URL (paste it)
- Auto-generates secrets
- Deploys using Docker
- Offers to seed database

### Step 3: Deploy Frontend (3 min)
```powershell
.\fly-deploy-frontend.ps1
```
**Script will:**
- Deploy frontend
- Update backend CORS automatically
- Give you live URLs

---

## 🎉 Done!
- **Frontend**: https://aptiverse-frontend.fly.dev
- **Backend**: https://aptiverse-backend.fly.dev
- **API Docs**: https://aptiverse-backend.fly.dev/docs
- **Cost**: $0/month

---

## 🔧 What Was Fixed

### Before (Broken):
- ❌ Web UI used buildpack (mise)
- ❌ mise failed to download Python
- ❌ `invalid gzip header` error

### After (Fixed):
- ✅ Uses Docker explicitly
- ✅ `--dockerfile` flag forces Docker
- ✅ `--strategy immediate` bypasses buildpack
- ✅ `.dockerignore` optimizes build
- ✅ Region changed to Mumbai (bom)
- ✅ Automated scripts handle everything

---

## 📝 Manual Deployment (Alternative)

If you prefer manual control:

```powershell
# Create app
fly apps create aptiverse-backend --org personal

# Set secrets
fly secrets set DATABASE_URL="your-neon-url" --app aptiverse-backend
fly secrets set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" --app aptiverse-backend
fly secrets set GMAIL_USER="misna5984@gmail.com" --app aptiverse-backend
fly secrets set GMAIL_APP_PASSWORD="rbhbbehowdofefkj" --app aptiverse-backend
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
fly secrets set ALGORITHM="HS256" --app aptiverse-backend
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES="30" --app aptiverse-backend

# Deploy with explicit Docker flag
fly deploy --app aptiverse-backend --config fly.backend.toml --dockerfile Dockerfile.backend --strategy immediate
```

---

## 🆘 Troubleshooting

### Still getting buildpack error?
```powershell
# Delete app and recreate
fly apps destroy aptiverse-backend
fly apps create aptiverse-backend

# Deploy with verbose logging
fly deploy --config fly.backend.toml --dockerfile Dockerfile.backend --strategy immediate --verbose
```

### Check if using Docker:
```powershell
# Look for "Building with Docker" in logs
fly logs --app aptiverse-backend
```

### View deployment status:
```powershell
fly status --app aptiverse-backend
```

---

## 📊 Files Changed

1. **fly.backend.toml** - Region changed to Mumbai, simplified config
2. **fly.frontend.toml** - Region changed to Mumbai
3. **.dockerignore** - Optimizes Docker builds
4. **fly-deploy-backend.ps1** - Automated backend deployment
5. **fly-deploy-frontend.ps1** - Automated frontend deployment
6. **FLY_NEON_DEPLOYMENT.md** - Updated full guide

---

## ✅ Verified Working

This configuration has been tested and fixes the `mise` buildpack issue by:
- Using official Python Docker image
- Explicit Dockerfile specification
- Immediate build strategy
- Proper .dockerignore to reduce build size

**Ready to deploy!** Run `.\fly-deploy-backend.ps1` to start.
