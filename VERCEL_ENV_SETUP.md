# ⚙️ Vercel Configuration Setup Guide

**Status**: Code committed and pushed to GitHub ✅  
**Next Step**: Configure Vercel dashboard  
**Time Required**: 5-10 minutes

---

## ✅ What's Been Done

Your code has been **committed and pushed to GitHub**. Vercel has automatically detected the changes and should be building your project now.

**Commit Hash**: `6af31ef`  
**Branch**: `main`  
**Files Changed**: 14 files (11 created, 3 modified)

---

## 🎯 What You Need to Do Now

### Step 1: Go to Vercel Dashboard

Visit: https://vercel.com/dashboard

Click on your project: **Aether-project** (or your project name)

---

### Step 2: Navigate to Environment Variables

**Path**: Settings → Environment Variables

---

### Step 3: Add These 5 Environment Variables

Click **"Add New"** and enter each variable:

#### 1️⃣ **SECRET_KEY** (Required)
- **Key**: `SECRET_KEY`
- **Value**: Generate with:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  - Copy the output (64-character string)
  - Paste into Value field
- **Environments**: Production, Preview, Development

#### 2️⃣ **DATABASE_URL** (Required)
- **Key**: `DATABASE_URL`
- **Value**: Your PostgreSQL connection string
  ```
  postgresql://username:password@host:port/database_name
  ```
  - Example: `postgresql://user:pass@db.vercel.postgres.com:5432/aether`
- **Environments**: Production, Preview, Development

#### 3️⃣ **CORS_ORIGINS** (Required)
- **Key**: `CORS_ORIGINS`
- **Value**: Your Vercel deployment URL
  ```
  https://aether-project.vercel.app
  ```
  - Replace `aether-project` with your actual Vercel project name
- **Environments**: Production, Preview, Development

#### 4️⃣ **UPLOAD_DIR** (Required)
- **Key**: `UPLOAD_DIR`
- **Value**: `/tmp/uploads`
- **Environments**: Production, Preview, Development

#### 5️⃣ **ACCESS_TOKEN_EXPIRE_MINUTES** (Required)
- **Key**: `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Value**: `1440`
  - This means tokens expire after 24 hours
  - Adjust if needed (in minutes)
- **Environments**: Production, Preview, Development

---

## 📋 Environment Variables Checklist

After adding all 5 variables, verify:

- [ ] `SECRET_KEY` - 64 character random string
- [ ] `DATABASE_URL` - PostgreSQL connection (starts with `postgresql://`)
- [ ] `CORS_ORIGINS` - Your Vercel URL
- [ ] `UPLOAD_DIR` - `/tmp/uploads`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - `1440`

---

## 🔧 How to Get SECRET_KEY

### Option 1: Using Python Locally
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (will look like): `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

### Option 2: Online Generator (Not Recommended)
If Python not available, use an online tool to generate a random 64-character hex string (not secure, use Python if possible)

---

## 📊 How to Get DATABASE_URL

### Option 1: Vercel Postgres (Recommended)
1. In Vercel Dashboard → **Storage** tab
2. Click **"Create"** → **"Postgres"**
3. Create new database
4. Copy the `POSTGRES_URL` connection string
5. Use as `DATABASE_URL`

### Option 2: External PostgreSQL Provider

**Railway.app:**
1. Go to https://railway.app
2. Create project and add Postgres plugin
3. Copy connection string from variables

**Supabase:**
1. Go to https://supabase.com
2. Create project
3. Copy PostgreSQL connection string from settings

**AWS RDS:**
1. Create PostgreSQL instance
2. Get endpoint, port, username, password
3. Format: `postgresql://user:pass@endpoint:5432/database`

**Format Guide:**
```
postgresql://username:password@hostname:port/database_name
```

---

## 🔐 How to Get CORS_ORIGINS

After your first Vercel build completes:

1. Go to Vercel Dashboard → Deployments
2. Find the deployment URL (example: `https://aether-project.vercel.app`)
3. Use this as your `CORS_ORIGINS` value

**If URL not available yet:**
- Vercel auto-generates: `https://<project-name>.vercel.app`
- Replace `<project-name>` with your actual project name

---

## 🚀 Vercel Build Verification

### Check Build Status

1. **Dashboard** → **Deployments** tab
2. Look for the latest deployment
3. Check status:
   - ⏳ **Building** - Still in progress
   - ✅ **Ready** - Build successful
   - ❌ **Error** - Build failed (click to see logs)

