# ⚡ Quick Start: Deploy to Vercel in 5 Minutes

## Step 1: Commit All Changes (2 min)

```bash
# Navigate to project root
cd c:\Users\poono\Desktop\Data Analysis Project\Aether-project

# Verify changes
git status

# Stage and commit
git add .
git commit -m "chore: prepare for Vercel full-stack deployment"
git push origin main
```

## Step 2: Install Vercel CLI (1 min)

```bash
npm install -g vercel
vercel login
```

## Step 3: Create Environment Variables (1 min)

### Option A: Interactive Setup (Recommended)

**On Windows PowerShell:**
```powershell
.\setup-vercel-env.ps1
```

**On Mac/Linux:**
```bash
bash setup-vercel-env.sh
```

### Option B: Manual Setup

1. Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

2. In Vercel Dashboard:
   - Go to Settings → Environment Variables
   - Add these 5 variables:
     - `SECRET_KEY` = your_generated_key
     - `DATABASE_URL` = postgresql://...
     - `CORS_ORIGINS` = https://your-project.vercel.app
     - `UPLOAD_DIR` = /tmp/uploads
     - `ACCESS_TOKEN_EXPIRE_MINUTES` = 1440

## Step 4: Deploy (Automatic)

```bash
# From project root
vercel --prod
```

The deployment will:
1. ✅ Build frontend (React + Vite)
2. ✅ Build backend (FastAPI + Mangum)
3. ✅ Deploy both to Vercel
4. ✅ Provide you with a live URL

## Step 5: Verify Deployment (1 min)

```bash
# Test backend API
curl https://your-project.vercel.app/api/health

# View live app
https://your-project.vercel.app
```

---

## What Was Changed?

### 1. **Backend Configuration**
- ✅ Added `mangum==0.17.0` to requirements.txt
- ✅ Updated `api/index.py` with Mangum handler
- ✅ Ready for serverless deployment

### 2. **Vercel Configuration**
- ✅ Updated `vercel-python.json` with:
  - Frontend static build
  - Backend serverless function
  - Proper routing rules
  - All environment variables

### 3. **Frontend Configuration**
- ✅ `vite.config.js` supports `VITE_API_URL` env var
- ✅ API client uses environment variable
- ✅ Works with any backend URL

### 4. **Documentation**
- ✅ `VERCEL_DEPLOYMENT.md` - Complete guide (20+ pages)
- ✅ `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- ✅ `setup-vercel-env.sh` - Auto setup script (bash)
- ✅ `setup-vercel-env.ps1` - Auto setup script (PowerShell)
- ✅ `.env.example` - Environment template

---

## Architecture Deployed

```
Internet Users
        ↓
   Vercel Edge (CDN)
        ↓
┌───────────────────────────────────┐
│   https://your-project.vercel.app │
├───────────────────────────────────┤
│ Frontend (React Build)            │  ← Static files served from CDN
│ /                                 │
├───────────────────────────────────┤
│ Backend (FastAPI via Mangum)      │  ← Serverless functions
│ /api/*                            │
└───────────────────────────────────┘
        ↓
   PostgreSQL Database
   (External provider)
```

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Build fails | Check Vercel logs: `vercel logs --prod` |
| CORS errors | Update `CORS_ORIGINS` env var |
| Database won't connect | Verify `DATABASE_URL` format |
| Uploads fail | Check `UPLOAD_DIR` is `/tmp/uploads` |
| 502 errors | Check backend logs for exceptions |

---

## Next Steps After Deployment

1. **Monitor**: Check Vercel Dashboard regularly
2. **Optimize**: Enable caching and compression
3. **Custom Domain**: Add your own domain (optional)
4. **CI/CD**: Auto-deploy on every push to main
5. **Backup**: Set up database backups
6. **Analytics**: Enable Vercel Analytics

---

## Useful Commands

```bash
# View current deployment URL
vercel list

# See live logs
vercel logs --prod --follow

# Redeploy current version
vercel --prod

# View environment variables
vercel env ls

# Pull env vars to local .env
vercel env pull

# Check function usage
vercel analytics
```

---

## Success Indicators ✅

After deployment, verify:

- [ ] `https://your-project.vercel.app` loads
- [ ] `https://your-project.vercel.app/docs` shows API docs
- [ ] `https://your-project.vercel.app/api/health` returns `{"status": "healthy"}`
- [ ] Can login/register
- [ ] Can upload data file
- [ ] No errors in browser console
- [ ] No 502 or 500 errors

---

## Estimated Costs

- **Frontend**: Free (included in free tier)
- **Backend API**: Free (100k function invocations/month)
- **Database**: ~$15-50/month (external provider)
- **Total**: Essentially free tier possible!

---

## Questions?

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **GitHub**: https://github.com/ijlalxansari1/Aether-project

---

**Ready to deploy? Run:** `vercel --prod` 🚀
