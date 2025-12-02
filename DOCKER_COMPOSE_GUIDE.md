# Docker Compose Quick Start Guide

## Prerequisites
- Docker installed and running
- Docker Compose v2.0+
- OpenAI API key

## Services Included

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Main database |
| pgvector | - | Vector search (embedded in PostgreSQL) |
| n8n | 5678 | Workflow automation |
| WAHA | 3000 | WhatsApp API |
| Redis | 6379 | Caching/sessions (optional) |
| Adminer | 8080 | Database admin UI (optional) |

## Quick Start

### 1. Configure Environment
```bash
# Copy the .env template
cp .env.docker .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 2. Start All Services
```bash
# Start all services in background
docker-compose up -d

# Or foreground (useful for debugging)
docker-compose up

# Or specific services only
docker-compose up postgres n8n waha
```

### 3. Verify Services
```bash
# Check all containers
docker-compose ps

# Check logs
docker-compose logs -f postgres
docker-compose logs -f n8n
docker-compose logs -f waha
```

### 4. Access Services

#### PostgreSQL (5432)
```bash
# Connect with psql
psql -h localhost -U smartops -d smartops_core

# Or use Adminer
# Open http://localhost:8080
# Server: postgres
# User: smartops
# Password: smartops_dev_password
# Database: smartops_core
```

#### n8n (5678)
```bash
# Open http://localhost:5678
# User: admin
# Password: smartops_n8n_password
```

#### WAHA (3000)
```bash
# Open http://localhost:3000
# WhatsApp API dashboard
# Scan QR to connect WhatsApp
```

#### Redis (6379)
```bash
# Connect
redis-cli -h localhost -p 6379
redis-cli ping  # Should return PONG
```

## Common Commands

### Stop Services
```bash
# Stop all services (keep volumes)
docker-compose stop

# Stop and remove containers (keep volumes)
docker-compose down

# Remove everything including volumes (CAUTION!)
docker-compose down -v
```

### View Logs
```bash
# Real-time logs
docker-compose logs -f

# Specific service
docker-compose logs -f postgres

# Last 50 lines
docker-compose logs --tail=50
```

### Rebuild Services
```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build postgres

# Rebuild without cache
docker-compose build --no-cache
```

### Database Management

#### Initialize Database with Sample Data
```bash
# Connect to postgres container
docker-compose exec postgres psql -U smartops -d smartops_core

# List tables
\dt

# Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

#### Backup Database
```bash
docker-compose exec postgres pg_dump -U smartops -d smartops_core > backup.sql
```

#### Restore Database
```bash
docker-compose exec -T postgres psql -U smartops -d smartops_core < backup.sql
```

## Troubleshooting

### PostgreSQL Connection Failed
```bash
# Check if container is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### n8n Not Starting
```bash
# Check n8n logs
docker-compose logs -f n8n

# Restart n8n
docker-compose restart n8n

# Reset n8n (deletes all workflows!)
docker-compose exec n8n rm -rf /home/node/.n8n/databases/*
docker-compose restart n8n
```

### WAHA Connection Issues
```bash
# Check WAHA logs
docker-compose logs -f waha

# Restart WAHA
docker-compose restart waha

# Check volumes
docker volume ls | grep waha
```

### Port Already in Use
```bash
# Find what's using port 5432
lsof -i :5432

# Or use netstat (Windows: netstat -ano | findstr :5432)

# Kill process (Linux/Mac)
kill -9 <PID>

# Change port in docker-compose.yml
# postgres:
#   ports:
#     - "5433:5432"  # Change 5432 to 5433
```

## Production Considerations

### Security
- Change default passwords in `.env`
- Use secrets management (Docker Secrets)
- Enable authentication for n8n
- Use reverse proxy (Nginx) for external access

### Performance
- Increase PostgreSQL memory: `shared_buffers = 256MB`
- Add more Redis replicas
- Use connection pooling for n8n

### Backup
- Regular database backups
- Volume snapshots
- Off-site backup storage

### Monitoring
- Enable Docker logging driver
- Use Prometheus for metrics
- Set up alerts

## Network Access

### From Host Machine
- FastAPI: http://localhost:8001
- n8n: http://localhost:5678
- WAHA: http://localhost:3000
- Adminer: http://localhost:8080
- PostgreSQL: localhost:5432

### From Container to Host
- Use `host.docker.internal` (Docker Desktop)
- Or use container network IP

### Container to Container
- Services can communicate using service names
- Example: `postgres:5432` (instead of localhost:5432)

## Environment Variables

All services read from `.env` file. Key variables:

```
DB_USER=smartops
DB_PASSWORD=smartops_dev_password
DB_NAME=smartops_core
OPENAI_API_KEY=sk-...
N8N_USER=admin
N8N_PASSWORD=smartops_n8n_password
```

See `.env.docker` for complete list.

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [n8n Documentation](https://docs.n8n.io/)
- [WAHA Documentation](https://docs.waha.dev/)
