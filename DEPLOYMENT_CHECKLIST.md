# 🚀 Aether Insight Platform - Vercel Deployment Checklist

## Pre-Deployment Checklist

- [ ] **Code is committed**: `git status` shows clean working directory
- [ ] **All changes pushed**: `git push origin main`
- [ ] **Dependencies installed**: `npm install` (frontend) & `pip install -r requirements.txt` (backend)
- [ ] **Tests passing**: Run `pytest backend/tests/` 
- [ ] **Environment file created**: `.env` with all required variables

## Environment Variables Checklist

- [ ] **SECRET_KEY**: Generated using `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] **DATABASE_URL**: PostgreSQL connection string verified
- [ ] **CORS_ORIGINS**: Set to `https://your-project.vercel.app`
- [ ] **UPLOAD_DIR**: Set to `/tmp/uploads`
- [ ] **ACCESS_TOKEN_EXPIRE_MINUTES**: Set to `1440` or desired value

## Configuration Files Checklist

- [ ] **vercel-python.json**: Updated with latest configuration
- [ ] **api/index.py**: Contains Mangum handler
- [ ] **backend/requirements.txt**: Includes `mangum==0.17.0`
- [ ] **.vercelignore**: Excludes unnecessary files
- [ ] **frontend/vite.config.js**: Supports environment variables

## Local Testing Checklist

- [ ] **Backend starts**: `python backend/start.py`
- [ ] **Frontend starts**: `npm run dev` (from frontend folder)
- [ ] **API endpoints work**: `curl http://localhost:8000/api/health`
- [ ] **Frontend loads**: `http://localhost:3000`
- [ ] **Login/Auth works**: Can register and login
- [ ] **Data upload works**: Can upload CSV file

## Vercel Setup Checklist

- [ ] **Vercel account created**: https://vercel.com
- [ ] **GitHub repository connected**: Authenticated with Vercel
- [ ] **Project created**: Imported from GitHub
- [ ] **Environment variables added**: All 5 required variables set
- [ ] **Build settings verified**: Framework = `Other`, Root directory = `/`
- [ ] **Deployment attempted**: First deployment started

## Post-Deployment Testing Checklist

- [ ] **Deployment successful**: Vercel shows "✓ Ready" status
- [ ] **Health check passes**: `https://your-project.vercel.app/api/health` returns 200
- [ ] **API docs accessible**: `https://your-project.vercel.app/docs` loads
- [ ] **Frontend loads**: `https://your-project.vercel.app/` displays home page
- [ ] **CORS headers correct**: No CORS errors in browser console
- [ ] **Database connected**: Can login successfully
- [ ] **File upload works**: Can upload data file
- [ ] **API responds**: Data processing, EDA, ML endpoints work

## Monitoring & Maintenance Checklist

- [ ] **Error logs reviewed**: Check Vercel logs for issues
- [ ] **Database performance**: Query times acceptable
- [ ] **Function duration**: API responses < 30 seconds
- [ ] **Bandwidth usage**: Monitor for unusual spikes
- [ ] **Security headers**: CORS, CSP headers configured

## Common Issues & Fixes

### Issue: Build Fails
```bash
# Check logs
vercel logs --prod

# Likely cause: Missing dependency
# Fix: Add to backend/requirements.txt
```

### Issue: CORS Errors in Frontend
```
# Error: Access to XMLHttpRequest blocked by CORS
# Fix: Update CORS_ORIGINS in Vercel env variables
# Set to: https://your-actual-vercel-domain.vercel.app
```

### Issue: Database Connection Fails
```
# Error: psycopg2.OperationalError
# Fix: Verify DATABASE_URL format:
# postgresql://user:password@host:port/database
```

### Issue: Uploads Fail
```
# Error: Permission denied on /uploads
# Fix: Already using /tmp/uploads in code
# Ensure UPLOAD_DIR=/tmp/uploads in env vars
```

### Issue: 502 Bad Gateway
```
# Error: Backend function crashed
# Fix: Check Vercel logs for exceptions
# Common cause: Missing environment variable
```

## Rollback Procedure

If deployment fails in production:

1. Go to Vercel Dashboard → Deployments
2. Find previous successful deployment
3. Click the deployment
4. Click "Promote to Production"
5. Verify application is restored

## Performance Optimization Checklist (Optional)

- [ ] **Frontend**: Enable gzip compression
- [ ] **Frontend**: Minify CSS/JS
- [ ] **Backend**: Add database query caching
- [ ] **Backend**: Enable connection pooling
- [ ] **Images**: Optimize and compress
- [ ] **CDN**: Enable Vercel's Edge Network

## Security Checklist

- [ ] **Secrets are private**: No hardcoded API keys in code
- [ ] **Environment variables**: Set in Vercel, not in .env file
- [ ] **HTTPS enabled**: All traffic encrypted
- [ ] **CORS configured**: Only allow trusted origins
- [ ] **Authentication**: JWT tokens working correctly
- [ ] **Database**: Using strong password

## Deployment Commands Quick Reference

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# View logs
vercel logs --prod

# Check environment variables
vercel env ls

# Pull environment variables locally
vercel env pull

# List all deployments
vercel list

# Rollback to previous version
vercel rollback
```

## Support Resources

- **Vercel Documentation**: https://vercel.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Mangum Documentation**: https://mangum.io
- **Project Repository**: https://github.com/ijlalxansari1/Aether-project

---

## Deployment Status

- **Frontend Deployment**: ✅ Ready
- **Backend Deployment**: ✅ Ready
- **Database Setup**: ⏳ Pending (requires external setup)
- **Environment Variables**: ⏳ Pending (requires user input)
- **Full Deployment**: ⏳ Ready to start

---

**Last Updated**: November 13, 2025
**Status**: All configurations prepared - Ready for deployment!
