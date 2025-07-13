# 🚀 SQL Analyzer Enterprise - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ System Requirements
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for dependencies

### ✅ Quick Deployment (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Andrewgo12/sql-analyzer-enterprise.git
cd sql-analyzer-enterprise

# 2. Run automated setup
python setup.py

# 3. Start the application
cd web_app
python server.py
```

### ✅ Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create required directories
mkdir -p temp uploads output
mkdir -p conclusions_arc/{reports,analytics,exports}

# 3. Configure environment (optional)
cp .env.example .env
# Edit .env with your settings

# 4. Start the server
cd web_app
python server.py
```

## 🌐 Access the Application

- **URL**: http://localhost:8081
- **Default Login**: 
  - Username: `admin`
  - Password: `admin123`

## 🔧 Configuration Options

### Environment Variables (.env)
```bash
DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///sql_analyzer.db
UPLOAD_MAX_SIZE=10737418240
ALLOWED_EXTENSIONS=.sql,.txt,.pdf,.csv,.json
```

### Server Configuration (config/base.yaml)
```yaml
server:
  host: "127.0.0.1"
  port: 8081
  debug: true

database:
  url: "sqlite:///sql_analyzer.db"

security:
  session_timeout: 3600
  max_login_attempts: 5
```

## 🐳 Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8081

CMD ["python", "web_app/server.py"]
```

```bash
# Build and run
docker build -t sql-analyzer-enterprise .
docker run -p 8081:8081 sql-analyzer-enterprise
```

## ☁️ Cloud Deployment

### AWS EC2
```bash
# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip -y

# Deploy application
git clone https://github.com/Andrewgo12/sql-analyzer-enterprise.git
cd sql-analyzer-enterprise
python3 setup.py

# Configure security group: Allow port 8081
# Start application
cd web_app
python3 server.py
```

### Google Cloud Platform
```bash
# Use Cloud Shell or Compute Engine
gcloud compute instances create sql-analyzer \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --tags=http-server

# SSH and deploy
gcloud compute ssh sql-analyzer
# Follow manual deployment steps
```

### Azure
```bash
# Create VM
az vm create \
  --resource-group myResourceGroup \
  --name sql-analyzer-vm \
  --image UbuntuLTS \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH and deploy
az vm open-port --port 8081 --resource-group myResourceGroup --name sql-analyzer-vm
# Follow manual deployment steps
```

## 🔒 Production Security

### 1. Change Default Credentials
```python
# In web_app/server.py, update authentication
# Or use environment variables
ADMIN_USERNAME=your_admin_user
ADMIN_PASSWORD=your_secure_password
```

### 2. Configure HTTPS
```python
# Use reverse proxy (nginx/apache) or
# Configure SSL in uvicorn
uvicorn server:app --host 0.0.0.0 --port 8081 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### 3. Database Security
```yaml
# Use production database
database:
  url: "postgresql://user:password@localhost/sql_analyzer"
  # or
  url: "mysql://user:password@localhost/sql_analyzer"
```

## 📊 Performance Optimization

### 1. Production Server
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8081
```

### 2. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Database Optimization
```python
# Use connection pooling
# Configure database indexes
# Enable query caching
```

## 🔍 Monitoring and Logging

### 1. Application Logs
```bash
# Logs are written to console and files
tail -f logs/application.log
```

### 2. Health Checks
```bash
# Health endpoint
curl http://localhost:8081/health

# API status
curl http://localhost:8081/api/status
```

### 3. Performance Monitoring
```python
# Built-in metrics available at
# http://localhost:8081/metrics
```

## 🛠️ Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 8081
lsof -i :8081
# Kill process
kill -9 <PID>
```

**2. Permission Errors**
```bash
# Fix file permissions
chmod +x setup.py
chmod -R 755 web_app/
```

**3. Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**4. Database Connection**
```bash
# Check database file permissions
ls -la sql_analyzer.db
# Reset database
rm sql_analyzer.db
python setup.py
```

## 📞 Support

- **Documentation**: Check README.md
- **Issues**: GitHub Issues
- **Email**: support@sqlanalyzer.com

## 🔄 Updates

```bash
# Update application
git pull origin main
pip install -r requirements.txt --upgrade
python setup.py
```

---

**Deployment completed successfully!** 🎉

Your SQL Analyzer Enterprise is now ready for production use.
