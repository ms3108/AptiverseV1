# 🚀 Quick Redeploy Guide

## Current Status
- **Backend**: STOPPED (not using resources)
- **Frontend**: LIVE at https://aptiverse-v1-35au.vercel.app (serverless, no cost)
- **Database**: ACTIVE on Neon.tech (minimal usage, auto-suspends)

---

## 📍 When You Need to Restart

### ✅ **Option 1: Quick Start (1 command)**
```powershell
C:\Users\misna\.fly\bin\flyctl.exe machine start e7847205f5d168 --app aptiverse-backend
```
**Time:** ~10-15 seconds  
**Use when:** Just testing or showing the app quickly

---

### 🔄 **Option 2: Full Redeploy with Latest Code (if you made changes)**
```powershell
# Navigate to project
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"

# Deploy with optimizations
C:\Users\misna\.fly\bin\flyctl.exe deploy --app aptiverse-backend --dockerfile Dockerfile.backend --strategy immediate
```
**Time:** ~2-3 minutes  
**Use when:** You've updated backend code and want to deploy changes

---

### ⏹️ **To Stop Again After Use**
```powershell
C:\Users\misna\.fly\bin\flyctl.exe machine stop e7847205f5d168 --app aptiverse-backend
```

---

## 🔍 **Check Status Anytime**
```powershell
C:\Users\misna\.fly\bin\flyctl.exe machine list --app aptiverse-backend
```

---

## 📊 **Current Configuration**
- **Region**: Singapore (sin) - closest to database
- **Memory**: 256MB (free tier)
- **Optimizations Active**:
  - ✅ GZip compression (-300ms)
  - ✅ In-memory caching (-200ms)
  - ✅ Database indexes (-100ms)
  - ✅ Singapore region (-100ms)
  - ✅ Keep-warm GitHub Action (when running)

---

## 💡 **Tips**
1. **Frontend always works** - Users can visit the site, they just won't be able to log in or use features until backend starts
2. **Database doesn't cost when idle** - Neon.tech auto-suspends after 5 minutes of inactivity
3. **Free tier is safe** - Stopped machines don't count toward usage limits
4. **GitHub Actions keep-warm** - Will only ping when machine is running (it's smart enough to skip if stopped)

---

## 🎯 **Expected Performance When Restarted**
- First request after start: 2-3 seconds (cold start)
- After keep-warm kicks in: 150-500ms average
- With caching: 100-300ms on cached endpoints

---

## 📱 **URLs**
- Frontend: https://aptiverse-v1-35au.vercel.app
- Backend: https://aptiverse-backend.fly.dev (only works when machine is running)
- Backend Docs: https://aptiverse-backend.fly.dev/docs

---

## ⚠️ **Remember**
- Stopped machine = **0 hours** of compute usage
- Running machine = counts toward 2,160 free hours/month
- You have plenty of free hours even if you test frequently!