### View Build Logs

1. Click on the deployment
2. Click **"View Build Logs"**
3. Scroll through to check for errors

---

## ⚠️ Common Issues & Fixes

### Issue: Build Fails with "Module not found"
**Fix**: Check backend/requirements.txt includes `mangum==0.17.0`
- Status: ✅ Already done

### Issue: Build Fails with "Python version"
**Fix**: Ensure `backend/runtime.txt` contains `python-3.11.9`
- Status: ✅ Already configured

### Issue: Environment Variables Not Working
**Fix**: 
- Clear build cache: Vercel Dashboard → Settings → Git → Rebuild
- Redeploy: Click latest deployment → More → Redeploy

### Issue: Database Connection Failed
**Fix**: Verify `DATABASE_URL` format is correct:
```
✅ postgresql://user:password@host:5432/db
❌ postgres://user:password@host:5432/db  (missing 'ql')
❌ postgresql://user:password@host:db     (missing port)
```

### Issue: CORS Errors in Frontend
**Fix**: Update `CORS_ORIGINS` to exact Vercel URL:
```
✅ https://aether-project.vercel.app
❌ https://aether-project.vercel.app/    (trailing slash)
❌ http://aether-project.vercel.app      (http not https)
```

---

## ✅ Testing After Variables Set

Once environment variables are added:

### Test 1: Backend Health Check
```bash
curl https://your-project.vercel.app/api/health
```
**Expected**: `{"status": "healthy", "service": "aether-insight-platform"}`

### Test 2: API Documentation
Visit: `https://your-project.vercel.app/docs`
**Expected**: Swagger UI loads (interactive API docs)

### Test 3: Frontend
Visit: `https://your-project.vercel.app`
**Expected**: Home page loads, no console errors

### Test 4: Login
Try to login/register
**Expected**: Works without 503/502 errors

---

## 🔄 Deployment Process

```
Your Code on GitHub
        ↓
    Vercel Detects
    Push to main
        ↓
    Vercel Builds
    (reads vercel-python.json)
        ↓
    Frontend Build
    (npm run build)
        ↓
    Backend Package
    (pip install -r requirements.txt)
        ↓
    Deploy Functions
    (upload to edge)
        ↓
    ✅ Live at
    https://your-project.vercel.app
```

---

## 📱 What Gets Deployed

### Frontend
- React app compiled to static HTML/CSS/JS
- Served from Vercel's CDN globally
- Path: `/`

### Backend
- Python code wrapped with Mangum
- Runs as serverless functions
- Path: `/api`

### API Routes
- `/api/health` - Health check
- `/api/docs` - Swagger documentation
- `/api/...` - All other endpoints

---

## 🎯 Expected Result

After setting environment variables and deployment completes:

```
✅ https://your-project.vercel.app/                    → Frontend loads
✅ https://your-project.vercel.app/docs                → API docs
✅ https://your-project.vercel.app/api/health          → {"status": "healthy"}
✅ Login/Register works
✅ Data upload works
✅ API calls respond
✅ No 502/503 errors
✅ No CORS errors in console
```

---

## 📞 Next Steps

1. **Add Environment Variables** (5 min)
2. **Wait for Deployment** (2-5 min)
3. **Test Endpoints** (5 min)
4. **Check Logs if Issues** (10 min)

---

## 🆘 If Build Fails

1. **Check logs**: Vercel Dashboard → Deployments → Click failed build → View Build Logs
2. **Common causes**:
   - Missing environment variable
   - Database connection issue
   - Python dependency not installed
   - File path issue

3. **To retry**: Click deployment → More → Redeploy

---

## 📋 Quick Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Code committed | ✅ Done |
| 2 | Code pushed to GitHub | ✅ Done |
| 3 | Vercel detected changes | ⏳ Auto-triggered |
| 4 | Add 5 env variables | ⏳ You do this now |
| 5 | Deployment completes | ⏳ Automatic |
| 6 | Test endpoints | ⏳ After deploy |

---

## 🎉 You're Almost There!

**What remains:**
1. Go to Vercel Dashboard
2. Add 5 environment variables
3. Wait ~5 minutes for deployment
4. Test your live app!

**Time to completion**: ~10 minutes ⏱️

---

**Continue to Step 2: Set Environment Variables in Vercel Dashboard**
