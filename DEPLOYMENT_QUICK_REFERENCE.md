# 📚 Deployment Documentation - Quick Reference Card

## 🎯 Deployment Overview

```
AETHER INSIGHT PLATFORM
     Frontend (React)           Backend (FastAPI)
           ↓                            ↓
    ┌──────────────┐          ┌──────────────┐
    │ Vite + React │          │ FastAPI      │
    │ Material-UI  │          │ + Mangum     │
    └──────────────┘          └──────────────┘
           ↓                            ↓
         BUILD                        BUILD
           ↓                            ↓
    ┌──────────────────────────────────────┐
    │      VERCEL (Single Project)         │
    │                                      │
    │  / → frontend/dist (CDN)            │
    │  /api → api/index.py (Serverless)   │
    │  /docs → OpenAPI docs                │
    └──────────────────────────────────────┘
           ↓
    PostgreSQL Database
    (External: Vercel/Railway/AWS)
```

---

## 📋 Deployment Checklist (TL;DR)

- [ ] Commit code: `git add . && git commit && git push`
- [ ] Install CLI: `npm install -g vercel && vercel login`
- [ ] Setup env: Run `.\setup-vercel-env.ps1` or `bash setup-vercel-env.sh`
- [ ] Deploy: `vercel --prod`
- [ ] Test: Visit `https://your-project.vercel.app`

---

## 📖 Documentation Files

| File | Read Time | Purpose | When to Use |
|------|-----------|---------|------------|
| **QUICK_START_DEPLOYMENT.md** | 5 min | Step-by-step guide | Want to deploy NOW |
| **VERCEL_DEPLOYMENT.md** | 30 min | Complete reference | Need all details |
| **DEPLOYMENT_CHECKLIST.md** | 15 min | Verification steps | Before/after deploy |
| **DEPLOYMENT_README.md** | 10 min | Overview & setup | First time? Start here |
| **DEPLOYMENT_CHANGES.md** | 10 min | What changed | Want to understand changes |
| **This file** | 2 min | Quick reference | Need quick answers |

---

## ✅ Files Changed

### Modified (3 files)
```
✏️ backend/requirements.txt      → Added: mangum==0.17.0
✏️ api/index.py                  → Uncommented Vercel handler
✏️ vercel-python.json            → Updated deployment config
```

### Created (8 files)
```
📄 QUICK_START_DEPLOYMENT.md
📄 VERCEL_DEPLOYMENT.md
📄 DEPLOYMENT_CHECKLIST.md
📄 DEPLOYMENT_README.md
📄 DEPLOYMENT_CHANGES.md
📄 setup-vercel-env.sh
📄 setup-vercel-env.ps1
📄 .env.example
```

---

## 🚀 5-Minute Deployment

```bash
# 1. Commit (1 min)
cd aether-project
git add .
git commit -m "chore: prepare for Vercel deployment"
git push

# 2. Install Vercel CLI (1 min)
npm install -g vercel
vercel login

# 3. Set Environment Variables (1 min)
# Windows: .\setup-vercel-env.ps1
# Mac/Linux: bash setup-vercel-env.sh

# 4. Deploy (1 min)
vercel --prod

# 5. Test (1 min)
# Visit: https://your-project.vercel.app
```

---

## 🔐 Required Environment Variables

```bash
# Generate SECRET_KEY first:
python -c "import secrets; print(secrets.token_hex(32))"

# Then add these to Vercel:
SECRET_KEY=<your-generated-key>
DATABASE_URL=postgresql://user:pass@host:port/db
CORS_ORIGINS=https://your-project.vercel.app
UPLOAD_DIR=/tmp/uploads
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🎮 Common Commands

```bash
# Deployment
vercel --prod                    # Deploy to production
vercel --prod --confirm         # Deploy without prompt

# Debugging
vercel logs --prod              # View live logs
vercel logs --prod --follow     # Stream logs in real-time
vercel env ls                   # List env variables
vercel env pull                 # Pull env to .env file

# Management
vercel list                      # List all deployments
vercel rollback                 # Rollback to previous
vercel analytics                # View function usage
vercel env add KEY value --prod # Add env variable
```

---

## ✨ Architecture

```
┌─────────────────────────────────────────────┐
│            Vercel Edge Network              │
├─────────────────────────────────────────────┤
│                                             │
│  Static (CDN)          Serverless Function  │
│  ──────────────        ─────────────────    │
│  React Build           FastAPI + Mangum     │
│  HTML/CSS/JS          Python Code           │
│  Lightning Fast        Auto-Scaling         │
│  Cached                Pay-Per-Use          │
│                                             │
└─────────────────────────────────────────────┘
         ↓
    PostgreSQL
    (External)
