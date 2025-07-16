# 🛠️ Guía de Instalación - SQL Analyzer Enterprise

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Python**: 3.8 o superior
- **RAM**: 4GB mínimo
- **Espacio en Disco**: 500MB
- **Sistema Operativo**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### Requisitos Recomendados
- **Python**: 3.9 o superior
- **RAM**: 8GB o más
- **Espacio en Disco**: 2GB
- **CPU**: 4 cores o más

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/sql-analyzer-enterprise.git
cd sql-analyzer-enterprise

# 2. Ejecutar script de instalación
# Windows:
install.bat

# macOS/Linux:
chmod +x install.sh
./install.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/sql-analyzer-enterprise.git
cd sql-analyzer-enterprise

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Actualizar pip
python -m pip install --upgrade pip

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Verificar instalación
python web_app.py --test
```

## 🔧 Configuración Inicial

### 1. Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Configuración de la aplicación
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Configuración de archivos
MAX_CONTENT_LENGTH=104857600  # 100MB
UPLOAD_FOLDER=uploads

# Configuración de seguridad
SECURITY_SCAN_ENABLED=True
MALWARE_SCAN_ENABLED=False

# Configuración de base de datos (opcional)
DATABASE_URL=sqlite:///analyzer.db
```

### 2. Configuración de Directorios

```bash
# Crear directorios necesarios
mkdir uploads
mkdir logs
mkdir exports
mkdir cache

# Configurar permisos (Linux/macOS)
chmod 755 uploads logs exports cache
```

### 3. Configuración de Logging

Crear archivo `logging.conf`:

```ini
[loggers]
keys=root,analyzer

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_analyzer]
level=DEBUG
handlers=fileHandler
qualname=analyzer
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('logs/analyzer.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🧪 Verificación de Instalación

### 1. Test Básico

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Ejecutar tests
python -m pytest tests/ -v

# Test de funcionalidad básica
python test_installation.py
```

### 2. Test de Rendimiento

```bash
# Test de análisis de archivos
curl -X POST -F "file=@test_sample.sql" http://localhost:5000/api/analyze

# Test de health check
curl http://localhost:5000/api/health
```

### 3. Test de Interfaz

```bash
# Iniciar servidor
python web_app.py

# Abrir en navegador
# http://localhost:5000
```

## 🐳 Instalación con Docker

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p uploads logs exports cache

# Configurar permisos
RUN chmod 755 uploads logs exports cache

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando de inicio
CMD ["python", "web_app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  sql-analyzer:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./exports:/app/exports
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### Comandos Docker

```bash
# Construir imagen
docker build -t sql-analyzer-enterprise .

# Ejecutar contenedor
docker run -p 5000:5000 sql-analyzer-enterprise

# Con Docker Compose
docker-compose up -d
```

## 🌐 Deployment en Producción

### Heroku

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login a Heroku
heroku login

# Crear aplicación
heroku create sql-analyzer-enterprise

# Configurar variables de entorno
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-production-secret-key

# Deploy
git push heroku main

# Abrir aplicación
heroku open
```

### AWS EC2

```bash
# 1. Crear instancia EC2 (Ubuntu 20.04)
# 2. Conectar via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 4. Instalar Python y dependencias
sudo apt install python3 python3-pip python3-venv nginx -y

# 5. Clonar repositorio
git clone https://github.com/tu-usuario/sql-analyzer-enterprise.git
cd sql-analyzer-enterprise

# 6. Configurar aplicación
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. Configurar Nginx
sudo nano /etc/nginx/sites-available/sql-analyzer

# 8. Configurar systemd service
sudo nano /etc/systemd/system/sql-analyzer.service

# 9. Iniciar servicios
sudo systemctl enable sql-analyzer
sudo systemctl start sql-analyzer
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### Error: "ModuleNotFoundError"
```bash
# Verificar entorno virtual activado
which python
# Debe mostrar: /path/to/venv/bin/python

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### Error: "Permission denied"
```bash
# Linux/macOS
chmod +x web_app.py
sudo chown -R $USER:$USER uploads logs

# Windows (ejecutar como administrador)
icacls uploads /grant Users:F
```

#### Error: "Port already in use"
```bash
# Encontrar proceso usando puerto 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:5000 | xargs kill -9
```

#### Error: "File too large"
```bash
# Aumentar límite en web_app.py
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
```

### Logs y Debugging

```bash
# Ver logs de la aplicación
tail -f logs/analyzer.log

# Modo debug
export FLASK_DEBUG=1
python web_app.py

# Verificar configuración
python -c "from web_app import app; print(app.config)"
```

### Performance Tuning

```python
# Configuración optimizada para producción
app.config.update(
    TESTING=False,
    DEBUG=False,
    SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 año
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100MB
    UPLOAD_FOLDER='uploads',
    SECRET_KEY=os.environ.get('SECRET_KEY'),
)
```

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. **Revisa los logs**: `logs/analyzer.log`
2. **Verifica dependencias**: `pip list`
3. **Consulta Issues**: [GitHub Issues](https://github.com/tu-usuario/sql-analyzer-enterprise/issues)
4. **Contacto**: soporte@sql-analyzer-enterprise.com

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Directorios creados
- [ ] Variables de entorno configuradas
- [ ] Tests ejecutados exitosamente
- [ ] Servidor iniciado en http://localhost:5000
- [ ] Interfaz web accesible
- [ ] API endpoints funcionando

**¡Instalación completada exitosamente!** 🎉
