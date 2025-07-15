# 🚀 SQL Analyzer Enterprise - Production Deployment Guide

## Overview

SQL Analyzer Enterprise is a comprehensive, enterprise-grade SQL analysis platform with real-time monitoring, advanced export capabilities, and professional UI/UX. This guide covers complete production deployment.

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Ubuntu 18.04+, CentOS 7+, macOS 10.15+
- **CPU**: 2 cores, 2.4 GHz
- **RAM**: 4 GB
- **Storage**: 10 GB available space
- **Network**: Stable internet connection

### Recommended Requirements
- **OS**: Ubuntu 20.04 LTS or Windows Server 2019+
- **CPU**: 4+ cores, 3.0+ GHz
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: High-speed internet with SSL certificate

## 🛠️ Pre-Deployment Setup

### 1. Environment Preparation

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip nodejs npm git -y

# CentOS/RHEL
sudo yum update -y
sudo yum install python3 python3-pip nodejs npm git -y

# Windows (using Chocolatey)
choco install python nodejs git -y
```

### 2. Python Dependencies

```bash
# Install required Python packages
pip3 install -r requirements.txt

# Or install individually:
pip3 install flask flask-cors psutil requests sqlparse
```

### 3. Node.js Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

## 🔧 Configuration

### 1. Backend Configuration

Create `config/production.py`:

```python
import os

class ProductionConfig:
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SSL_CONTEXT = 'adhoc'  # Use proper SSL certificates in production
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///production.db')
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # File Upload
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/uploads')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/sql-analyzer/app.log'
    
    # Performance
    WORKERS = int(os.environ.get('WORKERS', 4))
    TIMEOUT = int(os.environ.get('TIMEOUT', 30))
```

### 2. Environment Variables

Create `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=5000
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=postgresql://user:password@localhost/sql_analyzer

# Redis Cache
REDIS_URL=redis://localhost:6379

# File Storage
UPLOAD_FOLDER=/var/uploads

# SSL
SSL_CERT_PATH=/etc/ssl/certs/sql-analyzer.crt
SSL_KEY_PATH=/etc/ssl/private/sql-analyzer.key

# Performance
WORKERS=4
TIMEOUT=30
```

### 3. Frontend Configuration

Update `frontend/src/config/production.js`:

```javascript
export const config = {
  API_BASE_URL: 'https://your-domain.com/api',
  WS_URL: 'wss://your-domain.com/ws',
  MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
  SUPPORTED_FORMATS: ['.sql', '.txt'],
  REFRESH_INTERVAL: 5000,
  CACHE_DURATION: 300000, // 5 minutes
  FEATURES: {
    REAL_TIME_METRICS: true,
    EXPORT_SYSTEM: true,
    TERMINAL: true,
    BATCH_PROCESSING: true
  }
};
```

## 🚀 Deployment Options

### Option 1: Docker Deployment (Recommended)

#### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /var/uploads && chmod 755 /var/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["python", "backend_server.py"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  sql-analyzer:
    build: .
    ports:
      - "5000:5000"
    environment:
      - HOST=0.0.0.0
      - PORT=5000
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
    volumes:
      - uploads:/var/uploads
      - logs:/var/log/sql-analyzer
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=sql_analyzer
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - sql-analyzer
    restart: unless-stopped

volumes:
  uploads:
  logs:
  redis_data:
  postgres_data:
```

#### 3. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f sql-analyzer
```

### Option 2: Traditional Server Deployment

#### 1. Install and Configure Nginx

```nginx
# /etc/nginx/sites-available/sql-analyzer
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/sql-analyzer.crt;
    ssl_certificate_key /etc/ssl/private/sql-analyzer.key;

    # Frontend
    location / {
        root /var/www/sql-analyzer/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 2. Create Systemd Service

```ini
# /etc/systemd/system/sql-analyzer.service
[Unit]
Description=SQL Analyzer Enterprise
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sql-analyzer
Environment=PATH=/var/www/sql-analyzer/venv/bin
ExecStart=/var/www/sql-analyzer/venv/bin/python backend_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/sql-analyzer
sudo chown $USER:$USER /var/www/sql-analyzer

# Clone repository
git clone https://github.com/your-repo/sql-analyzer-enterprise.git /var/www/sql-analyzer

# Set up Python virtual environment
cd /var/www/sql-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build

# Set permissions
sudo chown -R www-data:www-data /var/www/sql-analyzer
sudo chmod -R 755 /var/www/sql-analyzer

# Enable and start service
sudo systemctl enable sql-analyzer
sudo systemctl start sql-analyzer

# Enable and start nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 🔒 Security Configuration

### 1. SSL/TLS Setup

```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Or use custom certificates
sudo mkdir -p /etc/ssl/private
sudo chmod 700 /etc/ssl/private
sudo cp your-certificate.crt /etc/ssl/certs/sql-analyzer.crt
sudo cp your-private-key.key /etc/ssl/private/sql-analyzer.key
sudo chmod 600 /etc/ssl/private/sql-analyzer.key
```

### 2. Firewall Configuration

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. Security Headers

Add to Nginx configuration:

```nginx
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
```

## 📊 Monitoring and Logging

### 1. Application Monitoring

```python
# Add to backend_server.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler('/var/log/sql-analyzer/app.log', 
                                     maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Set up log rotation
sudo tee /etc/logrotate.d/sql-analyzer << EOF
/var/log/sql-analyzer/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload sql-analyzer
    endscript
}
EOF
```

## 🔄 Backup and Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/var/backups/sql-analyzer"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump sql_analyzer > $BACKUP_DIR/database_$DATE.sql

# Application files backup
tar -czf $BACKUP_DIR/app_files_$DATE.tar.gz /var/www/sql-analyzer

# Upload files backup
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/uploads

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 2. Automated Backups

```bash
# Add to crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /var/www/sql-analyzer/backup.sh
```

## 🚀 Performance Optimization

### 1. Application Optimization

```python
# Add to backend configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Enable gzip compression
from flask_compress import Compress
Compress(app)
```

### 2. Database Optimization

```sql
-- PostgreSQL optimizations
CREATE INDEX idx_analysis_timestamp ON analysis_history(timestamp);
CREATE INDEX idx_analysis_user ON analysis_history(user_id);

-- Analyze tables
ANALYZE;
```

### 3. Nginx Optimization

```nginx
# Add to nginx.conf
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Enable caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## ✅ Post-Deployment Checklist

- [ ] SSL certificate installed and working
- [ ] All services running (application, database, cache)
- [ ] Firewall configured properly
- [ ] Monitoring and logging set up
- [ ] Backup system configured
- [ ] Performance optimization applied
- [ ] Security headers configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   # Check logs
   sudo journalctl -u sql-analyzer -f
   
   # Check permissions
   sudo chown -R www-data:www-data /var/www/sql-analyzer
   ```

2. **Database connection issues**
   ```bash
   # Test database connection
   psql -h localhost -U username -d sql_analyzer
   
   # Check database service
   sudo systemctl status postgresql
   ```

3. **High memory usage**
   ```bash
   # Monitor memory
   htop
   
   # Restart application
   sudo systemctl restart sql-analyzer
   ```

## 📞 Support

For production support and enterprise features:
- Email: support@sql-analyzer-enterprise.com
- Documentation: https://docs.sql-analyzer-enterprise.com
- Status Page: https://status.sql-analyzer-enterprise.com

---

**SQL Analyzer Enterprise v2.0.0** - Production Ready ✅
