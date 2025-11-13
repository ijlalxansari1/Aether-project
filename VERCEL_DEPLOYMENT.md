# Vercel Full-Stack Deployment Guide

This guide provides step-by-step instructions to deploy the **Aether Insight Platform** (both frontend and backend) to Vercel as a full-stack application.

---

## Prerequisites

1. **Vercel Account**: Create one at https://vercel.com (free tier available)
2. **GitHub Repository**: Push your code to GitHub (https://github.com/ijlalxansari1/Aether-project)
3. **Database**: PostgreSQL instance (Vercel Postgres or external provider)
4. **Git CLI**: Installed on your machine

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Vercel Deployment               │
├─────────────────────────────────────────┤
│  Frontend (React + Vite)                │
│  - Static build at: /                   │
│  - Built from: frontend/                │
├─────────────────────────────────────────┤
│  Backend (FastAPI + Mangum)             │
│  - Serverless function at: /api         │
│  - Handler: api/index.py                │
│  - Source: backend/app/main.py          │
└─────────────────────────────────────────┘
```

---

## Step 1: Prepare Your Repository

Ensure your GitHub repository is up-to-date with all changes:

```bash
git add .
git commit -m "feat: prepare for Vercel deployment"
git push origin main
```

Verify these files exist in your repo:
- ✅ `vercel-python.json` (updated configuration)
- ✅ `api/index.py` (Mangum handler)
- ✅ `backend/requirements.txt` (includes mangum==0.17.0)
- ✅ `frontend/vite.config.js` (environment support)
- ✅ `.vercelignore` (ignore unnecessary files)

---

## Step 2: Create Vercel Project

### Option A: Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel --prod
```

### Option B: Using Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click **"New Project"**
3. Select your GitHub repository: `ijlalxansari1/Aether-project`
4. Click **"Import"**
5. Continue to next step (environment variables)

---

## Step 3: Configure Environment Variables

In Vercel Dashboard, navigate to **Settings → Environment Variables** and add:

### Required Variables

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@host:5432/aether_db` |
| `SECRET_KEY` | Secure random string (64 chars) | Generate using `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | Comma-separated frontend URLs | `https://your-project.vercel.app` |
| `UPLOAD_DIR` | Temp upload directory | `/tmp/uploads` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `1440` (24 hours) |

### Generate SECRET_KEY Locally

```bash
# PowerShell
python -c "import secrets; print(secrets.token_hex(32))"

# Or in Python shell
import secrets
print(secrets.token_hex(32))
```

Copy the output and use it as `SECRET_KEY`.

### Optional Variables (if using cloud storage)

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=your_bucket
```

---

## Step 4: Set Build & Development Settings

In Vercel Dashboard, navigate to **Settings → Build & Development**:

### Build Settings
- **Framework Preset**: `Other`
- **Build Command**: (leave default - uses `vercel-python.json`)
- **Output Directory**: (leave default)
- **Root Directory**: `/` (or `.`)

### Development Command
- Leave as default

---

## Step 5: Deploy

### Using CLI:
```bash
vercel --prod
```

### Using Dashboard:
If you set auto-deploy enabled (recommended):
- Push changes to `main` branch
- Vercel automatically builds and deploys

---

## Step 6: Verify Deployment

Once deployment completes, test your application:

### Test Backend API
```bash
# Health check
curl https://your-project.vercel.app/api/health

# API docs (Swagger UI)
https://your-project.vercel.app/docs

# ReDoc documentation
https://your-project.vercel.app/redoc
```

### Test Frontend
```
https://your-project.vercel.app/
```

Expected behavior:
1. Frontend loads (Home page visible)
2. Login/Register works
3. API calls succeed (no 500 errors)
4. Data uploads complete

---

## Step 7: Connect Database (PostgreSQL)

### Option A: Using Vercel Postgres (Recommended)

1. In Vercel Dashboard → **Storage** tab
2. Click **"Create"** → **"Postgres"**
3. Connect to your project
4. Copy `POSTGRES_URL` from `.env.local`
5. Add to Vercel Environment Variables as `DATABASE_URL`

### Option B: External PostgreSQL Provider

Use providers like:
- **Supabase** (https://supabase.com)
- **Railway** (https://railway.app)
- **Heroku Postgres** (https://heroku.com)
- **AWS RDS**

Get the connection string in format:
```
postgresql://user:password@host:port/database
```

---

## Step 8: Monitor Deployment

In Vercel Dashboard:

1. **Deployments Tab**: View build logs and history
2. **Functions Tab**: Monitor serverless function usage
3. **Logs**: Real-time error monitoring
4. **Analytics**: Track performance

---

## Troubleshooting

### Issue: "Build failed - ModuleNotFoundError"

**Solution**: Check that `backend/requirements.txt` includes all dependencies:
```bash
pip install -r backend/requirements.txt
```

### Issue: "CORS Error in Frontend"

**Solution**: Update `CORS_ORIGINS` in Vercel environment variables:
```
https://your-project.vercel.app
```

### Issue: "Database Connection Failed"

**Solution**: Verify `DATABASE_URL` format and connectivity:
```bash
psql <DATABASE_URL>
```

### Issue: "Upload Directory Permission Denied"

**Solution**: Use `/tmp` directory (already set in code):
```python
UPLOAD_DIR = "/tmp/uploads"
```

### Issue: "Frontend doesn't load - 404 errors"

**Solution**: Ensure `vercel-python.json` routes are correctly configured:
```json
{
  "src": "/(.*)",
  "dest": "frontend/dist/$1",
  "status": 200
}
```

### Issue: "Timeout on API calls"

**Solution**: 
- Check backend logs: Vercel Dashboard → Logs
- Verify database connectivity
- Increase function timeout if needed (max 60s on free tier)

---

## Performance Optimization

### Frontend Optimizations
1. Enable caching headers in `vercel.json`
2. Use Image Optimization with Vercel
3. Enable Incremental Static Regeneration (ISR)

### Backend Optimizations
1. Use connection pooling for database
2. Cache API responses where possible
3. Optimize database queries

### Example `vercel.json` with caching:
```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-cache" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=86400" }
      ]
    }
  ]
}
```

---

## Custom Domain (Optional)

1. Purchase domain (e.g., Namecheap, GoDaddy)
2. In Vercel Dashboard → **Domains**
3. Add your custom domain
4. Update DNS records (instructions provided by Vercel)

---

## Rollback & Versioning

### Rollback to Previous Deployment
1. Vercel Dashboard → **Deployments**
2. Click on previous deployment
3. Click **"Promote to Production"**

### Version Control
Keep track of deployment versions:
```bash
git tag v1.0.0-deployed
git push origin v1.0.0-deployed
```

---

## Maintenance & Monitoring

### Regular Tasks
- [ ] Monitor API error logs weekly
- [ ] Check database usage and optimize queries
- [ ] Review function execution time
- [ ] Update dependencies monthly
- [ ] Backup database weekly

### Useful Commands
```bash
# View deployment logs
vercel logs --prod

# Check environment variables
vercel env ls

# Pull environment variables locally
vercel env pull

# Redeploy current version
vercel --prod
```

---

## Cost Estimation

**Vercel Free Tier Includes:**
- 100 GB bandwidth per month
- Unlimited serverless function invocations
- Unlimited static site deployments
- 12 Function Executions per month (free tier limit)

**Paid Plans Start At:**
- **Pro**: $20/month
- **Enterprise**: Custom pricing

---

## Next Steps

1. ✅ Commit changes to GitHub
2. ✅ Deploy to Vercel
3. ✅ Configure database
4. ✅ Add custom domain (optional)
5. ✅ Set up monitoring alerts
6. ✅ Create CI/CD pipeline for auto-deployment

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Mangum (ASGI adapter)**: https://mangum.io
- **Project Repo**: https://github.com/ijlalxansari1/Aether-project

---

**Last Updated**: November 13, 2025
**Status**: Ready for Production Deployment
