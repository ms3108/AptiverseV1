# Deployment Checklist

Use this checklist to ensure you complete all deployment steps correctly.

## Pre-Deployment Preparation

- [ ] Code is committed to GitHub
- [ ] All features tested locally
- [ ] Environment variable examples updated
- [ ] Sensitive data removed from code

## 1. Neon.tech Database Setup

- [ ] Created Neon account
- [ ] Created new project: `aptiverse-db`
- [ ] Selected appropriate region
- [ ] Copied connection string
- [ ] Saved connection string securely
- [ ] Verified connection string includes `?sslmode=require`

**Connection String Format:**
```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
```

## 2. Render Backend Deployment

### Initial Setup
- [ ] Created Render account
- [ ] Connected GitHub account
- [ ] Created new Web Service
- [ ] Connected to `ms3108/AptiverseV1` repository
- [ ] Selected `main` branch

### Configuration
- [ ] Set name: `aptiverse-backend`
- [ ] Set runtime: Python 3
- [ ] Set build command: `./build.sh`
- [ ] Set start command: `./start.sh`
- [ ] Selected appropriate region
- [ ] Chose free or paid plan

### Environment Variables
- [ ] Added `DATABASE_URL` (from Neon)
- [ ] Added `SECRET_KEY` (generated strong key)
- [ ] Added `ALGORITHM = HS256`
- [ ] Added `ACCESS_TOKEN_EXPIRE_MINUTES = 30`
- [ ] Added `GMAIL_USER` (if using email)
- [ ] Added `GMAIL_APP_PASSWORD` (if using email)
- [ ] Added `WEAVIATE_URL` (or commented out if not using)
- [ ] Added `FRONTEND_URL` (placeholder initially)

### Deployment
- [ ] Clicked "Create Web Service"
- [ ] Waited for initial deployment (5-10 minutes)
- [ ] Verified deployment succeeded (green status)
- [ ] Copied backend URL
- [ ] Tested backend: `https://your-backend.onrender.com`
- [ ] Verified API docs: `https://your-backend.onrender.com/docs`

### Database Seeding
- [ ] Opened Shell tab in Render
- [ ] Ran: `cd backend`
- [ ] Ran: `python seed_data.py`
- [ ] Ran: `python create_admin.py`
- [ ] Verified data was created (check logs)

## 3. Vercel Frontend Deployment

### Initial Setup
- [ ] Created Vercel account
- [ ] Connected GitHub account
- [ ] Clicked "New Project"
- [ ] Imported `ms3108/AptiverseV1` repository

### Configuration
- [ ] Set root directory: `frontend`
- [ ] Verified framework preset: Create React App
- [ ] Build command: `npm run build` (auto-filled)
- [ ] Output directory: `build` (auto-filled)

### Environment Variables
- [ ] Added `REACT_APP_API_URL` with Render backend URL

### Deployment
- [ ] Clicked "Deploy"
- [ ] Waited for deployment (2-3 minutes)
- [ ] Verified deployment succeeded
- [ ] Copied Vercel URL
- [ ] Tested frontend: `https://your-app.vercel.app`

## 4. Backend CORS Update

- [ ] Went back to Render dashboard
- [ ] Opened `aptiverse-backend` service
- [ ] Clicked "Environment" tab
- [ ] Updated `FRONTEND_URL` with Vercel URL
- [ ] Clicked "Save Changes"
- [ ] Waited for auto-redeploy (1-2 minutes)
- [ ] Verified redeploy succeeded

## 5. Testing & Verification

### Backend Tests
- [ ] Visit backend root: shows welcome message
- [ ] Visit API docs: `/docs` endpoint works
- [ ] Test health check endpoint (if exists)
- [ ] Check logs for errors

### Frontend Tests
- [ ] Homepage loads correctly
- [ ] Can register new user
- [ ] Can login with credentials
- [ ] Questions load properly
- [ ] Navigation works
- [ ] No console errors
- [ ] No CORS errors

