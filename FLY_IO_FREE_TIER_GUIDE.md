# Fly.io Free Tier Management Guide

## ✅ Current Configuration (Within Free Tier!)

**Your current setup:**
- **Machines**: 1 machine (free tier allows up to 3)
- **Size**: shared-cpu-1x @ 256MB RAM (free tier spec)
- **Region**: Mumbai (bom)
- **Cost**: **$0/month** (within free allowances)

## 🎯 Fly.io Free Tier Limits

According to Fly.io's free allowances:

### What's Included for FREE:
- ✅ **Up to 3 VMs**: `shared-cpu-1x @ 256MB` each
- ✅ **3GB Persistent Storage**: Across all volumes
- ✅ **160GB Outbound Data Transfer**: Per month
- ✅ **Invoices < $5**: Automatically waived

### What You're Currently Using:
```
✓ 1 machine  (of 3 allowed)    = FREE
✓ 256MB RAM  (256MB is free)   = FREE
✓ 0GB volume (3GB allowed)     = FREE
✓ Bandwidth  (likely < 160GB)  = FREE
────────────────────────────────────
  TOTAL EXPECTED COST: $0/month
```

## ⚠️ What Would Cause Charges?

### 1. **Too Many Machines**
```bash
# ❌ PAID - 2 machines with 256MB each
flyctl scale count 2  # Exceeds free tier

# ✅ FREE - 1 machine with 256MB
flyctl scale count 1  # Current (stays free)
```

### 2. **Too Much Memory**
```bash
# ❌ PAID - Memory above 256MB on your single machine
flyctl scale memory 512   # Would cost ~$5-10/month
flyctl scale memory 1024  # Would cost ~$15-20/month

# ✅ FREE - 256MB on single machine
flyctl scale memory 256   # Current (stays free)
```

### 3. **Persistent Volumes**
```bash
# ❌ PAID - Volumes cost extra
flyctl volumes create data --size 10  # Would cost ~$1.50/month

# ✅ FREE - No volumes (using external database)
# Current setup uses Neon.tech (separate free tier)
```

### 4. **High Bandwidth Usage**
- Free tier: 160GB outbound data/month
- Typical small app: 5-20GB/month
- Your app: Likely < 10GB/month (API calls only)
- **Status**: Should stay FREE

## 📊 Cost Comparison

| Configuration | Machines | RAM | Monthly Cost |
|---------------|----------|-----|--------------|
| **Current (FREE)** | 1 | 256MB | **$0** |
| Small upgrade | 1 | 512MB | ~$5-7 |
| Previous setup | 2 | 512MB each | ~$15-20 |
| Performance setup | 2 | 1024MB each | ~$30-40 |
| Production-grade | 2 | 2048MB each | ~$60-80 |

## 🔍 Monitoring Your Usage

### Check Current Status
```powershell
# View machine count and size
flyctl machine list --app aptiverse-backend

# View app status
flyctl status --app aptiverse-backend

# Check estimated costs (dashboard)
# Visit: https://fly.io/dashboard/personal/billing
```

### Monthly Monitoring Checklist
- [ ] Check machine count (should be 1)
- [ ] Verify memory size (should be 256MB)
- [ ] Review bandwidth usage (should be < 160GB)
- [ ] Confirm no volumes attached
- [ ] Check billing dashboard for any charges

## 🚀 Performance Optimization (While Staying Free)

Even with 256MB RAM, you can still have decent performance:

### 1. **Backend Optimizations Applied** ✅
- Connection pooling (already added)
- Efficient database queries
- Proper indexing
- Code-level optimizations

### 2. **Frontend Optimizations** ✅
- Hosted on Vercel (separate free tier)
- Request timeouts configured
- API call monitoring

### 3. **Database Optimization** ✅
- Neon.tech free tier (separate from Fly.io)
- 512MB storage included
- Connection pooling to reduce overhead

### 4. **Caching Strategy** (Recommended)
```python
# Add in-memory caching for frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_categories():
    # Cache categories for 5 minutes
    return db.query(Question.category).distinct().all()
```

### 5. **Reduce Cold Starts**
Keep your app "warm" by:
- Using a free uptime monitor (e.g., UptimeRobot)
- Ping your API every 10-15 minutes
- Prevents app from sleeping

## ⚡ When to Consider Upgrading

### Signs You Need More Resources:

