# Deployment Guide: Fly.io (Full Stack)

This guide will help you deploy your **entire Aptiverse application** (Frontend + Backend + Database) on Fly.io.

---

## 🚨 Fix for "invalid gzip header" Error

**The error you encountered** happens because Fly.io's default Python buildpack (`mise`) has issues. Here's how to fix it:

### ✅ Solution: Use Docker Deployment Instead

Instead of using Fly.io's buildpack, we'll use a **Dockerfile** which is more reliable and gives you full control.

---

## 📋 Prerequisites

1. **Fly.io Account**: Sign up at https://fly.io
2. **Fly CLI installed**: 
   ```powershell
   # Install using PowerShell (Run as Administrator)
   iwr https://fly.io/install.ps1 -useb | iex
   ```
3. **Login to Fly.io**:
   ```powershell
   fly auth login
   ```

---

## 🐳 Step 1: Create Dockerfile for Backend

Create this file in your root directory:

**File: `Dockerfile.backend`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

WORKDIR /app/backend

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🐳 Step 2: Create Dockerfile for Frontend

**File: `Dockerfile.frontend`**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend code
COPY frontend/ ./
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 📝 Step 3: Create nginx.conf

**File: `nginx.conf`**
```nginx
server {
    listen 80;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 🗄️ Step 4: Create PostgreSQL Database on Fly.io

```powershell
# Create Postgres cluster
fly postgres create --name aptiverse-db --region ord --vm-size shared-cpu-1x --volume-size 1

# Save the connection details shown after creation
# You'll see something like:
# Username: postgres
# Password: <generated-password>
# Connection string: postgres://postgres:<password>@aptiverse-db.internal:5432
```

**Important**: Save the password! You'll need it later.

---

## 🚀 Step 5: Deploy Backend

```powershell
# Navigate to project root
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"

# Initialize Fly app for backend
fly launch --name aptiverse-backend --region ord --no-deploy

# This will create fly.toml
```

**Edit `fly.toml`** (created in root):
```toml
app = "aptiverse-backend"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile.backend"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512

[env]
  PORT = "8000"
  ALGORITHM = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES = "30"
```

**Set environment secrets** (sensitive data):
```powershell
# Set database URL
fly secrets set DATABASE_URL="postgresql://postgres:<password>@aptiverse-db.internal:5432/postgres"

# Generate and set secret key
$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
fly secrets set SECRET_KEY=$secretKey

# Set Gmail credentials
fly secrets set GMAIL_USER="your-email@gmail.com"
fly secrets set GMAIL_APP_PASSWORD="your-16-char-app-password"

# Set frontend URL (will update after frontend deployment)
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev"
```

**Deploy backend**:
```powershell
fly deploy
```

**Seed the database**:
```powershell
# SSH into backend machine
fly ssh console

# Run seed scripts
cd backend
python seed_data.py
python create_admin.py
exit
```

---

## 🌐 Step 6: Deploy Frontend

```powershell
# Create new Fly app for frontend
fly launch --name aptiverse-frontend --region ord --no-deploy

# Rename fly.toml to fly.backend.toml to keep it
mv fly.toml fly.backend.toml

# Create new fly.toml for frontend
```

**Create `fly.frontend.toml`**:
```toml
app = "aptiverse-frontend"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile.frontend"

[http_service]
  internal_port = 80
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[env]
  REACT_APP_API_URL = "https://aptiverse-backend.fly.dev"
```

**Update frontend to use backend URL**:

Before building, update `frontend/.env.production`:
```env
REACT_APP_API_URL=https://aptiverse-backend.fly.dev
```

**Deploy frontend**:
```powershell
fly deploy --config fly.frontend.toml
```

---

## 🔄 Step 7: Update Backend CORS

Now update backend to accept requests from frontend:

```powershell
# Update FRONTEND_URL secret
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
```

This will automatically redeploy the backend.

---

## ✅ Step 8: Verify Deployment

**Test Backend:**
```powershell
# Check backend health
curl https://aptiverse-backend.fly.dev

# Check API docs
start https://aptiverse-backend.fly.dev/docs
```

**Test Frontend:**
```powershell
# Open frontend in browser
start https://aptiverse-frontend.fly.dev
```

**Test Database:**
```powershell
# Connect to database
fly postgres connect --app aptiverse-db

