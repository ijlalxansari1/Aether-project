#!/bin/bash
# Vercel Environment Variables Setup Script
# This script helps you quickly set up environment variables for Vercel deployment

echo "=== Aether Insight Platform - Vercel Environment Variables Setup ==="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install it with: npm install -g vercel"
    exit 1
fi

echo "📝 You will be prompted to enter the following values:"
echo ""

# Generate SECRET_KEY if needed
echo "1️⃣ SECRET_KEY (secure random 64-char string)"
echo "   Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
read -p "   Enter SECRET_KEY: " SECRET_KEY

# Database URL
echo ""
echo "2️⃣ DATABASE_URL (PostgreSQL connection string)"
echo "   Format: postgresql://user:password@host:port/database"
read -p "   Enter DATABASE_URL: " DATABASE_URL

# CORS Origins
echo ""
echo "3️⃣ CORS_ORIGINS (comma-separated URLs)"
echo "   Example: https://your-project.vercel.app"
read -p "   Enter CORS_ORIGINS: " CORS_ORIGINS

# Upload directory
echo ""
echo "4️⃣ UPLOAD_DIR (directory for file uploads)"
echo "   Recommended: /tmp/uploads (for Vercel serverless)"
read -p "   Enter UPLOAD_DIR [/tmp/uploads]: " UPLOAD_DIR
UPLOAD_DIR=${UPLOAD_DIR:-/tmp/uploads}

# Token expiry
echo ""
echo "5️⃣ ACCESS_TOKEN_EXPIRE_MINUTES (JWT token expiry in minutes)"
read -p "   Enter ACCESS_TOKEN_EXPIRE_MINUTES [1440]: " ACCESS_TOKEN_EXPIRE_MINUTES
ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-1440}

# Confirm before setting
echo ""
echo "=== Summary ==="
echo "SECRET_KEY: ****${SECRET_KEY: -10}"
echo "DATABASE_URL: ${DATABASE_URL}"
echo "CORS_ORIGINS: ${CORS_ORIGINS}"
echo "UPLOAD_DIR: ${UPLOAD_DIR}"
echo "ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Set Vercel environment variables
    vercel env add SECRET_KEY "$SECRET_KEY" --prod
    vercel env add DATABASE_URL "$DATABASE_URL" --prod
    vercel env add CORS_ORIGINS "$CORS_ORIGINS" --prod
    vercel env add UPLOAD_DIR "$UPLOAD_DIR" --prod
    vercel env add ACCESS_TOKEN_EXPIRE_MINUTES "$ACCESS_TOKEN_EXPIRE_MINUTES" --prod
    
    echo ""
    echo "✅ Environment variables set successfully!"
    echo "🚀 You can now deploy: vercel --prod"
else
    echo "❌ Setup cancelled."
    exit 1
fi
