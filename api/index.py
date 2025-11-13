"""
Vercel Serverless Function Wrapper for FastAPI
This file enables running FastAPI on Vercel using Mangum adapter.

Full-stack deployment on Vercel:
- Frontend: Static build served at /
- Backend: API routes served at /api
"""
from mangum import Mangum
import sys
import os

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import FastAPI app
from app.main import app

# Create Mangum handler for Vercel
# lifespan="off" because Vercel functions are request-scoped
handler = Mangum(app, lifespan="off")