### Database Tests
- [ ] Login to Neon dashboard
- [ ] Open SQL Editor
- [ ] Run: `SELECT COUNT(*) FROM users;`
- [ ] Run: `SELECT COUNT(*) FROM questions;`
- [ ] Verify data exists

### Integration Tests
- [ ] Register → Login → Take quiz → View results
- [ ] Try admin login (if applicable)
- [ ] Test all major features
- [ ] Test on mobile device/responsive
- [ ] Test in different browsers

## 6. Post-Deployment Setup

### Monitoring
- [ ] Set up Render email notifications
- [ ] Set up Vercel deployment notifications
- [ ] Bookmark Neon dashboard
- [ ] Bookmark Render dashboard
- [ ] Bookmark Vercel dashboard

### Documentation
- [ ] Updated README with live URLs
- [ ] Documented admin credentials (securely)
- [ ] Saved all environment variables (securely)
- [ ] Created backup of configuration

### Optional Enhancements
- [ ] Set up custom domain on Vercel
- [ ] Configure DNS for custom domain
- [ ] Enable Vercel Analytics
- [ ] Set up uptime monitoring (UptimeRobot)
- [ ] Configure error tracking (Sentry)
- [ ] Set up backup strategy

## 7. Security Checklist

- [ ] No `.env` files in GitHub
- [ ] Strong `SECRET_KEY` generated
- [ ] Using `GMAIL_APP_PASSWORD` (not real password)
- [ ] Database uses SSL (`sslmode=require`)
- [ ] CORS only allows specific origins
- [ ] All secrets stored in platform dashboards
- [ ] 2FA enabled on all accounts
- [ ] Documented security procedures

## 8. Performance Optimization

### Free Tier Considerations
- [ ] Aware of Render cold start (30-60 sec)
- [ ] Aware of Neon database pause
- [ ] Set up uptime monitor (optional)
- [ ] Considered paid tier benefits

### Production Considerations
- [ ] Optimize frontend bundle size
- [ ] Enable compression
- [ ] Configure caching headers
- [ ] Optimize database queries
- [ ] Add error logging

## Troubleshooting Completed

If you encountered issues, mark what you fixed:
- [ ] Fixed CORS errors
- [ ] Fixed database connection
- [ ] Fixed environment variables
- [ ] Fixed build errors
- [ ] Fixed startup errors
- [ ] Other: ___________________

## Final Verification

- [ ] ✅ Backend is live and accessible
- [ ] ✅ Frontend is live and accessible
- [ ] ✅ Database is connected and seeded
- [ ] ✅ All environment variables configured
- [ ] ✅ CORS is working correctly
- [ ] ✅ Users can register and login
- [ ] ✅ All major features work
- [ ] ✅ No critical errors in logs
- [ ] ✅ Documentation updated
- [ ] ✅ Deployment process documented

## Live URLs

Record your live URLs here:

**Frontend (Vercel):**
```
https://your-app.vercel.app
```

**Backend (Render):**
```
https://your-backend.onrender.com
```

**Database (Neon):**
```
Dashboard: https://console.neon.tech/app/projects
Project: aptiverse-db
```

**Admin Credentials:**
```
Email: admin@aptiverse.com
Password: [stored securely]
```

## Next Steps

- [ ] Share app with beta testers
- [ ] Set up analytics
- [ ] Plan feature roadmap
- [ ] Monitor usage and performance
- [ ] Schedule regular backups
- [ ] Review and optimize costs

---

**Deployment Date:** _______________

**Deployed By:** _______________

**Status:** 🎉 LIVE IN PRODUCTION

---

## Support Resources

- Vercel Docs: https://vercel.com/docs
- Neon Docs: https://neon.tech/docs
- Render Docs: https://render.com/docs
- Project Docs: See `VERCEL_NEON_RENDER_DEPLOYMENT.md`