```

---

## 🧪 Testing After Deploy

```bash
# Test backend API
curl https://your-project.vercel.app/api/health
# Should return: {"status": "healthy", "service": "aether-insight-platform"}

# Test frontend
open https://your-project.vercel.app
# Should load home page

# Test API docs
open https://your-project.vercel.app/docs
# Should show Swagger UI
```

---

## 🛠️ Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| **Build fails** | Check: `vercel logs --prod` |
| **CORS error** | Update `CORS_ORIGINS` env var |
| **DB won't connect** | Verify `DATABASE_URL` format |
| **502 error** | Check backend logs, likely exception |
| **Static files 404** | Ensure `frontend/dist` exists |
| **Timeout** | API taking > 60s (free tier limit) |

---

## 💰 Cost Breakdown

```
✓ Frontend builds      → FREE (unlimited)
✓ 100k API calls      → FREE (per month)
✓ 100 GB bandwidth    → FREE (per month)
✓ Deployments         → FREE (unlimited)
✓ Custom domain       → $10-15/year
✓ PostgreSQL DB       → $15-50/month

= Essentially FREE tier possible! ✨
```

---

## 📱 Success Indicators

After deployment, check:

```
✅ https://your-project.vercel.app            → Loads frontend
✅ https://your-project.vercel.app/api/health → Returns 200
✅ https://your-project.vercel.app/docs       → Shows API docs
✅ Login page works                           → Can register/login
✅ Data upload works                          → Can upload CSV
✅ No console errors                          → Clean browser console
✅ Vercel dashboard shows "Ready"             → Deployment complete
```

---

## 🔄 Continuous Deployment

After first deployment:

1. **Enable auto-deploy**: Vercel Dashboard → Settings → Git
2. **Push changes**: `git push origin main`
3. **Auto-deploys**: Vercel automatically rebuilds and deploys

---

## 🆘 Need Help?

| Topic | Resource |
|-------|----------|
| **Vercel Questions** | https://vercel.com/docs |
| **FastAPI Help** | https://fastapi.tiangolo.com |
| **Deployment Issues** | See `DEPLOYMENT_CHECKLIST.md` |
| **Comprehensive Guide** | Read `VERCEL_DEPLOYMENT.md` |

---

## 📊 Post-Deployment Monitoring

### Weekly Checks
- [ ] Check error rate in Vercel logs
- [ ] Monitor function execution time
- [ ] Verify database connections stable

### Monthly Tasks
- [ ] Review bandwidth usage
- [ ] Check function invocation quota
- [ ] Update dependencies if needed
- [ ] Backup database

---

## 🎯 Next Steps Priority

1. **Immediate** (Now)
   - Read: `QUICK_START_DEPLOYMENT.md`
   - Do: `vercel --prod`

2. **Short-term** (Today)
   - Verify deployment works
   - Test all major features

3. **Follow-up** (This week)
   - Set up monitoring alerts
   - Configure custom domain
   - Set up backups

---

## 📌 File Locations

```
Your Project Root
├── DEPLOYMENT_README.md        ← Start here
├── QUICK_START_DEPLOYMENT.md   ← Then here
├── VERCEL_DEPLOYMENT.md        ← Deep dive
├── DEPLOYMENT_CHECKLIST.md     ← During deploy
├── setup-vercel-env.ps1        ← Windows users
├── setup-vercel-env.sh         ← Mac/Linux users
├── vercel-python.json          ← Deployment config
└── api/index.py                ← Serverless handler
```

---

## 🚀 TL;DR Quick Deploy

```powershell
# Windows PowerShell
cd aether-project
git add . ; git commit -m "deploy" ; git push
npm install -g vercel
vercel login
.\setup-vercel-env.ps1
vercel --prod
# Visit: https://your-project.vercel.app ✨
```

---

## 🎉 You're Ready!

**Status**: ✅ All configurations complete  
**Time to Deploy**: ~5 minutes  
**Complexity**: LOW (just run commands)  

**Start with**: `QUICK_START_DEPLOYMENT.md` → Run `vercel --prod` → Done!

---

**Questions?** See the comprehensive guides linked above.  
**Ready?** Let's deploy! 🚀
