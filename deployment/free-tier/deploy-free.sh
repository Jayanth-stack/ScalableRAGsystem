#!/bin/bash

# 🆓 FREE TIER DEPLOYMENT SCRIPT
# Total Cost: $0/month

set -e

echo "🚀 Free Tier Deployment Setup"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}Step $1:${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Choose deployment platform
echo "Choose your FREE backend platform:"
echo "1) Railway.app ($5 credit/month, no credit card)"
echo "2) Render.com (750 hours/month free)"
echo "3) Fly.io (3 VMs free, best option)"
echo "4) Vercel Serverless (backend as functions)"
read -p "Enter choice (1-4): " backend_choice

# Frontend is always on Vercel (unlimited free)
print_step 1 "Setting up Frontend on Vercel (FREE)"
echo "----------------------------------------"

cd ../frontend

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    print_warning "Installing Vercel CLI..."
    npm i -g vercel
fi

# Create production build
print_success "Building frontend..."
npm run build

# Deploy to Vercel
print_success "Deploying to Vercel..."
cp ../deployment/free-tier/vercel.json .
vercel --prod

FRONTEND_URL=$(vercel ls --json | jq -r '.[0].url')
print_success "Frontend deployed to: https://$FRONTEND_URL"

cd ..

# Backend deployment based on choice
case $backend_choice in
    1)
        print_step 2 "Deploying Backend to Railway.app"
        echo "-----------------------------------"
        
        # Install Railway CLI
        if ! command -v railway &> /dev/null; then
            print_warning "Installing Railway CLI..."
            npm i -g @railway/cli
        fi
        
        # Login to Railway
        railway login
        
        # Initialize project
        railway init --name code-assistant-api
        
        # Copy Railway config
        cp deployment/free-tier/railway.toml .
        cp deployment/free-tier/Dockerfile.railway Dockerfile
        
        # Deploy
        railway up
        
        # Get URL
        BACKEND_URL=$(railway status --json | jq -r '.url')
        print_success "Backend deployed to: $BACKEND_URL"
        ;;
        
    2)
        print_step 2 "Deploying Backend to Render.com"
        echo "---------------------------------"
        
        print_warning "Manual steps required:"
        echo "1. Go to https://render.com"
        echo "2. Connect your GitHub repository"
        echo "3. Create new Web Service"
        echo "4. Use blueprint: deployment/free-tier/render.yaml"
        echo "5. Set environment variable: GOOGLE_API_KEY"
        
        read -p "Press enter when complete..."
        BACKEND_URL="your-app.onrender.com"
        ;;
        
    3)
        print_step 2 "Deploying Backend to Fly.io"
        echo "-----------------------------"
        
        # Install Fly CLI
        if ! command -v flyctl &> /dev/null; then
            print_warning "Installing Fly CLI..."
            curl -L https://fly.io/install.sh | sh
        fi
        
        # Login to Fly
        flyctl auth login
        
        # Create app
        flyctl apps create code-assistant --org personal
        
        # Copy Fly config
        cp deployment/free-tier/fly.toml .
        
        # Create Dockerfile for Fly
        cat > Dockerfile.fly << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
COPY deployment/free-tier/requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy app
COPY code_assistant/ ./code_assistant/
COPY sample_repos/ ./sample_repos/

# Create data directory for SQLite
RUN mkdir -p /data

ENV DATABASE_URL="sqlite:////data/app.db"
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "code_assistant.api:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
        
        # Create volume for persistent storage
        flyctl volumes create data --size 1 --region ord
        
        # Set secrets
        read -p "Enter your GOOGLE_API_KEY: " google_key
        flyctl secrets set GOOGLE_API_KEY=$google_key
        
        # Deploy
        flyctl deploy
        
        # Get URL
        BACKEND_URL="code-assistant.fly.dev"
        print_success "Backend deployed to: https://$BACKEND_URL"
        ;;
        
    4)
        print_step 2 "Deploying Backend to Vercel Serverless"
        echo "----------------------------------------"
        
        # Create API directory for Vercel Functions
        mkdir -p api
        
        # Create serverless wrapper
        cat > api/index.py << 'EOF'
from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_assistant.api import app

# Create handler for Vercel
handler = Mangum(app)
EOF
        
        # Create vercel.json for API
        cat > vercel.json << 'EOF'
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9",
      "maxDuration": 10
    }
  },
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api" }
  ]
}
EOF
        
        # Deploy API to Vercel
        vercel --prod
        
        BACKEND_URL=$(vercel ls --json | jq -r '.[0].url')
        print_success "Backend deployed to: https://$BACKEND_URL"
        ;;
esac

# Step 3: Database Setup
print_step 3 "Setting up FREE Database"
echo "-------------------------"

echo "Choose your FREE database:"
echo "1) Supabase (500MB PostgreSQL)"
echo "2) PlanetScale (5GB MySQL)"
echo "3) Neon (3GB PostgreSQL)"
echo "4) MongoDB Atlas (512MB)"
echo "5) SQLite (file-based, included)"
read -p "Enter choice (1-5): " db_choice

case $db_choice in
    1)
        print_success "Setting up Supabase..."
        echo "1. Go to https://supabase.com"
        echo "2. Create new project (free)"
        echo "3. Copy connection string"
        read -p "Enter Supabase connection string: " db_url
        ;;
    2)
        print_success "Setting up PlanetScale..."
        echo "1. Go to https://planetscale.com"
        echo "2. Create database (free tier)"
        echo "3. Copy connection string"
        read -p "Enter PlanetScale connection string: " db_url
        ;;
    3)
        print_success "Setting up Neon..."
        echo "1. Go to https://neon.tech"
        echo "2. Create project (free tier)"
        echo "3. Copy connection string"
        read -p "Enter Neon connection string: " db_url
        ;;
    4)
        print_success "Setting up MongoDB Atlas..."
        echo "1. Go to https://cloud.mongodb.com"
        echo "2. Create M0 cluster (free)"
        echo "3. Copy connection string"
        read -p "Enter MongoDB connection string: " db_url
        ;;
    5)
        print_success "Using SQLite (already configured)"
        db_url="sqlite:///./data/app.db"
        ;;
esac

# Step 4: Update environment variables
print_step 4 "Configuring Environment"
echo "------------------------"

# Update frontend environment
cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=https://$BACKEND_URL
EOF

# Create summary
print_step 5 "Deployment Summary"
echo "==================="
echo ""
print_success "🎉 FREE TIER DEPLOYMENT COMPLETE!"
echo ""
echo "📱 Frontend URL: https://$FRONTEND_URL"
echo "🔧 Backend URL: https://$BACKEND_URL"
echo "💾 Database: $db_url"
echo ""
echo "📊 Monthly Cost: $0.00"
echo ""
echo "⚠️  Free Tier Limits:"
echo "  - Railway: $5 credit/month"
echo "  - Render: 750 hours/month"
echo "  - Fly.io: 3 VMs, 3GB storage"
echo "  - Vercel: 100GB bandwidth/month"
echo ""
echo "📈 When to upgrade:"
echo "  - >10,000 API calls/day"
echo "  - >100 concurrent users"
echo "  - >1GB vector storage needed"
echo ""
print_success "Your app is live and completely FREE! 🚀"