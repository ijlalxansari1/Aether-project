# 🎯 Aether Project Structure & Vercel Deployment Clarification

**Important**: Backend and Frontend are in the SAME root directory - This is CORRECT! ✅

---

## 📁 Project Structure (Correct)

```
Aether-project/                          ← Root directory
│
├── frontend/                            ← React App
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json                     ← npm scripts
│   ├── vite.config.js                   ← Vite config
│   └── dist/                            ← Built output (after npm run build)
│
├── backend/                             ← FastAPI App
│   ├── app/
│   │   ├── main.py                      ← FastAPI entry point
│   │   ├── routers/                     ← API endpoints
│   │   ├── modules/                     ← Business logic
│   │   └── database.py
│   ├── tests/
│   ├── uploads/                         ← Uploaded files
│   ├── requirements.txt                 ← Python dependencies
│   ├── start.py                         ← Local dev server
│   ├── Procfile                         ← Railway config
│   └── runtime.txt                      ← Python version
│
├── api/
│   └── index.py                         ← ⭐ VERCEL HANDLER (Critical!)
│
├── vercel-python.json                   ← ⭐ DEPLOYMENT CONFIG (Critical!)
├── vercel.json
├── .vercelignore
└── ... other files ...
```

---

## 🔧 How Vercel Builds This

### Build Process (Vercel does this automatically)

```
Step 1: Read vercel-python.json
        ↓
Step 2: Build Frontend
        ├─ cd frontend
        ├─ npm install
        ├─ npm run build
        └─ Output: frontend/dist/
        
Step 3: Build Backend
        ├─ pip install -r backend/requirements.txt
        ├─ Include api/index.py
        └─ Create serverless function
        
Step 4: Deploy
        ├─ Upload frontend/dist to CDN
        ├─ Upload Python code + handler to edge
        └─ Configure routing
```

---

## 🛣️ Request Routing (After Deployment)

```
User Request
        ↓
   https://your-project.vercel.app/
        ↓
   ┌────────────────────────────────┐
   │   VERCEL ROUTING RULES         │
   ├────────────────────────────────┤
   │                                │
   │  If path = /api/*              │
   │  └─→ Route to: api/index.py    │
   │      └─→ Runs: FastAPI backend │
   │          └─→ Accesses: backend/app/main.py
   │                                │
   │  If path = /docs or /openapi.json
   │  └─→ Route to: api/index.py    │
   │      └─→ Runs: FastAPI backend │
   │                                │
   │  If path = / or /anything-else │
   │  └─→ Route to: frontend/dist   │
   │      └─→ Serves: React app     │
   │                                │
   └────────────────────────────────┘
```

---

## ⚙️ Key Configuration File: vercel-python.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "pythonVersion": "3.11"
      }
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/docs", "dest": "api/index.py" },
    { "src": "/openapi.json", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1", "status": 200 }
  ]
}
```

**Explanation:**
- `builds`: What to build (frontend + backend)
- `routes`: Where to send each request

---

## 🔗 Key Handler File: api/index.py

```python
from mangum import Mangum
import sys
import os

# ⭐ CRITICAL: Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import FastAPI app from backend/app/main.py
from app.main import app

# Create ASGI handler for Vercel
handler = Mangum(app, lifespan="off")
```

**Why this works:**
1. `sys.path.insert(0, backend_path)` adds `backend/` to Python's search path
2. `from app.main import app` can now find `backend/app/main.py`
3. `Mangum` converts ASGI (FastAPI) to WSGI (Vercel compatible)

---

## ✅ Verification

### Local Structure Check
```bash
# From project root, verify these exist:
ls frontend/package.json          # ✅ Should exist
ls backend/requirements.txt        # ✅ Should exist
ls api/index.py                    # ✅ Should exist
ls vercel-python.json              # ✅ Should exist
```

### Build Configuration Check
```
vercel-python.json structure:
├─ builds[0]: frontend/package.json → @vercel/static-build
├─ builds[1]: api/index.py → @vercel/python
└─ routes: Proper routing for /api/* and static files
```

**Status**: ✅ All correct!

---

## 🚀 What Happens When You Deploy

### Timeline

```
0min:  You push to GitHub
       └─ Vercel auto-detects changes

1min:  Vercel reads vercel-python.json
       └─ Understands what to build

2min:  Build starts
       ├─ Frontend build begins (npm install + npm run build)
       └─ Backend dependencies prepared (pip install)

5min:  Builds complete
       ├─ frontend/dist/ ready
       └─ Python code packaged

6min:  Deploy starts
       ├─ Static files → CDN
       └─ Python function → Vercel Edge

10min: ✅ LIVE!
       ├─ Frontend: https://your-project.vercel.app/
       └─ Backend: https://your-project.vercel.app/api/
```

---

## 🔍 Troubleshooting: Same Directory

### Common Concern: "Won't they conflict?"
**Answer**: NO! They're in separate folders:
- Frontend at: `frontend/` (npm builds to `frontend/dist/`)
- Backend at: `backend/` (Python at `backend/app/`)
- Handler at: `api/index.py` (connects them)

### Common Issue: Build fails with "cannot find module"
**Check**: Is `api/index.py` adding backend to path?
```python
# Should have this:
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)
```

### Common Issue: Frontend and Backend can't communicate
**Fix**: Update `CORS_ORIGINS` environment variable:
```
CORS_ORIGINS=https://your-project.vercel.app
```
This allows frontend to call backend API

---

## 📊 Deployment Architecture

```
                    https://your-project.vercel.app
                              ↓
                ┌─────────────────────────────┐
                │    VERCEL DEPLOYMENT        │
                ├─────────────────────────────┤
                │                             │
                │  Path: /                    │
                │  Serves: frontend/dist      │
                │  Content: React app         │
                │  Location: CDN (global)     │
                │  Speed: Ultra-fast (cached) │
                │                             │
                │  Path: /api/*               │
                │  Serves: api/index.py       │
                │  Content: FastAPI backend   │
                │  Location: Edge (global)    │
                │  Scaling: Auto (per request)│
                │                             │
                └─────────────────────────────┘
                           ↓
                    PostgreSQL DB
                    (External setup)
```

---

## ✨ Environment Variables

All pointing to the same deployed instance:

```
DATABASE_URL=postgresql://...        ← Database connection
SECRET_KEY=<64-char-hex>             ← JWT signing
CORS_ORIGINS=https://your-project... ← Frontend talks to backend
UPLOAD_DIR=/tmp/uploads              ← File upload location
```

---

## 🎯 Next Steps

1. **Add 5 environment variables** in Vercel dashboard
2. **Wait for deployment** (usually 5-10 minutes)
3. **Test**:
   - Frontend loads: `https://your-project.vercel.app/`
   - API works: `https://your-project.vercel.app/api/health`
   - Backend accessible from frontend

---

## 📚 Files to Reference

- `vercel-python.json` - Deployment configuration ✅
- `api/index.py` - Serverless handler ✅
- `backend/requirements.txt` - Python dependencies ✅
- `frontend/vite.config.js` - Frontend build config ✅

---

## ✅ You're All Set!

**Your structure is PERFECT for Vercel:**
- ✅ Frontend in frontend/
- ✅ Backend in backend/
- ✅ Handler at api/index.py
- ✅ Config at vercel-python.json

**Just add environment variables and deploy!** 🚀

---

**Status**: Configuration is CORRECT for same-directory structure  
**Next**: Go to `ACTION_ITEMS.md` for final deployment steps
