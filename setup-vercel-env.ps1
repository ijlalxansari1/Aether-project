# Vercel Environment Variables Setup Script (PowerShell)
# This script helps you quickly set up environment variables for Vercel deployment

Write-Host "=== Aether Insight Platform - Vercel Environment Variables Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
$vercelCmd = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelCmd) {
    Write-Host "❌ Vercel CLI not found. Install it with: npm install -g vercel" -ForegroundColor Red
    exit 1
}

Write-Host "📝 You will be prompted to enter the following values:" -ForegroundColor Yellow
Write-Host ""

# Generate SECRET_KEY if needed
Write-Host "1️⃣  SECRET_KEY (secure random 64-char string)" -ForegroundColor Cyan
Write-Host "   Generate with: python -c 'import secrets; print(secrets.token_hex(32))'" -ForegroundColor Gray
$SECRET_KEY = Read-Host "   Enter SECRET_KEY"

# Database URL
Write-Host ""
Write-Host "2️⃣  DATABASE_URL (PostgreSQL connection string)" -ForegroundColor Cyan
Write-Host "   Format: postgresql://user:password@host:port/database" -ForegroundColor Gray
$DATABASE_URL = Read-Host "   Enter DATABASE_URL"

# CORS Origins
Write-Host ""
Write-Host "3️⃣  CORS_ORIGINS (comma-separated URLs)" -ForegroundColor Cyan
Write-Host "   Example: https://your-project.vercel.app" -ForegroundColor Gray
$CORS_ORIGINS = Read-Host "   Enter CORS_ORIGINS"

# Upload directory
Write-Host ""
Write-Host "4️⃣  UPLOAD_DIR (directory for file uploads)" -ForegroundColor Cyan
Write-Host "   Recommended: /tmp/uploads (for Vercel serverless)" -ForegroundColor Gray
$UPLOAD_DIR = Read-Host "   Enter UPLOAD_DIR [/tmp/uploads]"
if ([string]::IsNullOrWhiteSpace($UPLOAD_DIR)) {
    $UPLOAD_DIR = "/tmp/uploads"
}

# Token expiry
Write-Host ""
Write-Host "5️⃣  ACCESS_TOKEN_EXPIRE_MINUTES (JWT token expiry in minutes)" -ForegroundColor Cyan
$ACCESS_TOKEN_EXPIRE_MINUTES = Read-Host "   Enter ACCESS_TOKEN_EXPIRE_MINUTES [1440]"
if ([string]::IsNullOrWhiteSpace($ACCESS_TOKEN_EXPIRE_MINUTES)) {
    $ACCESS_TOKEN_EXPIRE_MINUTES = "1440"
}

# Confirm before setting
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Yellow
Write-Host "SECRET_KEY: ****$($SECRET_KEY.Substring([Math]::Max(0, $SECRET_KEY.Length - 10)))" -ForegroundColor White
Write-Host "DATABASE_URL: $DATABASE_URL" -ForegroundColor White
Write-Host "CORS_ORIGINS: $CORS_ORIGINS" -ForegroundColor White
Write-Host "UPLOAD_DIR: $UPLOAD_DIR" -ForegroundColor White
Write-Host "ACCESS_TOKEN_EXPIRE_MINUTES: $ACCESS_TOKEN_EXPIRE_MINUTES" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"

if ($confirm -eq "y" -or $confirm -eq "Y") {
    Write-Host ""
    Write-Host "Setting environment variables..." -ForegroundColor Cyan
    
    & vercel env add SECRET_KEY $SECRET_KEY --prod
    & vercel env add DATABASE_URL $DATABASE_URL --prod
    & vercel env add CORS_ORIGINS $CORS_ORIGINS --prod
    & vercel env add UPLOAD_DIR $UPLOAD_DIR --prod
    & vercel env add ACCESS_TOKEN_EXPIRE_MINUTES $ACCESS_TOKEN_EXPIRE_MINUTES --prod
    
    Write-Host ""
    Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green
    Write-Host "🚀 You can now deploy: vercel --prod" -ForegroundColor Green
} else {
    Write-Host "❌ Setup cancelled." -ForegroundColor Red
    exit 1
}
