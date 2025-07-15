# SQL Analyzer Enterprise

Enterprise-grade SQL analysis platform with support for 22+ database engines and 38+ export formats.

## Features

- **22+ Database Engines**: MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch, and more
- **38+ Export Formats**: JSON, HTML, PDF, Excel, Word, and specialized formats
- **Real-time Analysis**: Fast SQL parsing and validation
- **Enterprise Interface**: Professional full-screen design
- **Metrics Dashboard**: System monitoring and analytics
- **Security**: Built-in vulnerability detection

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python backend_server.py
   ```

3. **Access the application**:
   - Open http://localhost:5000 in your browser

## Deployment

### Railway
```bash
railway up
```

### Docker
```bash
docker build -t sql-analyzer-enterprise .
docker run -p 5000:5000 sql-analyzer-enterprise
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/databases/supported` - Get supported database engines
- `GET /api/export/formats` - Get supported export formats
- `POST /api/analyze` - Analyze SQL file
- `POST /api/export/<format>` - Export analysis results
- `GET /api/metrics/dashboard` - Get system metrics

## License

MIT License - see LICENSE file for details.
