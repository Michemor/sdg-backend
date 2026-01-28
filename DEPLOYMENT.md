# Deployment Guide

## Pre-Deployment Checklist

### Security
- [ ] `DEBUG = False` in production `.env`
- [ ] Generate new `SECRET_KEY` (use: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- [ ] Update `ALLOWED_HOSTS` with production domain
- [ ] Update `CORS_ALLOWED_ORIGINS` with production frontend URL
- [ ] Use HTTPS URLs in all configurations
- [ ] Set strong database password (not hardcoded)
- [ ] Store `GEMINI_API_KEY` securely (env var, secrets manager)

### Database
- [ ] PostgreSQL 12+ running on production server
- [ ] Database and user created with strong passwords
- [ ] Connection pooling configured (pgBouncer)
- [ ] Regular backups scheduled
- [ ] Test restore procedures

### Infrastructure
- [ ] Python 3.12+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] Gunicorn or uWSGI configured as WSGI server
- [ ] Nginx or Apache as reverse proxy
- [ ] SSL/TLS certificates installed
- [ ] Static files collected: `python manage.py collectstatic`

### Application
- [ ] All migrations applied: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Test API endpoints work
- [ ] Logs configured and rotating
- [ ] Error tracking (Sentry, DataDog) optional but recommended

---

## Production Environment Setup

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and PostgreSQL
sudo apt install python3.12 python3.12-venv postgresql postgresql-contrib -y

# Install system dependencies
sudo apt install build-essential libpq-dev -y
```

### 2. Create Application User

```bash
sudo useradd -m -s /bin/bash sdg_app
sudo su - sdg_app
```

### 3. Set Up Application

```bash
# Clone repository
git clone <repo-url> /home/sdg_app/impactDashboard
cd /home/sdg_app/impactDashboard

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env with production values
cp .env.example .env
nano .env  # Edit with production settings
```

### 4. Configure PostgreSQL

```bash
# As root or with sudo
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE daystar_sdg;
CREATE USER sdg_user WITH PASSWORD 'strong_password_here';
ALTER ROLE sdg_user SET client_encoding TO 'utf8';
ALTER ROLE sdg_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sdg_user SET default_transaction_deferrable TO on;
ALTER ROLE sdg_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE daystar_sdg TO sdg_user;
\q
```

### 5. Initialize Django

```bash
# Still as sdg_app user with activated venv
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Test:
python manage.py check
```

### 6. Configure Gunicorn

Create `/home/sdg_app/impactDashboard/gunicorn_config.py`:

```python
import multiprocessing

# Socket and binding
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 5

# Logging
accesslog = "/home/sdg_app/impactDashboard/logs/access.log"
errorlog = "/home/sdg_app/impactDashboard/logs/error.log"
loglevel = "info"

# Process naming
proc_name = 'sdg_dashboard'

# Server mechanics
daemon = False
pidfile = "/home/sdg_app/impactDashboard/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (optional - handle at Nginx level instead)
keyfile = None
certfile = None

# Server hooks
def post_fork(server, worker):
    pass

def pre_fork(server, worker):
    pass

def pre_exec(server):
    pass

def when_ready(server):
    pass

def worker_int(worker):
    pass

def worker_abort(worker):
    pass
```

Create `/etc/systemd/system/sdg-dashboard.service`:

```ini
[Unit]
Description=SDG Dashboard Gunicorn Service
After=network.target postgresql.service

[Service]
Type=notify
User=sdg_app
Group=sdg_app
WorkingDirectory=/home/sdg_app/impactDashboard
Environment="PATH=/home/sdg_app/impactDashboard/venv/bin"
EnvironmentFile=/home/sdg_app/impactDashboard/.env
ExecStart=/home/sdg_app/impactDashboard/venv/bin/gunicorn \
    --config /home/sdg_app/impactDashboard/gunicorn_config.py \
    daystar_sdg.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sdg-dashboard
sudo systemctl start sdg-dashboard
sudo systemctl status sdg-dashboard
```

### 7. Configure Nginx

Create `/etc/nginx/sites-available/sdg-dashboard`:

```nginx
upstream sdg_app {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/sdg-dashboard.access.log;
    error_log /var/log/nginx/sdg-dashboard.error.log;

    # Client max body size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /home/sdg_app/impactDashboard/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/sdg_app/impactDashboard/media/;
        expires 7d;
    }

    # API and Django
    location / {
        proxy_pass http://sdg_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/sdg-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Set Up SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 9. Configure Logging

```bash
mkdir -p /home/sdg_app/impactDashboard/logs
touch /home/sdg_app/impactDashboard/logs/{access,error}.log
chown sdg_app:sdg_app /home/sdg_app/impactDashboard/logs/
chmod 755 /home/sdg_app/impactDashboard/logs/
```

### 10. Set Up Monitoring & Backups

**Backup Script** (`/home/sdg_app/backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/home/sdg_app/backups"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="daystar_sdg"
DB_USER="sdg_user"

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump $DB_NAME > $BACKUP_DIR/db_$BACKUP_DATE.sql
gzip $BACKUP_DIR/db_$BACKUP_DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$BACKUP_DATE.tar.gz \
    /home/sdg_app/impactDashboard/media/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DATE"
```

Add to crontab:

```bash
# Daily backups at 2 AM
0 2 * * * /home/sdg_app/backup.sh >> /home/sdg_app/backup.log 2>&1
```

---

## Post-Deployment Verification

```bash
# Check application status
sudo systemctl status sdg-dashboard

# Check Nginx
sudo systemctl status nginx

# Test API
curl https://yourdomain.com/api/sdg/

# Check logs
tail -f /home/sdg_app/impactDashboard/logs/error.log
sudo tail -f /var/log/nginx/sdg-dashboard.error.log

# Database connectivity
sudo -u postgres psql -c "\c daystar_sdg" -c "SELECT 1;"
```

---

## Monitoring & Maintenance

### Daily Tasks
- Check application logs for errors
- Monitor disk space
- Verify backups completed

### Weekly Tasks
- Review performance metrics
- Check for security updates
- Test backup restoration

### Monthly Tasks
- Update dependencies: `pip list --outdated`
- Review access logs for anomalies
- Audit user accounts and permissions

### Quarterly Tasks
- Test disaster recovery procedures
- Security audit of infrastructure
- Performance optimization review

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (HAProxy, AWS ELB)
- Run multiple Gunicorn processes
- Use database connection pooling

### Vertical Scaling
- Increase server CPU/RAM
- Optimize database queries
- Implement caching (Redis)

### Performance Optimization
- Enable database query caching
- Implement API response caching
- Use CDN for static/media files
- Optimize image sizes

---

## Troubleshooting

### 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo systemctl status sdg-dashboard

# Check socket
ss -ln | grep 8001

# Check logs
tail -f /home/sdg_app/impactDashboard/logs/error.log
```

### Database Connection Issues
```bash
# Test connection
sudo -u postgres psql -U sdg_user -d daystar_sdg -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check permissions
ls -la /home/sdg_app/impactDashboard/staticfiles/
```

---

## Security Hardening

1. **Firewall**
```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

2. **SSH Security**
   - Disable root login
   - Change SSH port
   - Use SSH keys only

3. **Regular Updates**
```bash
sudo unattended-upgrades
```

4. **Fail2Ban** (optional)
```bash
sudo apt install fail2ban
```

---

**Last Updated:** January 20, 2026