# Run query
SELECT * FROM users;
\q
```

---

## 💰 Fly.io Free Tier Limits

**What you get FREE:**
- ✅ Up to 3 shared-cpu-1x 256MB VMs
- ✅ 3GB persistent volume storage
- ✅ 160GB outbound data transfer
- ✅ PostgreSQL database (1GB)

**Your usage:**
- Backend: 1 VM (512MB RAM)
- Frontend: 1 VM (256MB RAM)
- Database: 1 Postgres instance (1GB)
- **Total: Well within free tier!**

---

## 🔧 Deployment Commands Reference

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
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"
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

### Database Backup
```powershell
fly postgres backup create --app aptiverse-db
```

### Scale Resources
```powershell
# Scale backend memory
fly scale memory 1024 --app aptiverse-backend

# Scale to always-on (no auto-stop)
fly scale count 1 --app aptiverse-backend
```

---

## 🚨 Troubleshooting

### Issue 1: "invalid gzip header" (Your Original Error)
**Cause**: Fly.io's `mise` buildpack has corrupted downloads  
**Solution**: ✅ Use Dockerfile approach (this guide)

### Issue 2: Database Connection Refused
**Problem**: `could not connect to server`  
**Solution**:
```powershell
# Verify database is running
fly status --app aptiverse-db

# Check connection string
fly postgres connect --app aptiverse-db
```

### Issue 3: Backend Cold Start Slow
**Problem**: First request takes 10-20 seconds  
**Solution**:
```powershell
# Keep at least 1 machine always running
fly scale count 1 --app aptiverse-backend
```

### Issue 4: CORS Errors
**Problem**: Frontend can't reach backend  
**Solution**:
```powershell
# Verify FRONTEND_URL matches exactly
fly secrets list --app aptiverse-backend

# Update if needed
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
```

### Issue 5: Build Fails
**Problem**: Docker build fails  
**Solution**:
```powershell
# Build locally first to test
docker build -f Dockerfile.backend -t aptiverse-backend .

# Check Fly.io build logs
fly logs --app aptiverse-backend
```

---

## 🔐 Security Best Practices

1. **Never commit secrets** to git
2. **Use `fly secrets` command** for sensitive data
3. **Enable 2FA** on Fly.io account
4. **Rotate secrets regularly**:
   ```powershell
   fly secrets set SECRET_KEY="new-secret-key" --app aptiverse-backend
   ```
5. **Monitor logs** for suspicious activity:
   ```powershell
   fly logs --app aptiverse-backend
   ```

---

## 📊 Cost Comparison

### Free Tier (0-1,000 users)
- Backend + Frontend + Database: **$0/month**
- Auto-stop after inactivity (cold starts)

### Paid Tier (1,000+ users)
- Always-on backend: **~$5-10/month**
- Larger database: **~$10-15/month**
- **Total: ~$15-25/month**

---

## 🎯 Why Fly.io Failed Initially

**The error you saw:**
```
mise invalid gzip header
```

**Root cause:**
- Fly.io tried using buildpack auto-detection
- Detected Python project and used `mise` (Python version manager)
- `mise` tried downloading pre-compiled Python from GitHub
- Download got corrupted → gzip extraction failed

**Our solution:**
- ✅ Skip buildpacks entirely
- ✅ Use explicit Dockerfile
- ✅ Use official Python 3.11 image (stable & reliable)
- ✅ Full control over dependencies

---

## 🎉 Advantages of Fly.io

1. **Global edge network** - Your app runs close to users
2. **Free PostgreSQL** - No external database service needed
3. **Auto-scaling** - Scales to zero when not used
4. **Simple deployment** - One command: `fly deploy`
5. **SSH access** - Debug directly on production
6. **Free tier** - Generous enough for small apps

---

## 📞 Support Resources

- **Fly.io Docs**: https://fly.io/docs
- **Fly.io Community**: https://community.fly.io
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

## ✅ Summary

**What we did:**
1. ✅ Fixed "invalid gzip header" by using Dockerfile
2. ✅ Created separate Docker images for backend & frontend
3. ✅ Set up PostgreSQL database on Fly.io
4. ✅ Deployed full-stack app (Frontend + Backend + DB)
5. ✅ All within free tier limits

**Your URLs after deployment:**
- Frontend: `https://aptiverse-frontend.fly.dev`
- Backend: `https://aptiverse-backend.fly.dev`
- Database: `aptiverse-db.internal` (private network)

**Next steps:**
1. Follow the guide above step-by-step
2. Test your deployed app
3. Set up custom domain (optional)
4. Monitor usage and scale as needed

---

**Happy Deploying! 🚀**
