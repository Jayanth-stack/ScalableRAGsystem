#!/bin/bash

# Cost-effective deployment script for VPS (DigitalOcean, Linode, etc.)
# Total cost: $10-20/month for a 2GB RAM VPS

set -e

echo "🚀 Starting deployment..."

# Configuration
VPS_IP="${1:-your-vps-ip}"
SSH_KEY="${2:-~/.ssh/id_rsa}"
DOMAIN="${3:-your-domain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if VPS IP is provided
if [ "$VPS_IP" == "your-vps-ip" ]; then
    print_error "Please provide VPS IP as first argument"
    echo "Usage: ./deploy.sh <vps-ip> [ssh-key-path] [domain]"
    exit 1
fi

# Step 1: Prepare local build
print_status "Building frontend for production..."
cd ../frontend
npm run build
npm run export  # Creates static export in 'out' directory
cd ../deployment

# Step 2: Create deployment package
print_status "Creating deployment package..."
tar -czf deploy-package.tar.gz \
    ../code_assistant \
    ../frontend/out \
    ../requirements.txt \
    ../api_server.py \
    ../sample_repos \
    docker-compose.prod.yml \
    Dockerfile.api \
    nginx.conf \
    setup-vps.sh

# Step 3: Copy to VPS
print_status "Copying files to VPS..."
scp -i "$SSH_KEY" deploy-package.tar.gz root@$VPS_IP:/tmp/

# Step 4: Setup VPS
print_status "Setting up VPS..."
ssh -i "$SSH_KEY" root@$VPS_IP << 'ENDSSH'
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi

    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi

    # Create app directory
    mkdir -p /opt/code-assistant
    cd /opt/code-assistant

    # Extract deployment package
    tar -xzf /tmp/deploy-package.tar.gz
    rm /tmp/deploy-package.tar.gz

    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        cat > .env << EOF
GOOGLE_API_KEY=your-google-api-key
DB_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
EOF
        echo "⚠️  Please update .env with your actual API keys!"
    fi

    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

    # Start services
    echo "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d

    # Wait for services to be healthy
    echo "Waiting for services to start..."
    sleep 10

    # Check status
    docker-compose -f docker-compose.prod.yml ps
ENDSSH

# Step 5: Setup SSL (optional but recommended)
if [ "$DOMAIN" != "your-domain.com" ]; then
    print_status "Setting up SSL for $DOMAIN..."
    ssh -i "$SSH_KEY" root@$VPS_IP << ENDSSH
        # Install certbot
        apt-get update
        apt-get install -y certbot

        # Get SSL certificate
        certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

        # Update nginx config to use SSL
        # This would require updating nginx.conf with SSL configuration
        echo "SSL certificate obtained. Update nginx.conf to enable HTTPS."
ENDSSH
fi

# Step 6: Verify deployment
print_status "Verifying deployment..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://$VPS_IP/health)

if [ "$HEALTH_CHECK" == "200" ]; then
    print_status "Deployment successful! 🎉"
    echo ""
    echo "Access your application at:"
    echo "  http://$VPS_IP"
    if [ "$DOMAIN" != "your-domain.com" ]; then
        echo "  https://$DOMAIN (after DNS propagation)"
    fi
    echo ""
    echo "Next steps:"
    echo "1. SSH into your VPS: ssh root@$VPS_IP"
    echo "2. Update .env file: nano /opt/code-assistant/.env"
    echo "3. Restart services: cd /opt/code-assistant && docker-compose -f docker-compose.prod.yml restart"
else
    print_error "Health check failed. Please check the logs:"
    echo "ssh root@$VPS_IP 'cd /opt/code-assistant && docker-compose -f docker-compose.prod.yml logs'"
fi

# Cleanup
rm -f deploy-package.tar.gz

print_status "Deployment script completed!"