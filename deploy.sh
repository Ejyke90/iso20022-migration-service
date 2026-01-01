#!/bin/bash

# Deployment Script for Word to PDF Agent
# This script helps deploy both frontend (Vercel) and backend (Railway)

set -e  # Exit on error

echo "🚀 Word to PDF Agent - Deployment Script"
echo "=========================================="
echo ""

# Check if we're in the correct directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to check if Railway is deployed
check_railway() {
    echo "🔍 Checking Railway backend..."
    RAILWAY_URL="https://doc-to-pdf-convertor-production.up.railway.app"
    
    if curl -s "$RAILWAY_URL/api/health" > /dev/null 2>&1; then
        echo "✅ Railway backend is running"
        echo "   URL: $RAILWAY_URL"
        curl -s "$RAILWAY_URL/api/health" | grep -o '"status":"[^"]*"'
        return 0
    else
        echo "⚠️  Railway backend is not responding"
        echo "   Please check Railway dashboard and redeploy if needed"
        return 1
    fi
}

# Function to deploy frontend to Vercel
deploy_vercel() {
    echo ""
    echo "📦 Deploying frontend to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI not found. Installing..."
        npm i -g vercel
    fi
    
    cd web-app
    
    echo "🔨 Building Next.js app..."
    npm install
    
    echo "🚀 Deploying to Vercel..."
    vercel --prod
    
    cd ..
    echo "✅ Frontend deployed to Vercel"
}

# Function to check Vercel environment variables
check_vercel_env() {
    echo ""
    echo "🔍 Checking Vercel environment variables..."
    echo "   Please ensure NEXT_PUBLIC_API_URL is set to:"
    echo "   https://doc-to-pdf-convertor-production.up.railway.app"
    echo ""
    echo "   Visit: https://vercel.com/dashboard → Your Project → Settings → Environment Variables"
}

# Main deployment flow
echo "Step 1: Checking Railway Backend"
echo "---------------------------------"
check_railway
RAILWAY_STATUS=$?

echo ""
echo "Step 2: Frontend Deployment"
echo "---------------------------"
read -p "Deploy frontend to Vercel? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    deploy_vercel
else
    echo "⏭️  Skipping frontend deployment"
fi

echo ""
echo "Step 3: Environment Variables"
echo "-----------------------------"
check_vercel_env

echo ""
echo "📋 Summary"
echo "=========="
if [ $RAILWAY_STATUS -eq 0 ]; then
    echo "✅ Backend: Running on Railway"
else
    echo "⚠️  Backend: Needs attention on Railway"
fi
echo "   Frontend: Check Vercel dashboard"
echo ""
echo "🧪 Testing"
echo "=========="
echo "1. Visit: https://word-to-pdf-agent.vercel.app"
echo "2. Upload a .docx file"
echo "3. Click 'Convert to PDF'"
echo "4. Verify download works"
echo ""
echo "📚 For troubleshooting, see: CORS_FIX_GUIDE.md"
