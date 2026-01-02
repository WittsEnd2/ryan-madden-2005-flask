# Deployment Guide

This guide covers different deployment scenarios for the NFL Football Game application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [VPS/Cloud Server Deployment](#vpscloud-server-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Platform-Specific Guides](#platform-specific-guides)
6. [Security Best Practices](#security-best-practices)
7. [Performance Tuning](#performance-tuning)

## Prerequisites

- Python 3.12 or higher
- Git
- 512MB RAM minimum (1GB+ recommended for production)
- Linux/macOS/Windows with WSL

## Local Development

### Quick Start

```bash
# Run the setup script
./scripts/setup.sh

# Start development server
./scripts/dev.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Generate secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
# Add to .env file: SECRET_KEY=<generated-key>

# Run development server
python app.py
```

## VPS/Cloud Server Deployment

### 1. Server Setup (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx

# Create application user
sudo useradd -m -s /bin/bash nflgame
sudo su - nflgame

# Clone repository
git clone <repository-url> app
cd app
```

### 2. Application Setup

```bash
# Run setup script
./scripts/setup.sh

# Configure environment
nano .env
# Set:
# FLASK_ENV=production
# SECRET_KEY=<secure-key>
# WORKERS=4
# PORT=5000
```

### 3. Create Systemd Service

Create `/etc/systemd/system/nflgame.service`:

```ini
[Unit]
Description=NFL Game Application
After=network.target

[Service]
User=nflgame
Group=nflgame
WorkingDirectory=/home/nflgame/app
Environment="PATH=/home/nflgame/app/venv/bin"
EnvironmentFile=/home/nflgame/app/.env
ExecStart=/home/nflgame/app/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Configure Nginx

Create `/etc/nginx/sites-available/nflgame`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/nflgame/app/static;
        expires 30d;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/nflgame /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Start the Application

```bash
sudo systemctl enable nflgame
sudo systemctl start nflgame
sudo systemctl status nflgame
```

### 6. Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t nfl-game:latest .

# Run container
docker run -d \
  --name nfl-game \
  -p 5000:5000 \
  -e SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))') \
  --restart unless-stopped \
  nfl-game:latest
```

### Using Docker Compose

```bash
# Set environment variables
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker with Nginx Reverse Proxy

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## Platform-Specific Guides

### Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Deploy:
```bash
railway login
railway init
railway up
```

3. Set environment variables in Railway dashboard:
- `SECRET_KEY`: Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `FLASK_ENV`: production

### Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: nfl-game
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --config gunicorn.conf.py wsgi:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
```

2. Connect repository to Render dashboard

### Heroku

1. Create `Procfile`:
```
web: gunicorn --config gunicorn.conf.py wsgi:app
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
git push heroku main
```

### DigitalOcean App Platform

1. Use the Docker deployment option
2. Set environment variables in the dashboard
3. Configure health check: `/`

## Security Best Practices

### 1. Environment Variables

Never commit `.env` file. Always use:
- Secure random SECRET_KEY (32+ bytes)
- Environment-specific configurations
- Secrets management service in cloud deployments

### 2. HTTPS

Always use HTTPS in production:
- Let's Encrypt for free SSL certificates
- Cloud provider SSL termination
- Reverse proxy SSL configuration

### 3. Firewall

Configure firewall rules:
```bash
# UFW example
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 4. Updates

Keep system and dependencies updated:
```bash
# System updates
sudo apt update && sudo apt upgrade

# Python dependencies
pip install --upgrade -r requirements.txt
```

### 5. Monitoring

Set up monitoring:
- Application logs
- Error tracking (Sentry, etc.)
- Uptime monitoring
- Resource usage

## Performance Tuning

### Gunicorn Workers

Calculate optimal workers:
```
workers = (2 * CPU_cores) + 1
```

Adjust in `.env`:
```
WORKERS=5  # For 2 CPU cores
THREADS=2
```

### Nginx Caching

Add to nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache app_cache;
    proxy_cache_valid 200 5m;
    # ... other proxy settings
}
```

### Database Session Store (Optional)

For scaling beyond single server, consider using:
- Redis for session storage
- PostgreSQL for game state persistence

## Monitoring and Logs

### View Logs

```bash
# Systemd service
sudo journalctl -u nflgame -f

# Docker
docker logs -f nfl-game

# Docker Compose
docker-compose logs -f
```

### Health Checks

Test application health:
```bash
curl http://localhost:5000/
```

### Resource Monitoring

```bash
# System resources
htop

# Docker resources
docker stats
```

## Backup and Recovery

### Application Backup

```bash
# Backup application directory
tar -czf nflgame-backup-$(date +%Y%m%d).tar.gz /home/nflgame/app

# Backup environment file
cp /home/nflgame/app/.env /home/nflgame/backups/.env.backup
```

### Restore

```bash
# Extract backup
tar -xzf nflgame-backup-YYYYMMDD.tar.gz

# Restore environment
cp /home/nflgame/backups/.env.backup /home/nflgame/app/.env

# Restart service
sudo systemctl restart nflgame
```

## Troubleshooting

### Application won't start

1. Check logs: `journalctl -u nflgame -n 50`
2. Verify SECRET_KEY is set
3. Check file permissions
4. Verify Python environment

### 502 Bad Gateway

1. Check if Gunicorn is running: `systemctl status nflgame`
2. Verify port configuration matches nginx config
3. Check firewall rules

### High Memory Usage

1. Reduce number of workers
2. Check for memory leaks in application logs
3. Monitor with `top` or `htop`

### Slow Response Times

1. Check worker/thread configuration
2. Enable nginx caching
3. Monitor with application performance tools
4. Check server resources

## Support

For issues and questions:
- Check application logs
- Review this deployment guide
- Check GitHub issues
