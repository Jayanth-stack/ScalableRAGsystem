# 💰 Budget-Friendly Deployment Guide

Deploy the Code Documentation Assistant for **$10-20/month** using a simple VPS setup!

## 🎯 Deployment Options Comparison

| Option | Monthly Cost | Complexity | Scalability | Best For |
|--------|-------------|------------|-------------|----------|
| **VPS (Recommended)** | $10-20 | Low | Medium | Most users |
| Vercel + Railway | $20-30 | Very Low | High | Quick start |
| AWS (Minimal) | $15-30 | Medium | High | AWS experience |
| Self-hosted | $0 | High | Low | Home labs |
| Serverless | $5-20 | Medium | Very High | Variable traffic |

## 🚀 Quick Start: VPS Deployment

### Step 1: Get a VPS ($10/month)

Choose one of these providers:
- **DigitalOcean**: $12/month (2GB RAM) - [Get $200 credit](https://try.digitalocean.com/freetrialoffer/)
- **Linode**: $10/month (2GB RAM) - [Get $100 credit](https://www.linode.com/lp/free-credit/)
- **Vultr**: $10/month (2GB RAM) - [Get $100 credit](https://www.vultr.com/promo/)
- **Hetzner**: €4.51/month (~$5) (2GB RAM) - Cheapest option!

### Step 2: Initial VPS Setup

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install essential tools
apt install -y git curl wget nano ufw

# Setup firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# Create swap file (important for 2GB RAM VPS)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Step 3: Deploy Application

```bash
# On your local machine
cd deployment
chmod +x deploy.sh

# Run deployment script
./deploy.sh your-vps-ip

# Or manually:
scp -r ../code_assistant root@your-vps-ip:/opt/
ssh root@your-vps-ip
cd /opt/code-assistant/deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Setup Domain (Optional)

1. Point your domain to VPS IP in DNS settings
2. Install SSL certificate:

```bash
# On VPS
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## 🐳 Docker Compose Setup

The `docker-compose.prod.yml` includes:
- **FastAPI Backend** (API server)
- **PostgreSQL** (Database)
- **Redis** (Cache)
- **Nginx** (Reverse proxy)

All in one command:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 💾 Backup Strategy

```bash
# Create backup script
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
# Backup database
docker exec code-assistant-db pg_dump -U postgres codeassistant > /backup/db-$(date +%Y%m%d).sql

# Backup ChromaDB
tar -czf /backup/chroma-$(date +%Y%m%d).tar.gz /opt/code-assistant/chroma_db

# Upload to S3 or Google Drive (optional)
# rclone copy /backup remote:backups/

# Keep only last 7 days
find /backup -name "*.sql" -mtime +7 -delete
find /backup -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/backup.sh" | crontab -
```

## 🔄 Updates & Maintenance

```bash
# Update application
cd /opt/code-assistant
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check resource usage
docker stats
```

## 📊 Monitoring (Free)

### Option 1: Uptime Kuma (Self-hosted)
```bash
docker run -d \
  --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1
```

### Option 2: Free External Monitoring
- [UptimeRobot](https://uptimerobot.com) - Free for 50 monitors
- [Freshping](https://freshping.io) - Free for 50 monitors

## 🚨 Troubleshooting

### Out of Memory
```bash
# Check memory usage
free -h
docker stats

# Increase swap
fallocate -l 4G /swapfile
mkswap /swapfile
swapon /swapfile

# Reduce container memory
# Edit docker-compose.prod.yml and add memory limits
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL logs
docker logs code-assistant-db

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

## 💡 Cost Optimization Tips

1. **Use Hetzner Cloud** - Cheapest reliable VPS (€4.51/month)
2. **Enable Cloudflare** - Free CDN and DDoS protection
3. **Use SQLite initially** - No separate database container needed
4. **Compress assets** - Reduce bandwidth costs
5. **Set up caching** - Reduce API calls to Google

## 🎓 Free Alternatives

### For Students/Startups:
- **GitHub Student Pack**: Free credits for DigitalOcean, Azure
- **AWS Educate**: $100 credit
- **Google Cloud**: $300 credit for new users
- **Oracle Cloud**: Always free tier (4 CPUs, 24GB RAM!)

### Completely Free Setup:
1. **Frontend**: Vercel/Netlify (free)
2. **Backend**: 
   - Render.com free tier
   - Railway.app free tier ($5 credit/month)
   - Fly.io free tier (3 shared VMs)
3. **Database**: 
   - Supabase (500MB free)
   - PlanetScale (5GB free)
   - Neon (3GB free)

## 📈 Scaling Path

When you need to scale:

1. **$10-20/month**: Single VPS (current setup)
2. **$30-50/month**: Larger VPS + CDN
3. **$50-100/month**: Multiple VPS + Load Balancer
4. **$100+/month**: Managed Kubernetes or AWS ECS

## 🔐 Security Checklist

- [ ] Change default passwords
- [ ] Enable firewall (ufw)
- [ ] Setup SSL certificate
- [ ] Disable root SSH (use sudo user)
- [ ] Enable fail2ban
- [ ] Regular backups
- [ ] Keep Docker images updated
- [ ] Use environment variables for secrets

## 📞 Support

Need help? Check:
1. Docker logs: `docker-compose logs -f`
2. System logs: `journalctl -xe`
3. Resource usage: `htop` or `docker stats`

---

**Total Monthly Cost: $10-20** for a production-ready deployment! 🎉