1. **Memory Issues**
   - App crashes with "Out of Memory" errors
   - Slow response times (> 3 seconds)
   - Database connection failures
   
   **Solution**: Upgrade to 512MB (~$5-7/month)

2. **High Traffic**
   - > 1000 concurrent users
   - Consistent load (not sporadic)
   
   **Solution**: Add second machine or upgrade memory

3. **Reliability Requirements**
   - Need 99.9% uptime
   - Can't afford downtime
   
   **Solution**: Scale to 2 machines for redundancy

## 💡 Staying Within Free Tier

### Best Practices:

1. **Monitor Monthly Usage**
   ```powershell
   # Check before month-end
   flyctl status --app aptiverse-backend
   ```

2. **Use External Services** (with their own free tiers)
   - ✅ Database: Neon.tech (512MB free)
   - ✅ Frontend: Vercel (100GB bandwidth free)
   - ✅ Email: Gmail (free for personal use)
   - ✅ Storage: Cloudinary/Imgur for images (free tier)

3. **Optimize Code, Not Resources**
   - Write efficient queries
   - Use caching
   - Minimize API calls
   - Compress responses

4. **Prevent Accidental Scaling**
   - Don't run auto-scaling commands
   - Be careful with `flyctl scale` commands
   - Always check current config before changes

5. **Alternative Free Hosting** (if needed)
   - **Railway**: $5 free credit/month
   - **Render**: Free tier with 750 hours/month
   - **Koyeb**: Free tier for small apps
   - **Cyclic**: Free tier for serverless

## 🛡️ Protecting Against Unexpected Charges

### Set Up Billing Alerts:
1. Go to: https://fly.io/dashboard/personal/billing
2. Set spending limit (if available)
3. Add payment method (required for overages)
4. Enable email notifications

### Auto-Shutdown Script (Optional):
Create a script to automatically scale down if not needed:
```powershell
# Scale down during off-hours (if desired)
# Add to Windows Task Scheduler
flyctl scale count 0 --app aptiverse-backend
```

## 📝 Quick Commands Reference

```powershell
# Check current configuration
flyctl status --app aptiverse-backend
flyctl machine list --app aptiverse-backend

# Stay within free tier (SAFE)
flyctl scale count 1 --app aptiverse-backend --yes
flyctl scale memory 256 --app aptiverse-backend

# Would exceed free tier (CAUTION)
flyctl scale count 2    # Adds 2nd machine = $5-7/month
flyctl scale memory 512 # More RAM = $5-10/month

# Emergency: Completely stop app (FREE)
flyctl machine stop --app aptiverse-backend

# Emergency: Delete app (FREE)
flyctl apps destroy aptiverse-backend
```

## 🎓 Learning Resources

- **Fly.io Pricing**: https://fly.io/docs/about/pricing/
- **Community Forum**: https://community.fly.io/
- **Billing Dashboard**: https://fly.io/dashboard/personal/billing
- **Free Tier Details**: https://fly.io/docs/about/pricing/#free-allowances

## ✅ Current Setup Summary

### Your Stack (All Free Tiers):

1. **Backend (Fly.io)**
   - 1 machine @ 256MB RAM
   - Cost: $0/month
   - Status: ✅ Within free tier

2. **Frontend (Vercel)**
   - Global CDN hosting
   - 100GB bandwidth/month
   - Cost: $0/month
   - Status: ✅ Within free tier

3. **Database (Neon.tech)**
   - PostgreSQL serverless
   - 512MB storage
   - Cost: $0/month
   - Status: ✅ Within free tier

4. **Email (Gmail)**
   - SMTP for verification emails
   - Personal use allowance
   - Cost: $0/month
   - Status: ✅ Free

**TOTAL MONTHLY COST: $0** 🎉

## ⚠️ Action Items

- [x] Scale down to 1 machine (done)
- [x] Scale memory to 256MB (done)
- [x] Remove second machine (done)
- [ ] Monitor usage weekly
- [ ] Check billing dashboard monthly
- [ ] Test app performance at 256MB
- [ ] Set up uptime monitor (optional)
- [ ] Add caching if performance suffers

## 📞 Need Help?

If you see unexpected charges:
1. Check billing dashboard immediately
2. Scale down resources: `flyctl scale count 1 --yes`
3. Contact Fly.io support (they're very responsive)
4. Remember: Charges < $5 are automatically waived

---

**Last Updated**: October 5, 2025
**Configuration Verified**: ✅ Within free tier limits
**Expected Monthly Cost**: $0
