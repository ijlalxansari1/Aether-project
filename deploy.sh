#!/bin/bash
# Deployment helper script for AETHER Insight Platform

set -e

echo "🚀 AETHER Insight Platform - Deployment Helper"
echo "=============================================="
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "📝 Creating .env from .env.example..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created backend/.env - Please update with your values!"
    else
        echo "❌ backend/.env.example not found. Please create backend/.env manually."
        exit 1
    fi
fi

echo ""
echo "Select deployment target:"
echo "1) Railway (Backend)"
echo "2) Vercel (Frontend)"
echo "3) Both"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "📦 Deploying backend to Railway..."
        cd backend
        if command -v railway &> /dev/null; then
            railway up
        else
            echo "❌ Railway CLI not found. Install with: npm i -g @railway/cli"
            exit 1
        fi
        ;;
    2)
        echo ""
        echo "📦 Deploying frontend to Vercel..."
        if command -v vercel &> /dev/null; then
            vercel --prod
        else
            echo "❌ Vercel CLI not found. Install with: npm i -g vercel"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "📦 Deploying backend to Railway..."
        cd backend
        if command -v railway &> /dev/null; then
            railway up
        else
            echo "❌ Railway CLI not found. Install with: npm i -g @railway/cli"
            exit 1
        fi
        cd ..
        echo ""
        echo "📦 Deploying frontend to Vercel..."
        if command -v vercel &> /dev/null; then
            vercel --prod
        else
            echo "❌ Vercel CLI not found. Install with: npm i -g vercel"
            exit 1
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update CORS_ORIGINS in backend with your Vercel frontend URL"
echo "2. Set VITE_API_URL in Vercel with your Railway backend URL"
echo "3. Configure cloud storage (Vercel Blob or AWS S3) if needed"
echo "4. Set up PostgreSQL database if not already done"

