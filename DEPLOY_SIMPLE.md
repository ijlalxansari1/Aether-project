# AETHER Insight Platform — Simple Deploy Checklist

This file gives minimal, copy-paste steps to run the project locally and deploy backend to Railway and frontend to Vercel.

## 1 — Local (Windows PowerShell)

Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# create .env from .env.example and edit secrets locally
copy .env.example .env
# replace SECRET_KEY with a secure value
python - <<'PY'
import secrets
print(secrets.token_hex(32))
PY

# optional: initialize DB tables
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# run backend (defaults to 8000)
$env:PORT = "8000"
python .\start.py
```

Frontend
```powershell
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

## 2 — Docker (local)

```powershell
docker-compose up --build
# Backend: http://localhost:8000, Frontend: http://localhost:3000
```

## 3 — Deploy Backend to Railway (minimal)

1. Push your repo to GitHub (ensure `backend/runtime.txt`, `backend/Procfile`, `backend/start.py` are committed).
2. Create a Railway project and connect the GitHub repo.
3. Add a PostgreSQL plugin; copy `DATABASE_URL` into Railway environment variables.
4. Add the following Railway environment variables:
   - SECRET_KEY (generate locally; do NOT use the example value)
   - CORS_ORIGINS (comma-separated frontend URL(s))
   - UPLOAD_DIR (e.g. `/tmp/uploads`)
   - ACCESS_TOKEN_EXPIRE_MINUTES (e.g. `1440`)
5. Deploy and check logs. Test: `GET https://<railway-url>/api/health` and `https://<railway-url>/docs`.

Notes:
- Railway provides `PORT` automatically; `backend/start.py` reads it.
- Use Postgres in production (Railway plugin) instead of SQLite.

## 4 — Deploy Frontend to Vercel (minimal)

1. Import the `frontend` folder into Vercel (or the repo and set root to `frontend`).
2. Set environment variable `VITE_API_URL` to your backend (Railway) URL.
3. Deploy. Confirm the app loads and API calls succeed.

## 5 — Essential env vars (backend)

Required:
- DATABASE_URL (e.g. `postgres://user:pass@host:port/dbname`)
- SECRET_KEY (secure random hex)
- CORS_ORIGINS (comma-separated)
- UPLOAD_DIR
- ACCESS_TOKEN_EXPIRE_MINUTES

Optional (cloud storage): S3/Blob credentials if you use remote uploads.

## 6 — Quick troubleshooting

- If Vercel shows a build error referencing `@api_url` or missing secret, create the Vercel secret or set `VITE_API_URL` as a literal value in the Vercel dashboard.
- If Railway fails to start with a port error, confirm `backend/Procfile` contains `web: python start.py` and `backend/start.py` exists.
- For DB migration in production, use Alembic instead of `Base.metadata.create_all`.

---

If you want, I can: commit this file, run `pytest` in `backend/`, or remove the local artifacts we identified earlier. Tell me which next step you want.
