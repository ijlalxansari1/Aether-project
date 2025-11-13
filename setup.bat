@echo off

echo Setting up AETHER Insight Platform...

REM Backend setup
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please update it with your configuration.
)

REM Initialize database
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
echo Database initialized.

cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend
call npm install
echo Frontend dependencies installed.

cd ..

echo Setup complete!
echo.
echo To start the backend:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo To start the frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Or use Docker:
echo   docker-compose up --build

