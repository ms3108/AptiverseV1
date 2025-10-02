# Quick Render Deployment Fix

## The Problem
Render's render.yaml Blueprint feature is not working correctly on the free tier, causing "python: not found" errors.

## ✅ The Solution: Manual Service Creation

Instead of using render.yaml, create services manually with these **exact** settings:

---

## Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Settings:
   - **Name**: `aptiverse-db`
   - **Database**: `aptiverse`  
   - **User**: `aptiverse`
   - **Region**: Singapore (or closest to you)
   - **Plan**: **Free**
4. Click "Create Database"
5. **COPY the Internal Database URL** (you'll need this!)

---

## Step 2: Create Backend Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repo: `ms3108/AptiverseV1`
3. Configure with these **EXACT** values:

### Basic Settings:
- **Name**: `aptiverse-backend`
- **Region**: Same as database (e.g., Singapore)
- **Branch**: `main`
- **Root Directory**: *(leave blank)*
- **Environment**: **Python 3**
- **Build Command**: 
  ```
  cd backend && pip install -r requirements.txt
  ```
- **Start Command**:
  ```
  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- **Plan**: **Free**

### Environment Variables:
Click "Add Environment Variable" and add these:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | *Paste Internal Database URL from Step 1* |
| `SECRET_KEY` | `aptiverse-secret-key-change-in-production-12345` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `GMAIL_USER` | `your-email@gmail.com` *(optional)* |
| `GMAIL_APP_PASSWORD` | `your-app-password` *(optional)* |

4. Click "Create Web Service"
5. Wait 5-10 minutes for deployment
6. **COPY the service URL** (e.g., `https://aptiverse-backend.onrender.com`)

---

## Step 3: Seed the Database

Once backend is deployed and running:

1. Go to your backend service dashboard
2. Click "Shell" tab on the left
3. Run these commands one by one:
   ```bash
   cd backend
   python seed_data.py
   python create_admin.py
   ```

4. You should see:
   - ✅ Questions seeded
   - ✅ Badges created
   - ✅ Admin account created

---

## Step 4: Create Frontend Static Site

1. Click "New +" → "Static Site"
2. Connect to same GitHub repo
3. Configure:

### Basic Settings:
- **Name**: `aptiverse-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`
- **Build Command**:
  ```
  npm install && npm run build
  ```
- **Publish Directory**: `build`

### Environment Variables:
| Key | Value |
|-----|-------|
| `REACT_APP_API_URL` | *Paste backend URL from Step 2* |

4. Click "Create Static Site"
5. Wait 3-5 minutes for deployment

---

## Step 5: Update Backend CORS

After frontend deploys:

1. Copy your frontend URL (e.g., `https://aptiverse-frontend.onrender.com`)
2. Go to backend service → "Environment" tab
3. Add new environment variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: *Your frontend URL*
4. Backend will auto-redeploy

---

## 🎉 Done!

Your app should now be live at:
- **Frontend**: `https://aptiverse-frontend.onrender.com`
- **Backend API**: `https://aptiverse-backend.onrender.com`
- **API Docs**: `https://aptiverse-backend.onrender.com/docs`

---

## ⚠️ Important Notes

1. **Don't use render.yaml** - It's causing issues. Use manual creation instead.

2. **Cold Starts**: Free tier services sleep after 15 min of inactivity. First request takes ~30 seconds.

3. **Database Expires**: Free PostgreSQL expires after 90 days. Backup your data!

4. **Weaviate Not Included**: Vector database requires paid plan or external hosting. Duplicate detection won't work on free tier.

5. **Admin Credentials**:
   - Email: `misna5984@gmail.com`
   - Password: Generated during `create_admin.py` (check shell output)

---

## 🐛 Troubleshooting

### Backend won't start
- Check logs for errors
- Verify `DATABASE_URL` is set correctly
- Make sure you're using the **Internal** database URL, not External

### Frontend can't connect to backend
- Verify `REACT_APP_API_URL` in frontend environment
- Check backend CORS settings
- Make sure backend is deployed and running

### Database connection fails
- Use Internal URL, not External
- Ensure backend and database are in same region
- Check database status (should show "Available")

### Build fails
- Check build logs
- Try "Clear build cache & deploy"
- Verify requirements.txt exists in backend folder

---

## 🔄 Future Deployments

After initial setup, changes auto-deploy when you push to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render will automatically detect and deploy!

---

**Last Updated**: October 2, 2025
**Status**: Manual deployment method (render.yaml not used)
