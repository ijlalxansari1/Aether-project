#!/bin/bash

echo "Setting up AETHER Insight Platform..."

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update it with your configuration."
fi

# Initialize database
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
echo "Database initialized."

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
echo "Frontend dependencies installed."

cd ..

echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"

